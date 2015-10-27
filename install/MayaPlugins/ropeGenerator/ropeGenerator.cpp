#include "ropeGenerator.h"
#include <maya/MFnNurbsCurve.h>
#include <maya/MGlobal.h>
#include <maya/MRampAttribute.h>
#include <maya/MPoint.h>
#include <maya/MFnMesh.h>
#include <maya/MFnMeshData.h>
#include <maya/MMatrix.h>
#include <maya/MAngle.h>
#include <maya/MQuaternion.h>
#include <maya/MFloatPoint.h>
#include <maya/MFloatPointArray.h>
#include <maya/MFnTypedAttribute.h>
#include <maya/MFnNumericAttribute.h>

MObject ropeGenerator::inCurve;
MObject ropeGenerator::divisions;
MObject ropeGenerator::createRope;
MObject ropeGenerator::ropesCount;
MObject ropeGenerator::pointsPerRope;
MObject ropeGenerator::ropesStrength;
MObject ropeGenerator::pointsCount;
MObject ropeGenerator::radius;
MObject ropeGenerator::taperRamp;
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
	int inDiv = data.inputValue( divisions ).asInt();
	bool inCreateRope = data.inputValue( createRope ).asBool();
	float inRopesCount = data.inputValue( ropesCount ).asFloat();
	int inPointsPerRope = data.inputValue( pointsPerRope ).asInt();
	int inPointsCount = data.inputValue( pointsCount ).asInt();
	float inRopesStrength = data.inputValue( ropesStrength ).asFloat();
	float inRadius = data.inputValue( radius ).asFloat();
	MRampAttribute inRadRamp( thisMObject(), taperRamp );
	float inTwist = data.inputValue( twist ).asFloat();
	MRampAttribute inTwistRamp( thisMObject(), twistRamp );

	MFnMesh fnMesh;
	MFnMeshData dataCreator;
	MObject outMeshData;
	outMeshData = dataCreator.create();
	MDataHandle outputHandle = data.outputValue(outMesh);
	//createBase 
	MIntArray faceCounts, faceConnects;
	MFloatPointArray points;
	int numVertices = ( inDiv + 1 ) * inPointsCount;
	int numFaces = ( inPointsCount * inDiv ) + 2;
	float param;
	float lengPerDiv = curveFn.length() / inDiv;
	float baseLeng = lengPerDiv;
	MMatrix mTrans;
	for (int d = 0; d <= inDiv + 1; d++)
	{
		if (d == 0)
		{
			param = 0;
			faceCounts.append( inPointsCount );
			for ( int i = inPointsCount; i > 0; i-- )
			{
				faceConnects.append( i );
			}
		}else{
			param = curveFn.findParamFromLength( baseLeng );
			for ( int i = 0; i < inPointsCount; i++ )
			{
				faceCounts.append( 4 );
			}
			for ( int f = 0; f< inPointsCount; f++ )
			{
				if( f == inPointsCount - 1)
				{
					faceConnects.append( ( f + 1 + ( d * inPointsCount ) ) - inPointsCount - inPointsCount );
					faceConnects.append( ( f + 1 + ( d * inPointsCount ) - inPointsCount ) );
					faceConnects.append( f + 1 + ( d * inPointsCount )  - 1 );
					faceConnects.append( f + 1 + ( d * inPointsCount ) - inPointsCount - 1 );
				}else{
					faceConnects.append( ( f + ( d * inPointsCount ) ) - inPointsCount );
					faceConnects.append( f + 1 + ( d * inPointsCount ) - inPointsCount );
					faceConnects.append( f + 1 + ( d * inPointsCount ) );
					faceConnects.append( ( f + ( d * inPointsCount )) );
				}
			}
			if ( d == inDiv )
			{
				faceCounts.append( inPointsCount );
				for ( int i = 0; i <  inPointsCount; i++ )
				{
					faceConnects.append( ( inPointsCount * inDiv ) + i );
				}
			}
			baseLeng += lengPerDiv;
		}
		mTrans = getMatrixFromParamCurve( curveFn, param, inTwist );
		if (inCreateRope)
			createRopesRings( inRopesCount, mTrans, points, inPointsPerRope, inRopesStrength );
		else
			createCriclePoints( inPointsCount, mTrans, points );
	}
	fnMesh.create( numVertices, numFaces, points, faceCounts, faceConnects, outMeshData );
	outputHandle.set(outMeshData);
	
}

MMatrix ropeGenerator::getMatrixFromParamCurve( MFnNurbsCurve &curveFn, float param, MAngle twist )
{

	MPoint pDivPos;
	curveFn.getPointAtParam( param, pDivPos, MSpace::kWorld );
	MVector vTangent( curveFn.tangent( param, MSpace::kObject ) );
	MVector vBase(0,1,0);
	MVector vNormal( vBase ^ vTangent );
	MQuaternion qTwist( twist.asRadians(), vTangent );
	vNormal = vNormal.rotateBy( qTwist );
	MVector vExtra( vNormal ^ vTangent );
	double dTrans[4][4] ={
						{vExtra.x, vExtra.y, vExtra.z, 0.0f},
						{vTangent.x, vTangent.y, vTangent.z, 0.0f},
						{vNormal.x, vNormal.y, vNormal.z, 0.0f},
						{pDivPos.x,pDivPos.y,pDivPos.z, 1.0f}};
	MMatrix mTrans( dTrans );
	return mTrans;
}

void ropeGenerator::createCriclePoints( int pointsCount, MMatrix bMatrix, MFloatPointArray &points)
{
	MPoint baseVector( 1,0,0 );
	MPoint baseVector2( 1,0,0 );
	baseVector2 = baseVector2 * bMatrix;
	points.append( MFloatPoint( baseVector2.x, baseVector2.y, baseVector2.z, 1.0 ) );
	for (int d = 1; d < pointsCount; d++ )
	{
		MVector vVector( baseVector );
		vVector = vVector.rotateBy( MVector::kYaxis, MAngle(( 360.0 / pointsCount * d ),MAngle::kDegrees).asRadians() );
		MPoint point( vVector );
		point = point * bMatrix;
		points.append( MFloatPoint( vVector ));
	}

}

void ropeGenerator::createRopesRings( int ropesCount, MMatrix bMatrix, MFloatPointArray &points, int pointsCount, float ropeStrength )
{
	MAngle angle( (180.0/ ropesCount ), MAngle::kDegrees );
	float distanceToMoveRope = cos( angle.asRadians() );
	float singleRopeRadius = sin( angle.asRadians() );
	for ( int d = 1; d < ropesCount + 1; d++)
	{
		MFloatPointArray ropePoints( createHalfRope( pointsCount, singleRopeRadius ) );
		for ( int ropP = 0; ropP < ropePoints.length(); ropP++)
		{
			MFloatPoint ropPoint( ropePoints[ropP] );
			MVector ropV( ropPoint.x, ropPoint.y, ropPoint.z * ropeStrength );
			ropV = ropV + MVector( 0,0,-distanceToMoveRope );
			ropV = ropV.rotateBy( MVector::kYaxis, MAngle(( 360.0 / ropesCount * d), MAngle::kDegrees).asRadians() );
			MPoint ropPoint( ropV );
			ropPoint = ropPoint * bMatrix;
			points.append( MFloatPoint( ropPoint.x, ropPoint.y, ropPoint.z ) );
		}
	}
}

MFloatPointArray ropeGenerator::createHalfRope( int pointsCount, float radius )
{
	MFloatPointArray points;
	MPoint baseVector( 1,0,0 );
	baseVector =  baseVector * radius;
	points.append( MFloatPoint( baseVector.x, baseVector.y, baseVector.z, 1.0 ) );
	for (int d = 1; d < pointsCount; d++)
	{
		if (d == 1)
		{
			MAngle baseAngle((180.0 / pointsCount * 0.25), MAngle::kDegrees  );
			MVector vVector( baseVector );
			vVector = vVector.rotateBy( MVector::kYaxis, baseAngle.asRadians() );
			points.append( MFloatPoint( vVector.x, vVector.y, vVector.z, 1.0 ) );
		}
		MAngle baseAngle((180.0 / pointsCount * d ), MAngle::kDegrees  );
		MVector vVector( baseVector );
		vVector = vVector.rotateBy( MVector::kYaxis, baseAngle.asRadians() );
		points.append( MFloatPoint( vVector.x, vVector.y, vVector.z, 1.0 ) );
		if ( d == pointsCount - 1 )
		{
			MAngle baseAngle((180.0 / pointsCount * ( d + 0.75 )), MAngle::kDegrees  );
			MVector vVector( baseVector );
			vVector = vVector.rotateBy( MVector::kYaxis, baseAngle.asRadians() );
			points.append( MFloatPoint( vVector.x, vVector.y, vVector.z, 1.0 ) );
		}

	}
	return points;
}

MStatus ropeGenerator::initialize()
{
	MStatus stat;
	MFnTypedAttribute tAttr;
	MFnNumericAttribute nAttr;

	inCurve = tAttr.create( "inCurve", "inCurve", MFnData::kNurbsCurve );
	tAttr.setHidden( true);

	divisions = nAttr.create( "divisions", "divisions", MFnNumericData::kInt, 15 );
	nAttr.setWritable( true );
	nAttr.setStorable( true );

	createRope = nAttr.create( "createRope", "createRope", MFnNumericData::kBoolean );
	nAttr.setWritable( true );
	nAttr.setStorable( true );

	ropesCount = nAttr.create( "ropesCount", "ropesCount", MFnNumericData::kInt, 5 );
	nAttr.setWritable( true );
	nAttr.setStorable( true );

	pointsPerRope = nAttr.create( "pointsPerRope", "pointsPerRope", MFnNumericData::kInt, 6 );
	nAttr.setWritable( true );
	nAttr.setStorable( true );

	ropesStrength = nAttr.create( "ropesStrength", "ropesStrength", MFnNumericData::kFloat, 1.0f );
	nAttr.setMin( 0.0 );
	nAttr.setMax( 1.0 );
	nAttr.setWritable( true );
	nAttr.setStorable( true );

	outMesh = tAttr.create( "outMesh", "outMesh", MFnData::kMesh );
	tAttr.setWritable( false );
	tAttr.setStorable( false );
}
