#include <maya/MPxNode.h>
#include <maya/MFloatVectorArray.h>
#include <maya/MFloatArray.h>
#include <vector>
#include "matrix.h"

class rbfSolver: public MPxNode
{
public:
	rbfSolver();
	~rbfSolver();

	virtual MStatus compute( const MPlug& plug, MDataBlock& data );

	MFloatVector amax( MFloatVectorArray x1 );
	MFloatVector amin( MFloatVectorArray x1 );
	MFloatArray _euclidean_norm( MFloatVectorArray x1, MFloatVectorArray x2 );
	MFloatArray _h_gaussian( MFloatArray r );
	MFloatArray _h_multiquadric( MFloatArray r );
	MFloatArray _h_linear( MFloatArray r );
	MFloatArray _h_cubic( MFloatArray r );
	MFloatArray _h_quintic( MFloatArray r );
	std::vector< Matrix > linalg( Matrix A, Matrix di );

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
	float epsilon;
	int N;
};