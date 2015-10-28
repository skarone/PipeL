#include "ropeGenerator.h"
#include <maya/MFnNurbsCurve.h>
#include <maya/MDataBlock.h>
#include <maya/MDataHandle.h>
#include <maya/MGlobal.h>
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
#include <maya/MRampAttribute.h>

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
ropeGenerator::~ropeGenerator(){}

MStatus ropeGenerator::compute( const MPlug& plug, MDataBlock& data )
{
	MStatus status;

	if ( plug == outMesh )
	{
		//Get Curve
		MDataHandle inCurve_Hdl = data.inputValue( inCurve, &status );
		if (status != MS::kSuccess ){
			MGlobal::displayError( "Node ropeGenerator needs an Input Curve" );
			return MS::kSuccess;
		}
		MObject inCurveObj = inCurve_Hdl.asNurbsCurve();
		MFnNurbsCurve curveFn( inCurveObj );
		
		//Get Attributes
		int inDiv = data.inputValue( divisions ).asInt();
		bool inCreateRope = data.inputValue( createRope ).asBool();
		int inRopesCount = data.inputValue( ropesCount ).asInt();
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
		faceCounts.clear();
		faceConnects.clear();
		points.clear();
		if (inCreateRope)
			inPointsCount = ( inPointsPerRope + 2 ) * inRopesCount;
		int numVertices = ( inDiv + 1 ) * inPointsCount;
		int numFaces = ( inPointsCount * inDiv ) + 2;
		float param;
		float lengPerDiv = curveFn.length() / inDiv;
		float baseLeng = lengPerDiv;
		float baseParamForRamp = 0;
		float paramForRamp = 1.0 / float( inDiv );
		for (int d = 0; d < inDiv + 1; d++)
		{
			if (d == 0)
			{
				param = 0;
				faceCounts.append( inPointsCount );
				for ( int i = inPointsCount - 1; i >= 0; i-- )
				{
					faceConnects.append( i );
				}
			}else{
				param = curveFn.findParamFromLength( baseLeng );
				for ( int i = 0; i < inPointsCount; i++ )
				{
					faceCounts.append( 4 );
				}
				for ( int f = 0; f < inPointsCount; f++ )
				{
					if( f == ( inPointsCount - 1 ))
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
			float divTwist;
			inTwistRamp.getValueAtPosition( baseParamForRamp, divTwist );
			float divTaper;
			inRadRamp.getValueAtPosition( baseParamForRamp, divTaper );
			baseParamForRamp += paramForRamp;
			if (inCreateRope)
				createRopesRings( inRopesCount, 
								getMatrixFromParamCurve( curveFn, param, inTwist, MAngle( divTwist, MAngle::kDegrees )  ),
								points, inPointsPerRope, inRopesStrength, inRadius * divTaper);
			else
				createCriclePoints( inPointsCount, 
									getMatrixFromParamCurve( curveFn, param, inTwist, MAngle( divTwist, MAngle::kDegrees ) ),
									points, inRadius * divTaper );
		}
		fnMesh.create( numVertices, numFaces, points, faceCounts, faceConnects, outMeshData );
		outputHandle.set(outMeshData);
		outputHandle.setClean();
	}
	return MS::kSuccess;
}

MMatrix ropeGenerator::getMatrixFromParamCurve( MFnNurbsCurve &curveFn, float param, float twist, MAngle divTwist )
{

	MPoint pDivPos;
	curveFn.getPointAtParam( param, pDivPos, MSpace::kWorld );
	MVector vTangent( curveFn.tangent( param, MSpace::kObject ).normal() );
	//vTangent = vTangent - MVector( pDivPos );
	MVector vBase(0,1,0);
	MVector vNormal( vBase ^ vTangent );
	MQuaternion qTwist( twist * divTwist.asRadians(), vTangent );
	vNormal = vNormal.rotateBy( qTwist );
	MVector vExtra( vNormal ^ vTangent );
	vNormal.normalize();
	vTangent.normalize();
	vExtra.normalize();
	double dTrans[4][4] ={
						{vNormal.x, vNormal.y, vNormal.z, 0.0f},
						{vTangent.x, vTangent.y, vTangent.z, 0.0f},
						{vExtra.x, vExtra.y, vExtra.z, 0.0f},
						{pDivPos.x,pDivPos.y,pDivPos.z, 1.0f}};
	MMatrix mTrans( dTrans );
	return mTrans;
}

void ropeGenerator::createCriclePoints( int pointsCount, MMatrix bMatrix, MFloatPointArray &points, float radius )
{
	MPoint baseVector2( radius,0,0 );
	baseVector2 = baseVector2 * bMatrix;
	points.append( MFloatPoint( baseVector2.x, baseVector2.y, baseVector2.z, 1.0 ) );
	float baseAngle = 360.0f / float( pointsCount );
	for (int d = 1; d < pointsCount; d++ )
	{
		MVector vVector( radius,0,0 );
		vVector = vVector.rotateBy( MVector::kYaxis, 
							MAngle( baseAngle * float( d ),MAngle::kDegrees).asRadians() );
		MPoint point( vVector.x, vVector.y, vVector.z );
		point = point * bMatrix;
		points.append( MFloatPoint( point.x, point.y, point.z, 1.0 ));
	}

}

void ropeGenerator::createRopesRings( int ropesCount, MMatrix bMatrix, MFloatPointArray &points, int pointsCount, float ropeStrength, float radius )
{
	MAngle angle( (180.0/ ropesCount ), MAngle::kDegrees );
	float distanceToMoveRope = cos( angle.asRadians() );
	float singleRopeRadius = sin( angle.asRadians() );
	float baseAngle = 360.0f / float( ropesCount ); 
	for ( int d = 1; d < ropesCount + 1; d++)
	{
		MFloatPointArray ropePoints( createHalfRope( pointsCount, singleRopeRadius ) );
		for ( int ropP = 0; ropP < ropePoints.length(); ropP++)
		{
			MFloatPoint ropPoint( ropePoints[ropP] );
			MVector ropV( ropPoint.x, ropPoint.y, ropPoint.z * ropeStrength );
			ropV = ropV + MVector( 0,0,-distanceToMoveRope );
			ropV = ropV.rotateBy( MVector::kYaxis, MAngle( baseAngle * float( d ), MAngle::kDegrees).asRadians() );
			MPoint ropFinalPoint( ropV * radius );
			ropFinalPoint = ropFinalPoint * bMatrix;
			points.append( MFloatPoint( ropFinalPoint.x, ropFinalPoint.y, ropFinalPoint.z ) );
		}
	}
}

MFloatPointArray ropeGenerator::createHalfRope( int pointsCount, float radius )
{
	MFloatPointArray points;
	MPoint baseVector( 1,0,0 );
	baseVector =  baseVector * radius;
	points.append( MFloatPoint( baseVector.x, baseVector.y, baseVector.z, 1.0 ) );
	float fbaseAngle = 180.0 / float( pointsCount );
	for (int d = 1; d < pointsCount; d++)
	{
		if (d == 1)
		{
			MAngle baseAngle((fbaseAngle * 0.25), MAngle::kDegrees  );
			MVector vVector( baseVector );
			vVector = vVector.rotateBy( MVector::kYaxis, baseAngle.asRadians() );
			points.append( MFloatPoint( vVector.x, vVector.y, vVector.z, 1.0 ) );
		}
		MAngle baseAngle((fbaseAngle * float( d ) ), MAngle::kDegrees  );
		MVector vVector( baseVector );
		vVector = vVector.rotateBy( MVector::kYaxis, baseAngle.asRadians() );
		points.append( MFloatPoint( vVector.x, vVector.y, vVector.z, 1.0 ) );
		if ( d == pointsCount - 1 )
		{
			MAngle baseAngle((fbaseAngle * ( d + 0.75 )), MAngle::kDegrees  );
			MVector vVector( baseVector );
			vVector = vVector.rotateBy( MVector::kYaxis, baseAngle.asRadians() );
			points.append( MFloatPoint( vVector.x, vVector.y, vVector.z, 1.0 ) );
		}

	}
	return points;
}

void* ropeGenerator::creator()
{
	return new ropeGenerator();
}

MStatus ropeGenerator::initialize()
{
	MStatus stat;
	MFnTypedAttribute tAttr;
	MFnNumericAttribute nAttr;
	MRampAttribute rAttr;

	inCurve = tAttr.create( "inCurve", "inCurve", MFnData::kNurbsCurve );
	tAttr.setHidden( true);

	divisions = nAttr.create( "divisions", "divisions", MFnNumericData::kInt, 15 );
	nAttr.setMin( 2 );
	nAttr.setWritable( true );
	nAttr.setKeyable( true );
	nAttr.setStorable( true );

	createRope = nAttr.create( "createRope", "createRope", MFnNumericData::kBoolean, false );
	nAttr.setWritable( true );
	nAttr.setStorable( true );
	nAttr.setKeyable( true );

	ropesCount = nAttr.create( "ropesCount", "ropesCount", MFnNumericData::kInt, 5 );
	nAttr.setMin( 3 );
	nAttr.setWritable( true );
	nAttr.setKeyable( true );
	nAttr.setStorable( true );

	pointsPerRope = nAttr.create( "pointsPerRope", "pointsPerRope", MFnNumericData::kInt, 6 );
	nAttr.setMin( 3 );
	nAttr.setWritable( true );
	nAttr.setKeyable( true );
	nAttr.setStorable( true );

	ropesStrength = nAttr.create( "ropesStrength", "ropesStrength", MFnNumericData::kFloat, 1.0f );
	nAttr.setMin( 0.0 );
	nAttr.setMax( 1.0 );
	nAttr.setWritable( true );
	nAttr.setStorable( true );
	nAttr.setKeyable( true );

	pointsCount = nAttr.create( "pointsCount", "pointsCount", MFnNumericData::kInt, 5 );
	nAttr.setWritable( true );
	nAttr.setKeyable( true );
	nAttr.setStorable( true );

	radius = nAttr.create( "radius", "radius", MFnNumericData::kFloat, 1.0f );
	nAttr.setMin( 0.0 );
	nAttr.setKeyable( true );
	nAttr.setWritable( true );
	nAttr.setStorable( true );

	taperRamp = rAttr.createCurveRamp( "tapper", "tapper" );

	twist = nAttr.create( "twist", "twist", MFnNumericData::kFloat, 0.0f );
	nAttr.setWritable( true );
	nAttr.setKeyable( true );
	nAttr.setStorable( true );

	twistRamp = rAttr.createCurveRamp( "twistRamp", "twistRamp" );

	outMesh = tAttr.create( "outMesh", "outMesh", MFnData::kMesh );
	tAttr.setWritable( false );
	tAttr.setStorable( false );

	stat = addAttribute( inCurve );
	if (!stat) { stat.perror("addAttribute inCurve"); return stat;}
	stat = addAttribute( divisions );
	if (!stat) { stat.perror("addAttribute divisions"); return stat;}
	stat = addAttribute( createRope );
	if (!stat) { stat.perror("addAttribute createRope"); return stat;}
	stat = addAttribute( ropesCount );
	if (!stat) { stat.perror("addAttribute ropesCount"); return stat;}
	stat = addAttribute( pointsPerRope );
	if (!stat) { stat.perror("addAttribute pointsPerRope"); return stat;}
	stat = addAttribute( ropesStrength );
	if (!stat) { stat.perror("addAttribute ropesStrength"); return stat;}
	stat = addAttribute( pointsCount );
	if (!stat) { stat.perror("addAttribute pointsCount"); return stat;}
	stat = addAttribute( radius );
	if (!stat) { stat.perror("addAttribute radius"); return stat;}
	stat = addAttribute( taperRamp );
	if (!stat) { stat.perror("addAttribute taperRamp"); return stat;}
	stat = addAttribute( twist );
	if (!stat) { stat.perror("addAttribute twist"); return stat;}
	stat = addAttribute( twistRamp );
	if (!stat) { stat.perror("addAttribute twistRamp"); return stat;}
	stat = addAttribute( outMesh );
	if (!stat) { stat.perror("addAttribute outMesh"); return stat;}


	stat = attributeAffects( inCurve, outMesh );
	if (!stat) { stat.perror("attributeAffects"); return stat;}
	stat = attributeAffects( divisions, outMesh );
	if (!stat) { stat.perror("attributeAffects"); return stat;}
	stat = attributeAffects( createRope, outMesh );
	if (!stat) { stat.perror("attributeAffects"); return stat;}
	stat = attributeAffects( ropesCount, outMesh );
	if (!stat) { stat.perror("attributeAffects"); return stat;}
	stat = attributeAffects( pointsPerRope, outMesh );
	if (!stat) { stat.perror("attributeAffects"); return stat;}
	stat = attributeAffects( ropesStrength, outMesh );
	if (!stat) { stat.perror("attributeAffects"); return stat;}
	stat = attributeAffects( pointsCount, outMesh );
	if (!stat) { stat.perror("attributeAffects"); return stat;}
	stat = attributeAffects( radius, outMesh );
	if (!stat) { stat.perror("attributeAffects"); return stat;}
	stat = attributeAffects( taperRamp, outMesh );
	if (!stat) { stat.perror("attributeAffects"); return stat;}
	stat = attributeAffects( twist, outMesh );
	if (!stat) { stat.perror("attributeAffects"); return stat;}
	stat = attributeAffects( twistRamp, outMesh );
	if (!stat) { stat.perror("attributeAffects"); return stat;}

	return MS::kSuccess;
}


