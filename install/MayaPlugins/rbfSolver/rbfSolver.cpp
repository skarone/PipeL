#include "rbfSolver.h"
//#include "matrix.h"
#include <maya/MFnNumericAttribute.h>
#include <maya/MFnCompoundAttribute.h>
#include <maya/MStatus.h>
#include <maya/MArrayDataBuilder.h>

MObject rbfSolver::inPositions;
MObject rbfSolver::inValue;
MObject rbfSolver::inValues;
MObject rbfSolver::inCenters;
MObject rbfSolver::outValue;
MObject rbfSolver::outValues;

MTypeId rbfSolver::id( 0x00347 );

rbfSolver::rbfSolver(){};
rbfSolver::~rbfSolver(){};


MStatus rbfSolver::compute( const MPlug& plug, MDataBlock& data )
{
	MStatus stats;
    MObject thisNode = thisMObject();
    MPlug wPlug(thisNode, outValue);
	
	////////////////////////////////////////
	//Get Input Positions
	MArrayDataHandle inPositionsH = data.inputArrayValue( inPositions, &stats );
	MFloatVectorArray xi;
	unsigned inPosCount = inPositionsH.elementCount();
	if (inPosCount == 0)
		return MS::kSuccess;
	for( int i = 0; i < inPosCount; i++) {
		inPositionsH.jumpToElement(i);
		MDataHandle pointH = inPositionsH.inputValue(&stats);
		xi.append( pointH.asFloatVector() );
	}
	N = xi.length();
	////////////////////////////////////////
	//Get InputValues
	MArrayDataHandle inValuesH = data.inputArrayValue( inValues, &stats );
	unsigned inValCount = inValuesH.elementCount();
	if (inValCount == 0)
		return MS::kSuccess;
	inValuesH.jumpToElement(0);
	MDataHandle eHandle = inValuesH.inputValue(&stats).child(inValue);
	MArrayDataHandle eArrayHandle(eHandle, &stats);
	unsigned eCount = eArrayHandle.elementCount();
	Matrix di( inValCount, eCount );

	for( int i = 0; i < inValCount; i++) {
		inValuesH.jumpToElement(i);
		MDataHandle eHandle = inValuesH.inputValue(&stats).child(inValue);
		MArrayDataHandle eArrayHandle(eHandle, &stats);
		unsigned eCount = eArrayHandle.elementCount();
		for( int j = 0; j < eCount; j++) {
			eArrayHandle.jumpToElement(j);
			float val = eArrayHandle.inputValue(&stats).asFloat();
			di.setValue(i,j,val);
			//fprintf(stderr, "di[%u][%u] = %g\n",i,j,val );
		}
	}
	////////////////////////////////////////
	////////////////////////////////////////
	//Get Input Centers
	MArrayDataHandle inCentersH = data.inputArrayValue( inCenters, &stats );
	unsigned inCentCount = inCentersH.elementCount();
	if (inCentCount == 0)
		return MS::kSuccess;
	MFloatVectorArray inCentersA;
	for( int i = 0; i < inCentCount; i++) {
		inCentersH.jumpToElement(i);
		MDataHandle pointH = inCentersH.inputValue(&stats);
		inCentersA.append( pointH.asFloatVector() );
	}
	////////////////////////////////////////

	////////////////////////////////////////
	// Calculate epsilon
	MFloatVector edges( amax( xi ) - amin( xi ) );
	float edgePow = 1.0;
	for (int i = 0; i < 3; i++)
	{
		if (edges[i] != 0.0)
			edgePow = edgePow * edges[i];
	}
	epsilon = pow( edgePow/ N, 1.0/3.0 );
	////////////////////////////////////////
	//Calculate RBF!
	MFloatArray r( _euclidean_norm( xi, xi ) );
	MFloatArray A( _h_multiquadric( r ) ); //TODO---> change this so we can change function by attribute!!!!!
	Matrix Amat( xi.length(), xi.length() );
	int count = 0;
	for (int x = 0; x < xi.length(); x++)
	{
		for (int y = 0; y < xi.length(); y++)
		{
			Amat.setValue( x,y, A[count] );
			count +=1;
		}
	}
	std::vector< Matrix > nodes = linalg( Amat, di );
	
	MFloatArray rCenters( _euclidean_norm( inCentersA, xi ) );
	MFloatArray r2Centers( _h_multiquadric( rCenters ) );

	Matrix r2Mat( inCentersA.length(), xi.length() );
	count = 0;
	std::vector< Matrix > finalMatrixData; //Result
	for (int x = 0; x < inCentersA.length(); x++)
	{
		finalMatrixData.push_back( Matrix( 1, eCount ) ); //Create Base Matrices for final Result
		for (int y = 0; y < xi.length(); y++)
		{
			r2Mat.setValue( x, y, r2Centers[count] );
			count += 1;
		}
	}
	//Calculate Matrix per Node
	for (int i = 0; i < nodes.size(); i++)
	{
		Matrix tmpMat = r2Mat.mult( nodes[i] );
		for (int r = 0; r < tmpMat.mat.size(); r++)
		{
				finalMatrixData[r].mat[0][i] = tmpMat.mat[r][0];
		}

	}
	////////////////////////////////////////
	// Write Output :)
	for(int i = 0; i < finalMatrixData.size(); i++) {
            stats = wPlug.selectAncestorLogicalIndex( i, outValues );
            MDataHandle wHandle = wPlug.constructHandle(data);
            MArrayDataHandle arrayHandle(wHandle, &stats);
            MArrayDataBuilder arrayBuilder = arrayHandle.builder(&stats);
			for( int j = 0; j < finalMatrixData[i].mat[0].size(); j++) {
                MDataHandle handle = arrayBuilder.addElement(j,&stats);
				//fprintf(stderr, "[%u]di[%u][%u] = %g\n",i,0,j,finalMatrixData[i].mat[0][j] );
				handle.set(finalMatrixData[i].mat[0][j] );
				//handle.set(float( i+j ));
            }
            stats = arrayHandle.set(arrayBuilder);
            wPlug.setValue(wHandle);
            wPlug.destructHandle(wHandle);
        }
	return MS::kSuccess;
}

MFloatVector rbfSolver::amax( MFloatVectorArray x1 )
{
	float xmax = x1[0][0];
	float ymax = x1[0][1];
	float zmax = x1[0][2];
	for (int x = 0; x < x1.length(); x++)
	{
		if (xmax < x1[x][0])
			xmax = x1[x][0];
		if (ymax < x1[x][1])
			ymax = x1[x][1];
		if (zmax < x1[x][2])
			zmax = x1[x][2];
	}
	return MFloatVector( xmax, ymax, zmax );
}

MFloatVector rbfSolver::amin( MFloatVectorArray x1 )
{
	float xmin = x1[0][0];
	float ymin = x1[0][1];
	float zmin = x1[0][2];
	for (int x = 0; x < x1.length(); x++)
	{
		if (xmin > x1[x][0])
			xmin = x1[x][0];
		if (ymin > x1[x][1])
			ymin = x1[x][1];
		if (zmin > x1[x][2])
			zmin = x1[x][2];
	}
	return MFloatVector( xmin, ymin, zmin );
}

MFloatArray rbfSolver::_euclidean_norm( MFloatVectorArray x1, MFloatVectorArray x2 )
{
	MFloatArray res;
	for (int x = 0; x < x1.length(); x++)
	{
		for (int y = 0; y < x2.length(); y++)
		{
			res.append( (x1[x] - x2[y]).length() );
		}
	}
	return res;
}

MFloatArray rbfSolver::_h_gaussian( MFloatArray r )
{
	MFloatArray res;
	for (int ri = 0; ri < r.length(); ri++)
	{
		float re = (1.0/epsilon*r[ri]);
		res.append( exp( -re*re ) );
	}
	return res;
}

MFloatArray rbfSolver::_h_multiquadric( MFloatArray r )
{
	MFloatArray res;
	for (int ri = 0; ri < r.length(); ri++)
	{
		float re = (1.0/epsilon*r[ri]);
		res.append( sqrt( re*re ) + 1.0 );
	}
	return res;
}

MFloatArray rbfSolver::_h_linear( MFloatArray r )
{
	return r;
}

MFloatArray rbfSolver::_h_cubic( MFloatArray r )
{
	MFloatArray res;
	for (int ri = 0; ri < r.length(); ri++)
	{
		res.append( r[ri] * r[ri] * r[ri] );
	}
	return res;
}

MFloatArray rbfSolver::_h_quintic( MFloatArray r )
{
	MFloatArray res;
	for (int ri = 0; ri < r.length(); ri++)
	{
		res.append( r[ri] * r[ri] * r[ri] * r[ri] * r[ri] );
	}
	return res;
}

std::vector< Matrix > rbfSolver::linalg( Matrix A, Matrix di )
{
	std::vector< Matrix > nodes;
	Matrix Ainverted = A.invert();
	for (int d = 0; d < di.getRow(0).size(); d++)
	{
		Matrix diTmp( di.rowsCount, 1 );
		for (int a = 0; a < di.rowsCount; a++)
		{
			diTmp.setValue( a,0, di.getValue(a, d) );
		}
		nodes.push_back( Ainverted.mult( diTmp ) );
	}
	return nodes;
}

MStatus rbfSolver::initialize()
{
	MStatus stat;
	MFnNumericAttribute nAttr;
	MFnCompoundAttribute cmpAttr;

	//input Positions Array
	inPositions = nAttr.createPoint( "inPos","inPos");
	nAttr.setArray(true);
	nAttr.setConnectable(true);
	nAttr.setHidden(true);
	nAttr.setStorable(true);
	nAttr.setUsesArrayDataBuilder(true);

	stat = addAttribute( inPositions );
	if (!stat) { stat.perror("addAttribute inPositions"); return stat;}

	inValue = nAttr.create( "inValue", "inValue", MFnNumericData::kFloat );
	nAttr.setArray(true);
	nAttr.setKeyable(true);
	nAttr.setReadable(true);
	nAttr.setStorable(true);
	nAttr.setUsesArrayDataBuilder(true);
	/*
	stat = addAttribute( inValue );
	if (!stat) { stat.perror("addAttribute inValue"); return stat;}
	*/
	//input ND Values Array
	inValues = cmpAttr.create( "inValues", "inValues");
	cmpAttr.setArray(true);
	cmpAttr.addChild( inValue );
	cmpAttr.setReadable(true);
	cmpAttr.setStorable(true);
	cmpAttr.setUsesArrayDataBuilder(true);

	stat = addAttribute( inValues );
	if (!stat) { stat.perror("addAttribute inValues"); return stat;}

	//input Centers Array
	inCenters = nAttr.createPoint( "inCenter","inCenter");
	nAttr.setArray(true);
	nAttr.setConnectable(true);
	nAttr.setHidden(true);
	nAttr.setStorable(true);
	nAttr.setUsesArrayDataBuilder(true);

	stat = addAttribute( inCenters );
	if (!stat) { stat.perror("addAttribute inCenters"); return stat;}

	outValue = nAttr.create( "outValue", "outValue", MFnNumericData::kFloat );
	nAttr.setArray(true);
	nAttr.setReadable(true);
	nAttr.setHidden(true);
	nAttr.setStorable(false);
	nAttr.setUsesArrayDataBuilder(true);
	/*
	stat = addAttribute( outValue );
	if (!stat) { stat.perror("addAttribute outValue"); return stat;}
	*/
	//output ND Values Array
	outValues = cmpAttr.create( "outValues", "outValues");
	cmpAttr.setArray(true);
	cmpAttr.addChild( outValue );
	cmpAttr.setHidden(true);
	cmpAttr.setReadable(true);
	cmpAttr.setStorable(false);
	cmpAttr.setUsesArrayDataBuilder(true);

	stat = addAttribute( outValues );
	if (!stat) { stat.perror("addAttribute outValues"); return stat;}

	stat = attributeAffects( inPositions, outValues );
	if (!stat) { stat.perror("attributeAffects"); return stat;}
	stat = attributeAffects( inValues, outValues );
	if (!stat) { stat.perror("attributeAffects"); return stat;}
	stat = attributeAffects( inCenters, outValues );
	if (!stat) { stat.perror("attributeAffects"); return stat;}

	return MS::kSuccess;
}

void* rbfSolver::creator()
{
	return new rbfSolver();
}