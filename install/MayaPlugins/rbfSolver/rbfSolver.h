#include <maya/MPxNode.h>
#include <maya/MFloatVectorArray.h>

class rbfSolver: public MPxNode
{
public:
	rbfSolver();
	virtual ~rbfSolver();

	virtual MStatus compute( const MPlug& plug, MDataBlock& data );

	static void* creator();
	static MStatus initialize();
	static MTypeId id;

	static MObject inPositions;
	static MObject inValue;
	static MObject inValues;
	static MObject inCenters;
	static MObject outValue;
	static MObject outValues;

	MFloatVectorArray xi;
	int N;
};