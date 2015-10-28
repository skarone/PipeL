//
//
// This plugin generates a poly mesh based on an input curve
// Is designed to create ropes very easy
//
//
//
//
//
#include <maya/MPxNode.h>
#include <maya/MFloatPointArray.h>
#include <maya/MFnNurbsCurve.h>

class ropeGenerator: public MPxNode
{
public:
	ropeGenerator();
	virtual ~ropeGenerator();

	virtual MStatus compute( const MPlug& plug, MDataBlock& data );

	static void* creator();
	static MStatus initialize();
	static void createCriclePoints( int pointsCount, MMatrix bMatrix, MFloatPointArray &points, float radius);
	static void createRopesRings( int ropesCount, MMatrix bMatrix, MFloatPointArray &points, int pointsCount, float ropeStrength, float radius );
	static MFloatPointArray createHalfRope( int pointsCount, float radius );
	static MMatrix getMatrixFromParamCurve( MFnNurbsCurve &curveFn, float param, float twist, MAngle divTwist );
	static MTypeId id;


public:
	//Attributes for node
	static MObject inCurve;
	static MObject createRope;
	static MObject ropesCount;
	static MObject pointsPerRope;
	static MObject pointsCount;
	static MObject ropesStrength;
	static MObject radius;
	static MObject taperRamp;
	static MObject divisions;
	static MObject twist;
	static MObject twistRamp;
	static MObject outMesh;

};
