//-

//+

//////////////////////////////////////////////////////////////////
//
//
/*
loadPlugin "D:/PipeL/install/MayaPlugins/simpleSolverNode/x64/Release/splineSolverNode.mll" ;
joint -p -8 0 0 ;
joint -p -7 0 0 ;
joint -e -zso -oj xyz -sao yup joint1;
joint -p -6 0 0 ;
joint -e -zso -oj xyz -sao yup joint2;
joint -p -5 0 0 ;
joint -e -zso -oj xyz -sao yup joint3;
joint -p -4 0 0 ;
joint -e -zso -oj xyz -sao yup joint4;
joint -p -3 0 0 ;
joint -e -zso -oj xyz -sao yup joint5;
joint -p -2 0 0 ;
joint -e -zso -oj xyz -sao yup joint6;
joint -p -1 0 0 ;
joint -e -zso -oj xyz -sao yup joint7;
joint -p 0 0 0 ;
joint -e -zso -oj xyz -sao yup joint8;
joint -p 1 0 0 ;
joint -e -zso -oj xyz -sao yup joint9;
joint -p 2 0 0 ;
joint -e -zso -oj xyz -sao yup joint10;
int $i;
for ($i = 1; $i < 11; $i++)
{
    setAttr ("joint" + $i + ".displayLocalAxis") 1;
}
select -r joint1.rotatePivot ;
select -add joint11.rotatePivot ;
ikHandle;
curve -d 3 -p -7 0 0 -p -3.666667 0 0 -p -0.333333 0 0 -p 3 0 0 -k 0 -k 0 -k 0 -k 1 -k 1 -k 1 ;
connectAttr -force curveShape1.worldSpace[0] ikHandle1.inCurve;
createNode "splineSolverNode" -name "stretchyik";
select -r ikHandle1 ;
ikHandle -n "ikHandle1" -e -sol "stretchyik";
select -cl;

*/

//////////////////////////////////////////////////////////////////

#include <maya/MIOStream.h>

#include <maya/MPxIkSolverNode.h>
#include <maya/MString.h>
#include <maya/MFnPlugin.h>
#include <maya/MObject.h>
#include <maya/MIkHandleGroup.h>
#include <maya/MFnIkHandle.h>
#include <maya/MDagPath.h>
#include <maya/MVector.h>
#include <maya/MPoint.h>
#include <maya/MDoubleArray.h>
#include <maya/MFnNurbsCurve.h>
#include <maya/MFnNumericAttribute.h>
#include <maya/MFnIkJoint.h>
#include <maya/MQuaternion.h>
#include <vector>
#include <maya/MGlobal.h>
#include <maya/MAngle.h>
#include <maya/MRampAttribute.h>


#define MAX_ITERATIONS 1
#define kSolverType "splineSolverNode"

//////////////////////////////////////////////////////////////////
//
// Class declaration
//
//////////////////////////////////////////////////////////////////
class splineSolverNode : public MPxIkSolverNode {

public:
					splineSolverNode();
    virtual			~splineSolverNode();

	virtual MStatus	doSolve();
	virtual MStatus	postSolve(MStatus 	stat);
	virtual MStatus	preSolve();
	virtual void evaluateDG();
	virtual MString	solverTypeName() const;

	static	void*	creator();
	static  MStatus         initialize();

	static	MTypeId	id;

private:
	MStatus			doSimpleSolver();
	double			getJointsTotalLenght();
	std::vector<MDagPath> joints;
	std::vector<MDagPath> jointsScales;
	MFnNurbsCurve curveFn;
	MFnIkHandle fnHandle;
	MFnTransform tran;

};

MTypeId splineSolverNode::id( 0x80100 );


//////////////////////////////////////////////////////////////////
//
// Implementation
//
//////////////////////////////////////////////////////////////////
splineSolverNode::splineSolverNode()
	: MPxIkSolverNode()
{
	// setMaxIterations( MAX_ITERATIONS );
}

splineSolverNode::~splineSolverNode() {}

void* splineSolverNode::creator()
{
	return new splineSolverNode;
}

MStatus splineSolverNode::initialize()
{ 
	return MS::kSuccess;
}

MString splineSolverNode::solverTypeName() const
//
// This method returns the type name used to identify this solver.
//
{
	return MString( kSolverType );
}

MStatus splineSolverNode::preSolve()
{

	MStatus stat;
	setRotatePlane(false);
	setSingleChainOnly(true);
	setPositionOnly(false);
	//Get Handle
	MIkHandleGroup * handle_group = handleGroup();
	if (NULL == handle_group) {
		return MS::kFailure;
	}
	MObject handle = handle_group->handle( 0 );
	MDagPath handlePath = MDagPath::getAPathTo( handle );
	fnHandle.setObject( handlePath );
	//Get Curve
	MPlug inCurvePlug = fnHandle.findPlug( "inCurve" );
	MDataHandle curveHandle = inCurvePlug.asMDataHandle();
	MObject inputCurveObject = curveHandle.asNurbsCurveTransformed();
	curveFn.setObject( inputCurveObject );
	float initCurveLength = curveFn.length();
	float stretchRatio = 1;
	// Get the position of the end_effector
	//
	MDagPath effectorPath;
	fnHandle.getEffector(effectorPath);
	tran.setObject( effectorPath );
	// Get the start joint position
	//
	MDagPath startJointPath;
	fnHandle.getStartJoint( startJointPath );
	joints.clear();
	//Get Joints
	while (true)
	{
			effectorPath.pop();
			joints.push_back( effectorPath );
			if (effectorPath == startJointPath)
				break;
	}
	std::reverse(joints.begin(), joints.end());
	if (!fnHandle.hasAttribute("str"))
	{
		//Add Custom Attributes to Handle
		MFnNumericAttribute fnAttr;
		MObject attr = fnAttr.create("stretchRatio", "str", MFnNumericData::kDouble, stretchRatio);
		fnAttr.setKeyable(1);
		fnAttr.setWritable(1);
		fnAttr.setMin(0);
		fnAttr.setMax(1);
		fnAttr.setHidden(0);
		fnAttr.setStorable(1);
		fnAttr.setReadable(1);
		fnHandle.addAttribute(attr, MFnDependencyNode::kLocalDynamicAttr);
		attr = fnAttr.create("anchorPosition", "ancp", MFnNumericData::kDouble, 0);
		fnAttr.setKeyable(1);
		fnAttr.setWritable(1);
		fnAttr.setMin(0);
		fnAttr.setMax(1);
		fnAttr.setHidden(0);
		fnAttr.setStorable(1);
		fnAttr.setReadable(1);
		fnHandle.addAttribute(attr, MFnDependencyNode::kLocalDynamicAttr);
		attr = fnAttr.create("curveLength", "cvLen", MFnNumericData::kDouble, initCurveLength);
		fnAttr.setKeyable(0);
		fnAttr.setWritable(1);
		fnAttr.setHidden(1);
		fnAttr.setStorable(1);
		fnAttr.setReadable(1);
		fnHandle.addAttribute(attr, MFnDependencyNode::kLocalDynamicAttr);
		attr = fnAttr.create("jointsLength", "jsLen", MFnNumericData::kDouble, getJointsTotalLenght());
		fnAttr.setKeyable(0);
		fnAttr.setWritable(1);
		fnAttr.setHidden(1);
		fnAttr.setStorable(1);
		fnAttr.setReadable(1);
		fnHandle.addAttribute(attr, MFnDependencyNode::kLocalDynamicAttr);
		attr = fnAttr.create("prevRoll", "preRoll", MFnNumericData::kDouble, 0);
		fnAttr.setKeyable(0);
		fnAttr.setWritable(1);
		fnAttr.setHidden(1);
		fnAttr.setStorable(1);
		fnAttr.setReadable(1);
		fnHandle.addAttribute(attr, MFnDependencyNode::kLocalDynamicAttr);
		attr = fnAttr.create("startTwist", "strtw", MFnNumericData::kDouble, 0);
		fnAttr.setKeyable(1);
		fnAttr.setWritable(1);
		fnAttr.setHidden(0);
		fnAttr.setStorable(1);
		fnAttr.setReadable(1);
		fnHandle.addAttribute(attr, MFnDependencyNode::kLocalDynamicAttr);
		attr = fnAttr.create("endTwist", "endtw", MFnNumericData::kDouble, 0);
		fnAttr.setKeyable(1);
		fnAttr.setWritable(1);
		fnAttr.setHidden(0);
		fnAttr.setStorable(1);
		fnAttr.setReadable(1);
		fnHandle.addAttribute(attr, MFnDependencyNode::kLocalDynamicAttr);
		attr = fnAttr.create("prevStartTwist", "prestrtw", MFnNumericData::kDouble, 0);
		fnAttr.setKeyable(1);
		fnAttr.setWritable(1);
		fnAttr.setHidden(1);
		fnAttr.setStorable(1);
		fnAttr.setReadable(1);
		fnHandle.addAttribute(attr, MFnDependencyNode::kLocalDynamicAttr);
		attr = fnAttr.create("preEndTwist", "preendtw", MFnNumericData::kDouble, 0);
		fnAttr.setKeyable(1);
		fnAttr.setWritable(1);
		fnAttr.setHidden(1);
		fnAttr.setStorable(1);
		fnAttr.setReadable(1);
		fnHandle.addAttribute(attr, MFnDependencyNode::kLocalDynamicAttr);
		MObject twistRamp = MRampAttribute::createCurveRamp("twistRamp", "twr");
		fnHandle.addAttribute(twistRamp, MFnDependencyNode::kLocalDynamicAttr);
	} else
	{
			MPlug strPlug = fnHandle.findPlug("str");
			stretchRatio = strPlug.asDouble();
	}

	return MS::kSuccess;
}

MStatus splineSolverNode::doSolve()
//
// This is the core solver.
//
{
	doSimpleSolver();
	return MS::kSuccess;
}

MStatus splineSolverNode::postSolve(MStatus 	stat)
{
	evaluateDG();
	//MGlobal::displayInfo( "en postSolve ");
	doSimpleSolver();
	return MS::kSuccess;
}

double splineSolverNode::getJointsTotalLenght()
{
	double totalLength = 0;
	MPoint pBaseJoint, pEndJoint;
	for (int i = 0; i < joints.size(); i++)
	{
		MFnIkJoint j( joints[i]);
		pBaseJoint = j.rotatePivot(MSpace::kWorld);
		if( i == joints.size() - 1)
			//Effector Position
			pEndJoint = tran.rotatePivot(MSpace::kWorld);
		else
		{
			//get position of next joint
			MFnIkJoint j2( joints[i + 1]);
			pEndJoint = j2.rotatePivot(MSpace::kWorld);
		}
		MVector vBaseJoint(pBaseJoint[0]-pEndJoint[0], pBaseJoint[1]-pEndJoint[1], pBaseJoint[2]-pEndJoint[2]);
		totalLength += vBaseJoint.length();
	}
	return totalLength;
}

MStatus splineSolverNode::doSimpleSolver()
//
// Solve single joint in the x-y plane
//
// - first it calculates the angle between the handle and the end-effector.
// - then it determines which way to rotate the joint.
//
{
	//Do Real Solve
	//
	MStatus stat;
	float curCurveLength = curveFn.length();
	MPlug crvLengPlug = fnHandle.findPlug("cvLen");
	double initCurveLength = crvLengPlug.asDouble();
	//Twist
	MPlug twistRamp = fnHandle.findPlug("twistRamp");
	MRampAttribute curveAttribute( twistRamp, &stat );
	MPlug startTwistPlug = fnHandle.findPlug("strtw");
	double startTwist = startTwistPlug.asDouble();
	MPlug endTwistPlug = fnHandle.findPlug("endtw");
	double endTwist = endTwistPlug.asDouble();
	MPlug prestartTwistPlug = fnHandle.findPlug("prestrtw");
	double preStartTwist = prestartTwistPlug.asDouble();
	MPlug preendTwistPlug = fnHandle.findPlug("preendtw");
	double preEndTwist = preendTwistPlug.asDouble();
	//float twistValue;
	// curveAttribute.getValueAtPosition(rampPosition, twistValue, &stat);
	// startTwist + twistValue *( endTwist - startTwist );
	//Roll
	MPlug rollPlug = fnHandle.findPlug("roll");
	double roll = rollPlug.asDouble();
	MPlug preRollPlug = fnHandle.findPlug("preRoll");
	double preRoll = preRollPlug.asDouble();

	MPlug strPlug = fnHandle.findPlug("str");
	float stretchRatio = strPlug.asDouble();
	float normCrvLength = curCurveLength / initCurveLength;
	double scale[3] = {1 +stretchRatio*(normCrvLength -1), 1, 1};
	//Get Anchor Position
	MPlug ancPosPlug = fnHandle.findPlug("ancp");
	double anchorPos = ancPosPlug.asDouble();
	MPlug jointsTotLengthPlug = fnHandle.findPlug("jsLen");
	double jointsTotalLength = jointsTotLengthPlug.asDouble();
	double difLengthCurveJoints = curCurveLength - (jointsTotalLength * scale[0]);
	float startLength = 0.0 + anchorPos*( difLengthCurveJoints );
	float parm = curveFn.findParamFromLength( startLength );
	MPoint pBaseJoint, pEndJoint;
	curveFn.getPointAtParam( parm, pBaseJoint );
	MFnIkJoint j( joints[0] );
	j.setTranslation( MVector( pBaseJoint ), MSpace::kWorld );
	float jointRotPercent = 1.0/joints.size();
	float currJointRot = 0;
	float prevTwist = 0;
	float v0 = startTwist - preStartTwist;
	float v1 = endTwist - preEndTwist;
	prestartTwistPlug.setDouble( startTwist );
	preendTwistPlug.setDouble( endTwist );
	//j.setScale(scale);
	for (int i = 0; i < joints.size(); i++)
	{
		MFnIkJoint j( joints[i]);
		pBaseJoint = j.rotatePivot(MSpace::kWorld);
		j.setScale(scale);
		//j.setRotation( rot, j.rotationOrder()  );
		if( i == joints.size() - 1)
			//Effector Position
			pEndJoint = tran.rotatePivot(MSpace::kWorld);
		else
		{
			//get position of next joint
			MFnIkJoint j2( joints[i + 1]);
			pEndJoint = j2.rotatePivot(MSpace::kWorld);
		}
		MVector vBaseJoint(pBaseJoint[0]-pEndJoint[0], pBaseJoint[1]-pEndJoint[1], pBaseJoint[2]-pEndJoint[2]);
		startLength += vBaseJoint.length();
		float parm = curveFn.findParamFromLength( startLength );
		MPoint pFinalPos;
		curveFn.getPointAtParam( parm, pFinalPos );
		MVector vFinalJoint(pBaseJoint[0]-pFinalPos[0], pBaseJoint[1]-pFinalPos[1], pBaseJoint[2]-pFinalPos[2]);

		MVector crosVec = vBaseJoint^vFinalJoint;
		float w = sqrt((vBaseJoint.length() * vBaseJoint.length()) * (vFinalJoint.length() * vFinalJoint.length())) + vBaseJoint*vFinalJoint;
		//Calculate Twist
		{
			float twistValue;
			curveAttribute.getValueAtPosition(currJointRot, twistValue, &stat);
			//float rotVal = startTwist - preStartTwist + twistValue *( endTwist - preEndTwist - startTwist - preStartTwist );
			float rotVal = (1-twistValue)*v0 + twistValue*v1;
			MQuaternion qTwist( MAngle(rotVal - prevTwist, MAngle::kDegrees).asRadians(), vBaseJoint );
			j.rotateBy( qTwist, MSpace::kWorld );
			currJointRot += jointRotPercent;
			prevTwist = rotVal;
			//MGlobal::displayInfo(MString("CurrJointRot: ") + currJointRot);
			//MGlobal::displayInfo(MString("Rot Val: ") + rotVal);
		}
		//Calculate Roll
		if (i == 0)
		{
			if ( preRoll != roll ){
				MQuaternion qRoll( roll - preRoll, vBaseJoint );
				j.rotateBy( qRoll, MSpace::kWorld );
				preRollPlug.setDouble( roll );
			}
		}
		MQuaternion q(crosVec.x, crosVec.y, crosVec.z, w );
		//q.normalizeIt();
		j.rotateBy( q, MSpace::kWorld );
	}

	return MS::kSuccess;
}

void splineSolverNode::evaluateDG()
{
	//Use the Force!
	for (int i = 0; i < joints.size(); i++)
	{
		MFnIkJoint j( joints[i]);
		MPlug sxPlug = j.findPlug("sx");
		MPlug syPlug = j.findPlug("sy");
		MPlug szPlug = j.findPlug("sz");
		double sxValue = sxPlug.asDouble();
		sxPlug.setDouble(sxValue);
		double syValue = syPlug.asDouble();
		syPlug.setDouble(syValue);
		double szValue = szPlug.asDouble();
		szPlug.setDouble(szValue);
	}
}

/////////////////////////////////////////////////////////
//
// Register the solver
//
/////////////////////////////////////////////////////////
MStatus initializePlugin( MObject obj )
{
	MStatus			status;
	MFnPlugin	plugin( obj, "Ignacio Urruty", "1.0", "Any");

	status = plugin.registerNode("splineSolverNode", 
								 splineSolverNode::id,
								 &splineSolverNode::creator,
								 &splineSolverNode::initialize,
								 MPxNode::kIkSolverNode);
	if (!status) {
		status.perror("registerNode");
		return status;
	}

	return status;
}

MStatus uninitializePlugin( MObject obj )
{
	MStatus   		status;
	MFnPlugin	plugin( obj );

	status = plugin.deregisterNode(splineSolverNode::id);
	if (!status) {
		status.perror("deregisterNode");
		return status;
	}

	return status;
}
