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

class ropeGenerator: public MPxNode
{
public:
	ropeGenerator();
	virtual ~ropeGenerator();

	virtual MStatus compute( const MPlug& plug, MDataBlock& data );

	static void* creator();
	static MStatus initialize();
	static MTypeId id;

private:
	//Attributes for node
	static MObject inCurve;
	static MObject ropesCount;
	static MObject radius;
	static MObject taperRamp;
	static MObject divisions;
	static MObject twist;
	static MObject twistRamp;
	static MObject outMesh;

};
