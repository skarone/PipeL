#include "rbfSolver.h"
#include "matrix.h"

#include <maya/MFnNumericAttribute.h>
#include <maya/MFnCompoundAttribute.h>
#include <maya/MFloatVectorArray.h>
#include <maya/MStatus.h>

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
    MPlug wPlug(thisNode, inValues);
	
	////////////////////////////////////////
	//Get Input Positions
	MArrayDataHandle inPositionsH = data.inputArrayValue( inPositions, &stats );
	unsigned inPosCount = inPositionsH.elementCount();
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
	inValuesH.jumpToElement(0);
	MDataHandle eHandle = inValuesH.inputValue(&stats).child(inValue);
	MArrayDataHandle eArrayHandle(eHandle, &stats);
	unsigned eCount = eArrayHandle.elementCount();
	Matrix m( inValCount, eCount );

	for( int i = 0; i < inValCount; i++) {
		inValuesH.jumpToElement(i);
		MDataHandle eHandle = inValuesH.inputValue(&stats).child(inValue);
		MArrayDataHandle eArrayHandle(eHandle, &stats);
		unsigned eCount = eArrayHandle.elementCount();
		for( int j = 0; j < eCount; j++) {
			eArrayHandle.jumpToElement(j);
			float val = eArrayHandle.inputValue(&stats).asFloat();
			m.setValue(i,j,val);
			fprintf(stderr, "Val = %g\n",m.getValue(i,j));
		}
	}
	////////////////////////////////////////
	////////////////////////////////////////
	//Get Input Centers
	MArrayDataHandle inCentersH = data.inputArrayValue( inCenters, &stats );
	unsigned inCentCount = inCentersH.elementCount();
	MFloatVectorArray inCentersA;
	for( int i = 0; i < inCentCount; i++) {
		inCentersH.jumpToElement(i);
		MDataHandle pointH = inCentersH.inputValue(&stats);
		inCentersA.append( pointH.asFloatVector() );
	}
	////////////////////////////////////////
	return MS::kSuccess;
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

	inValue = nAttr.create( "inValue", "inValue", MFnNumericData::kFloat );
	nAttr.setArray(true);
	nAttr.setKeyable(true);
	nAttr.setReadable(true);
	nAttr.setStorable(true);
	nAttr.setUsesArrayDataBuilder(true);


	//input ND Values Array
	inValues = cmpAttr.create( "inValues", "inValues");
	cmpAttr.setArray(true);
	cmpAttr.addChild( inValue );
	cmpAttr.setStorable(true);
	cmpAttr.setUsesArrayDataBuilder(true);

	//input Centers Array
	inCenters = nAttr.createPoint( "inCenter","inCenter");
	nAttr.setArray(true);
	nAttr.setConnectable(true);
	nAttr.setHidden(true);
	nAttr.setStorable(true);
	nAttr.setUsesArrayDataBuilder(true);

	outValue = nAttr.create( "outValue", "outValue", MFnNumericData::kFloat );
	nAttr.setArray(true);
	nAttr.setReadable(true);
	nAttr.setStorable(false);
	nAttr.setUsesArrayDataBuilder(true);

	//output ND Values Array
	outValues = cmpAttr.create( "outValues", "outValues");
	cmpAttr.setArray(true);
	cmpAttr.addChild( outValue );
	cmpAttr.setStorable(false);
	cmpAttr.setUsesArrayDataBuilder(true);

	stat = addAttribute( inPositions );
	if (!stat) { stat.perror("addAttribute inPositions"); return stat;}
	stat = addAttribute( inValues );
	if (!stat) { stat.perror("addAttribute inValues"); return stat;}
	stat = addAttribute( inCenters );
	if (!stat) { stat.perror("addAttribute inCenters"); return stat;}
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