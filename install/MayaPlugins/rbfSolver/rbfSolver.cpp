#include "rbfSolver.h"
//#include "matrix.h"
#include <maya/MFnNumericAttribute.h>
#include <maya/MFnCompoundAttribute.h>
#include <maya/MFnEnumAttribute.h>
#include <maya/MFnTypedAttribute.h>
#include <maya/MStatus.h>
#include <maya/MArrayDataBuilder.h>
#include <maya/MFnMesh.h>
#include <maya/MDagPath.h>


MObject rbfSolver::inPositions;
MObject rbfSolver::inMesh;
MObject rbfSolver::inValue;
MObject rbfSolver::function;
MObject rbfSolver::smooth;
MObject rbfSolver::customEpsilon;
MObject rbfSolver::autoEpsilon;
MObject rbfSolver::inValues;
MObject rbfSolver::inCenters;
MObject rbfSolver::outValue;
MObject rbfSolver::outValues;
MObject rbfSolver::outputMesh;

MTypeId rbfSolver::id( 0x00347 );

rbfSolver::rbfSolver(){};
rbfSolver::~rbfSolver(){};


MStatus rbfSolver::compute( const MPlug& plug, MDataBlock& data )
{
	MStatus stats;
    MObject thisNode = thisMObject();
    MPlug wPlug(thisNode, outValue);
	
	////////////////////////////////////////
	// Get function
	MDataHandle typeHandle = data.inputValue( function );
    short func_type = typeHandle.asShort();
	////////////////////////////////////////
	// Get auto_Epsilon
	MDataHandle auto_epsiHandle = data.inputValue( autoEpsilon );
	bool auto_epsi = auto_epsiHandle.asBool();
	////////////////////////////////////////
	// Get Epsilon
	MDataHandle epsiHandle = data.inputValue( customEpsilon );
	float epsi = epsiHandle.asFloat();
	////////////////////////////////////////
	// Get smooth
	MDataHandle smooHandle = data.inputValue( smooth );
	float smoot = smooHandle.asFloat();
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
	MFloatVectorArray inCentersA;
	////////////////////////////////////////
	// Get mesh
	MDataHandle inputData = data.inputValue( inMesh, &stats );
    MObject surf = inputData.asMesh();
	MPlug surfPlug( thisNode, inMesh );
	bool useMesh = false;
	MFnMesh surfFn;
	MFnDagNode dagNodeFn(surf);
	MDagPath        fNodePath;
	dagNodeFn.getPath(fNodePath);
    if ( surfPlug.isConnected() ) {
		useMesh = true;
		surfFn.setObject( surf );
		surfFn.clearColors();
		for (int i = 0; i < surfFn.numVertices(); i++)
		{
			MPoint point;
			surfFn.getPoint( i, point, MSpace::kWorld );
			inCentersA.append( MFloatVector( point.x, point.y, point.z ) );
		}
	}else{
		////////////////////////////////////////
		//Get Input Centers
		MArrayDataHandle inCentersH = data.inputArrayValue( inCenters, &stats );
		unsigned inCentCount = inCentersH.elementCount();
		if (inCentCount == 0)
			return MS::kSuccess;
		for( int i = 0; i < inCentCount; i++) {
			inCentersH.jumpToElement(i);
			MDataHandle pointH = inCentersH.inputValue(&stats);
			inCentersA.append( pointH.asFloatVector() );
		}
	}
	////////////////////////////////////////

	////////////////////////////////////////
	// Calculate epsilon
	if (auto_epsi)
	{
		MFloatVector edges( amax( xi ) - amin( xi ) );
		float edgePow = 1.0;
		for (int i = 0; i < 3; i++)
		{
			if (edges[i] != 0.0)
				edgePow = edgePow * edges[i];
		}
		epsilon = pow( edgePow/ N, 1.0/3.0 );
	}else{
		epsilon = epsi;
	}
	////////////////////////////////////////
	//Calculate RBF!
	MFloatArray r( _euclidean_norm( xi, xi ) );
	MFloatArray A( method( func_type, r ) );
	Matrix Amat( xi.length(), xi.length() );
	int count = 0;
	for (int x = 0; x < xi.length(); x++)
	{
		for (int y = 0; y < xi.length(); y++)
		{
			float val = A[count];
			if (x == y)
				val -= smoot;
			Amat.setValue( x,y, val );
			count +=1;
		}
	}
	std::vector< Matrix > nodes = linalg( Amat, di );
	
	MFloatArray rCenters( _euclidean_norm( inCentersA, xi ) );
	MFloatArray r2Centers( method( func_type, rCenters ) );

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
			MColor rbgSphere(0.0,0.0,0.0,1.0);
			for( int j = 0; j < finalMatrixData[i].mat[0].size(); j++) {
                MDataHandle handle = arrayBuilder.addElement(j,&stats);
				//fprintf(stderr, "[%u]di[%u][%u] = %g\n",i,0,j,finalMatrixData[i].mat[0][j] );
				handle.set(finalMatrixData[i].mat[0][j] );
				if (useMesh)
					rbgSphere[j] = finalMatrixData[i].mat[0][j];
				//handle.set(float( i+j ));
            }
			if (useMesh){
				surfFn.setVertexColor( rbgSphere, i );
			}
            stats = arrayHandle.set(arrayBuilder);
            wPlug.setValue(wHandle);
            wPlug.destructHandle(wHandle);
    }
	if (useMesh)
		surfFn.updateSurface();
	MDataHandle outMeshDH = data.outputValue(outputMesh);
	
	outMeshDH.setMObject( surf );

	stats = data.setClean(outputMesh); 
	return MS::kSuccess;
}


MFloatArray rbfSolver::method( short funcType, MFloatArray r )
{
	MFloatArray res;
	switch( funcType )
	{
		case 0:
			res = _h_multiquadric( r );
			break;
		case 1:
			res = _h_gaussian( r );
			break;
		case 2:
			res = _h_linear( r );
			break;
		case 3:
			res = _h_cubic( r );
			break;
		case 4:
			res = _h_quintic( r );
			break;
	}
	return res;
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

MFloatArray rbfSolver::_euclidean_norm( MFloatVectorArray x1, MFloatVectorArray x2)
{
	MFloatArray res;
	for (int x = 0; x < x1.length(); x++)
	{
		for (int y = 0; y < x2.length(); y++)
		{
			float len = (x1[x] - x2[y]).length();
			res.append( len );
		}
	}
	return res;
}

MFloatArray rbfSolver::_h_gaussian( MFloatArray r )
{
	MFloatArray res;
	for (int ri = 0; ri < r.length(); ri++)
	{
		//res.append( exp( 1.0/r[ri] * r[ri] * -epsilon ) );
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
		//res.append( sqrt( r[ri] * r[ri] + epsilon * epsilon ) );
		float re = (1.0/epsilon*r[ri]);
		res.append( sqrt( ( re*re ) + 1.0 ) );
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
		res.append( (r[ri] * r[ri] * r[ri] ));
	}
	return res;
}

MFloatArray rbfSolver::_h_quintic( MFloatArray r )
{
	MFloatArray res;
	for (int ri = 0; ri < r.length(); ri++)
	{
		res.append( (r[ri] * r[ri] * r[ri] * r[ri] * r[ri] ));
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
	MFnEnumAttribute     enumAttr;
	MFnTypedAttribute   typedAttr;

	//input Function
	function = enumAttr.create( "function", "function", 0, &stat );
	stat = enumAttr.addField( "multiquadric", 0 );
	stat = enumAttr.addField( "gaussian", 1 );
	stat = enumAttr.addField( "linear", 2 );
	stat = enumAttr.addField( "cubic", 3 );
	stat = enumAttr.addField( "quintic", 4 );
	enumAttr.setStorable(true);
	enumAttr.setReadable(true);

	stat = addAttribute( function );
	if (!stat) { stat.perror("addAttribute function"); return stat;}

	autoEpsilon = nAttr.create( "auto_epsilon", "auto_epsilon", MFnNumericData::kBoolean, true );
	nAttr.setKeyable(true);
	nAttr.setReadable(true);
	nAttr.setStorable(true);

	stat = addAttribute( autoEpsilon );
	if (!stat) { stat.perror("addAttribute autoEpsilon"); return stat;}

	customEpsilon = nAttr.create( "epsilon", "epsilon", MFnNumericData::kFloat, 0.0 );
	nAttr.setKeyable(true);
	nAttr.setReadable(true);
	nAttr.setStorable(true);

	stat = addAttribute( customEpsilon );
	if (!stat) { stat.perror("addAttribute customEpsilon"); return stat;}

	smooth = nAttr.create( "smooth", "smooth", MFnNumericData::kFloat, 0.0 );
	nAttr.setKeyable(true);
	nAttr.setReadable(true);
	nAttr.setStorable(true);

	stat = addAttribute( smooth );
	if (!stat) { stat.perror("addAttribute smooth"); return stat;}

	//in mesh, just to draw colors :)
	inMesh = typedAttr.create( "inputMesh", "im", MFnData::kMesh, NULL );
	typedAttr.setHidden(true);

	stat = addAttribute( inMesh );
	if (!stat) { stat.perror("addAttribute inMesh"); return stat;}

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

	outputMesh = typedAttr.create( "outputMesh", "out", MFnData::kMesh ); 

	stat = addAttribute( outputMesh );
	if (!stat) { stat.perror("addAttribute outputMesh"); return stat;}

	stat = attributeAffects( function, outValues );
	if (!stat) { stat.perror("attributeAffects"); return stat;}
	stat = attributeAffects( inMesh, outValues );
	if (!stat) { stat.perror("attributeAffects"); return stat;}
	stat = attributeAffects( autoEpsilon, outValues );
	if (!stat) { stat.perror("attributeAffects"); return stat;}
	stat = attributeAffects( customEpsilon, outValues );
	if (!stat) { stat.perror("attributeAffects"); return stat;}
	stat = attributeAffects( smooth, outValues );
	if (!stat) { stat.perror("attributeAffects"); return stat;}
	stat = attributeAffects( inPositions, outValues );
	if (!stat) { stat.perror("attributeAffects"); return stat;}
	stat = attributeAffects( inValues, outValues );
	if (!stat) { stat.perror("attributeAffects"); return stat;}
	stat = attributeAffects( inCenters, outValues );
	if (!stat) { stat.perror("attributeAffects"); return stat;}

	stat = attributeAffects( function, outputMesh );
	if (!stat) { stat.perror("attributeAffects"); return stat;}
	stat = attributeAffects( inMesh, outputMesh );
	if (!stat) { stat.perror("attributeAffects"); return stat;}
	stat = attributeAffects( autoEpsilon, outputMesh );
	if (!stat) { stat.perror("attributeAffects"); return stat;}
	stat = attributeAffects( customEpsilon, outputMesh );
	if (!stat) { stat.perror("attributeAffects"); return stat;}
	stat = attributeAffects( smooth, outputMesh );
	if (!stat) { stat.perror("attributeAffects"); return stat;}
	stat = attributeAffects( inPositions, outputMesh );
	if (!stat) { stat.perror("attributeAffects"); return stat;}
	stat = attributeAffects( inValues, outputMesh );
	if (!stat) { stat.perror("attributeAffects"); return stat;}
	stat = attributeAffects( inCenters, outputMesh );
	if (!stat) { stat.perror("attributeAffects"); return stat;}
	return MS::kSuccess;
}

void* rbfSolver::creator()
{
	return new rbfSolver();
}