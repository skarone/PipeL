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
	MQuaternion     quaternionFromVectors(MVector vec1, MVector vec2);
	void			gsOrthonormalize( MVector &normal, MVector &tangent );
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
	MVector initNormal = curveFn.normal(0);
	MVector initTangent = curveFn.tangent(0);
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
		attr = fnAttr.create("anchorPosition", "ancp", MFnNumericData::kDouble, 0.0);
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
		attr = fnAttr.create("initNormal", "norm", MFnNumericData::k3Double);
		fnAttr.setDefault(initNormal.x, initNormal.y, initNormal.z);
		fnAttr.setKeyable(0);
		fnAttr.setWritable(1);
		fnAttr.setHidden(1);
		fnAttr.setStorable(1);
		fnAttr.setReadable(1);
		fnHandle.addAttribute(attr, MFnDependencyNode::kLocalDynamicAttr);
		attr = fnAttr.create("initTangent", "tang", MFnNumericData::k3Double);
		fnAttr.setDefault(initTangent.x, initTangent.y, initTangent.z);
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
		attr = fnAttr.create("startTwist", "strtw", MFnNumericData::kDouble, 0.0);
		fnAttr.setKeyable(1);
		fnAttr.setWritable(1);
		fnAttr.setHidden(0);
		fnAttr.setStorable(1);
		fnAttr.setReadable(1);
		fnHandle.addAttribute(attr, MFnDependencyNode::kLocalDynamicAttr);
		attr = fnAttr.create("endTwist", "endtw", MFnNumericData::kDouble, 0.0);
		fnAttr.setKeyable(1);
		fnAttr.setWritable(1);
		fnAttr.setHidden(0);
		fnAttr.setStorable(1);
		fnAttr.setReadable(1);
		fnHandle.addAttribute(attr, MFnDependencyNode::kLocalDynamicAttr);
		MObject twistRamp = MRampAttribute::createCurveRamp("twistRamp", "twr");
		fnHandle.addAttribute(twistRamp, MFnDependencyNode::kLocalDynamicAttr);
		MObject scaleRamp = MRampAttribute::createCurveRamp("scaleRamp", "scr");
		fnHandle.addAttribute(scaleRamp, MFnDependencyNode::kLocalDynamicAttr);
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
MQuaternion splineSolverNode::quaternionFromVectors(MVector vec1, MVector vec2)
{
		MVector crosVec = vec1^vec2;
		float w = sqrt((vec1.length() * vec1.length()) * (vec2.length() * vec2.length())) + vec1*vec2;
		//float w = 1.0f + vBaseJoint*vFinalJoint;
		MQuaternion q(crosVec.x, crosVec.y, crosVec.z, w );
		q.normalizeIt();
		return q;
}

void splineSolverNode::gsOrthonormalize( MVector &normal, MVector &tangent )
{
    // Gram-Schmidt Orthonormalization
    normal.normalize();
    MVector proj = normal * ( tangent * normal ); // normal * dotProduct(tangent,normal)
    tangent = tangent - proj;
    tangent.normalize();
    
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
	//Scale Ramp
	MPlug scaleRamp = fnHandle.findPlug("scaleRamp");
	MRampAttribute curveScaleAttribute( scaleRamp, &stat );
	//Roll
	MPlug rollPlug = fnHandle.findPlug("roll");
	double roll = rollPlug.asDouble();
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
	//get Init normal
	MPlug initNormalPlug = fnHandle.findPlug("norm");
	double nx = initNormalPlug.child(0).asDouble();
	double ny = initNormalPlug.child(1).asDouble();
	double nz = initNormalPlug.child(2).asDouble();
	MVector eyeUp( nx, ny, nz );
	//get Init Tangent
	MPlug initTangentPlug = fnHandle.findPlug("tang");
	double tx = initTangentPlug.child(0).asDouble();
	double ty = initTangentPlug.child(1).asDouble();
	double tz = initTangentPlug.child(2).asDouble();
	MVector eyeV( tx, ty, tz );
	
	MFnIkJoint j( joints[0] );
	j.setTranslation( MVector( pBaseJoint ), MSpace::kWorld );
	float jointRotPercent = 1.0/joints.size();
	float currJointRot = 0;
	float prevTwist = 0;
	double angle;
	//j.setScale(scale);
	for (int i = 0; i < joints.size(); i++)
	{
		MFnIkJoint j( joints[i]);
		pBaseJoint = j.rotatePivot(MSpace::kWorld);
		//Calculate Scale
		float scaleValue;
		curveScaleAttribute.getValueAtPosition(currJointRot, scaleValue, &stat);
		//if ( scale[0] >= 1 ) // Stretch
			scale[1] = 1 + scaleValue * ( 1 - scale[0] );
		/*
		else //Squash
			scale[1] = 1 + scaleValue * ( 1.0 - scale[0] );
		*/
		if (scale[1] < 0)
			scale[1] = 0;
		scale[2] = scale[1];
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
		MVector eyeAim(1.0,0.0,0.0);
		MPoint pFinalPos;
		float parm = curveFn.findParamFromLength( startLength );
		//Aim to final Pos
		curveFn.getPointAtParam( parm, pFinalPos, MSpace::kWorld );
		MVector eyeU(pBaseJoint[0]-pFinalPos[0], pBaseJoint[1]-pFinalPos[1], pBaseJoint[2]-pFinalPos[2]);
		eyeU.normalize();
		MVector eyeW( eyeU ^ eyeV );
		eyeW.normalize();
		eyeV = eyeW ^ eyeU;
		MQuaternion qU( -eyeAim, eyeU );
		
		MVector upRotated( eyeUp.rotateBy( qU ));
		angle = acos( upRotated*eyeV );
		
		//Calculate Twist
		{
			float twistValue;
			curveAttribute.getValueAtPosition(currJointRot, twistValue, &stat);
			double rotVal = (1-twistValue)*startTwist + twistValue*endTwist;
			angle += MAngle(rotVal, MAngle::kDegrees).asRadians();
			currJointRot += jointRotPercent;
		}
		//Calculate Roll
		angle += roll;
		
		MQuaternion qV(angle, eyeU);
		
		MQuaternion q(qU*qV);
		
		j.setRotation( q, MSpace::kWorld );
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
