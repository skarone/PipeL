#include "ropeGenerator.h"
#include <maya/MFnNurbsCurve.h>
#include <maya/MGlobal.h>
#include <maya/MRampAttribute.h>
#include <maya/MPoint.h>
#include <maya/MFnMesh.h>
#include <maya/MFnMeshData.h>
#include <maya/MMatrix.h>

MObject ropeGenerator::inCurve;
MObject ropeGenerator::ropesCount;
MObject ropeGenerator::radius;
MObject ropeGenerator::taperRamp;
MObject ropeGenerator::divisions;
MObject ropeGenerator::twist;
MObject ropeGenerator::twistRamp;
MObject ropeGenerator::outMesh;
MTypeId ropeGenerator::id( 0x00348 );

ropeGenerator::ropeGenerator(){}
ropeGenerator::ropeGenerator(){}

MStatus ropeGenerator::compute( const MPlug& plug, MDataBlock& data )
{
	MStatus status;

	if(plug != outMesh){
		return MS::kSuccess;
	}

	//Get Curve
	MDataHandle inCurve_Hdl = data.inputValue( inCurve, &status );
	if (status != MS::kSuccess ){
		MGlobal::displayError( "Node ropeGenerator needs an Input Curve" );
		return MS::kSuccess;
	}
	MObject inCurveObj = inCurve_Hdl.asNurbsCurveTransformed();
	MFnNurbsCurve curveFn( inCurveObj );
	
	//Get Attributes
	float inRopesCount = data.inputValue( ropesCount ).asFloat();
	float inRadius = data.inputValue( radius ).asFloat();
	MRampAttribute inRadRamp( thisMObject(), taperRamp );
	float inTwist = data.inputValue( twist ).asFloat();
	MRampAttribute inTwistRamp( thisMObject(), twistRamp );
	int inDiv = data.inputValue( divisions ).asInt();

	MFnMesh fnMesh;
	MFnMeshData dataCreator;
	MObject outMeshData;
	outMeshData = dataCreator.create();
	//createBase 
	MPoint pDivPos;
	curveFn.getPointAtParam( 0, pDivPos, MSpace::kWorld );
	MVector vNormal( curveFn.normal( 0, MSpace::kObject ) );
	MVector vTangent( curveFn.tangent( 0, MSpace::kObject ) );
	MVector vExtra( vNormal ^ vTangent );
	double dTrans[4][4] ={
						{vExtra.x, vExtra.y, vExtra.z, 0.0f},
						{vTangent.x, vTangent.y, vTangent.z, 0.0f},
						{vNormal.x, vNormal.y, vNormal.z, 0.0f},
						{pDivPos.x,pDivPos.y,pDivPos.z, 1.0f}};
	MMatrix mTrans( dTrans );


	for (int d = 1; d <= inDiv; d++){
		//get Param on curve Based on divisions
		//last d should get a Param of 1 and first one 0
		float param = float(d) / float( inDiv );
		curveFn.getPointAtParam( param, pDivPos, MSpace::kWorld );
		vNormal = curveFn.normal( param, MSpace::kObject );
		vTangent = curveFn.tangent( param, MSpace::kObject );
		vExtra =vNormal ^ vTangent;
		double dTrans2[4][4] ={
						{vExtra.x, vExtra.y, vExtra.z, 0.0f},
						{vTangent.x, vTangent.y, vTangent.z, 0.0f},
						{vNormal.x, vNormal.y, vNormal.z, 0.0f},
						{pDivPos.x,pDivPos.y,pDivPos.z, 1.0f}};
		MMatrix mTrans2( dTrans2 );
		
	}

}
