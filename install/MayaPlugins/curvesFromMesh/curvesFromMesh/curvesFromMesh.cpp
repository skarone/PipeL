//
// Copyright (C) Ignacio Urruty
// 
// File: curvesFromMesh.cpp
//
// Dependency Graph Node: curvesFromMesh
//
// Author: Maya Plug-in Wizard 2.0
//
/*
mc.loadPlugin( "C:/Users/iurruty/Documents/Visual Studio 2010/Projects/sk_dentPuller/sk_dentPuller/Release_2011/sk_dentPuller.mll" );


mc.file( "C:/Users/iurruty/Documents/maya/projects/default/scenes/test_DentCPlus.ma",f=True,options= "v=0" ,typ="mayaAscii",o=True);

mc.select('pPlane1');
mc.deformer(type='sk_dentPuller')
*/

#include "curvesFromMesh.h"
#include <vector>
#include <iostream>
#include <maya/MPlug.h>
#include <maya/MDataBlock.h>
#include <maya/MDataHandle.h>
#include <maya/MItMeshVertex.h>
#include <maya/MFnNurbsCurve.h>
#include <maya/MFnNurbsCurveData.h>
#include <maya/MPointArray.h>
#include <maya/MGlobal.h>
#include <maya/MPoint.h>
#include <maya/MString.h>
#include <maya/MFnMatrixAttribute.h>
#include <maya/MFnMatrixData.h>
#include <maya/MMatrix.h>
#include <maya/MFnNumericAttribute.h>
#include <maya/MArrayDataBuilder.h>
// You MUST change this to a unique value!!!  The id is a 32bit value used
// to identify this type of node in the binary file format.  
//
//#error change the following to a unique value and then erase this line 
MTypeId     curvesFromMesh::id( 0x00358 );
void removeEquals(MIntArray &Array1, MIntArray &Array2);
// Example attributes
// 
MObject     curvesFromMesh::inMesh;        
MObject     curvesFromMesh::outCurve;  
MObject     curvesFromMesh::inWorldMatrixAttr;
MObject     curvesFromMesh::outRadius;
MObject     curvesFromMesh::outDistance;
MObject		curvesFromMesh::curvesAmount;
curvesFromMesh::curvesFromMesh() {}
curvesFromMesh::~curvesFromMesh() {}

MStatus curvesFromMesh::compute( const MPlug& plug, MDataBlock& data )
//
//	Description:
//		This method computes the value of the given output plug based
//		on the values of the input attributes.
//
//	Arguments:
//		plug - the plug to compute
//		data - object that provides access to the attributes for this node
//
{
	MStatus returnStatus;
 
	// Check which output attribute we have been asked to compute.  If this 
	// node doesn't know how to compute it, we must return 
	// MS::kUnknownParameter.
	// 
	if( plug == outCurve || plug == outRadius || plug == outDistance)
	{
		// Get a handle to the input attribute that we will need for the
		// computation.  If the value is being supplied via a connection 
		// in the dependency graph, then this call will cause all upstream  
		// connections to be evaluated so that the correct value is supplied.
		// 
		MDataHandle inputData = data.inputValue( inMesh, &returnStatus );
		MArrayDataHandle outRadHandle = data.outputArrayValue( outRadius );
		MArrayDataBuilder radBuilder = outRadHandle.builder();

		MArrayDataHandle outDisHandle = data.outputArrayValue( outDistance );
		MArrayDataBuilder disBuilder = outDisHandle.builder();

		if( returnStatus != MS::kSuccess )
			MGlobal::displayError( "Node curvesFromMesh cannot get value\n" );
		else
		{
			
			//get Matrix
			
			MObject thisNode = thisMObject();
			MPlug plugpMat( thisNode, inWorldMatrixAttr);	// find our attribute plug on ourselves
			MObject pMat ;
			plugpMat.getValue( pMat );		// For matrix plugs, have to get as MObject
			MFnMatrixData fnPMat( pMat );	// Then take that to a MfnMatrix Data.    
			MMatrix pMmatrix = fnPMat.matrix();
			/*
			//DEBUGUIN
			MString msg ("Matrix: ");
			msg = msg + pMmatrix[3][0] + " " + pMmatrix[3][1]+ " " + pMmatrix[3][2];
			//msg = msg + controlVertices[i][0] + " " + controlVertices[i][1] + " " + controlVertices[i][2];
			MGlobal::displayInfo(msg);
			*/
			MObject InputMesh = inputData.asMesh();
			MItMeshVertex vertexIt(InputMesh);
			MPointArray controlVertices1,
						controlVertices2,
						controlVertices3,
						controlVertices4,
						controlVertices5;

			MDoubleArray knotSequences;
			MFnNurbsCurve HairCurveFn;
			MFnNurbsCurveData dataCreator;
			MObject outCurveData;
			outCurveData = dataCreator.create();
			MIntArray boundsRing;
			int vertCount = vertexIt.count();
			int RingsCount = int(vertCount/4.0);
			
			while(vertexIt.isDone() == false)
			{
				if (vertexIt.onBoundary())
					boundsRing.append(vertexIt.index());
				vertexIt.next();
			}
			vertexIt.reset();
			//create Rings
			std::vector<MIntArray> rings;
			rings.push_back(boundsRing);
			MIntArray UsedVerteces,umbVerteces;
			/*
			for (int ring = 0;ring < (RingsCount-1);ring++)
				rings.push_back(boundsRing);
			*/
			int Indptr;
			for (int ring = 0;ring < RingsCount;ring++)
			{
				MVector tempPoint (0.0,0.0,0.0);
				MIntArray umbVerticesOfRing;
				MVectorArray vertRingPos;
				MVector FirstVertex;
				for (int r = 0;r < (rings[ring].length());r++)//boundsRing = rings[ring=0]
				{	
					vertexIt.setIndex(rings[ring][r],Indptr);
					MVector vertexPos(vertexIt.position());
					if(r==0) FirstVertex = vertexPos;
					vertRingPos.append(vertexPos);
					tempPoint = tempPoint + vertexPos;
					UsedVerteces.append(rings[ring][r]);
					//get Umbrella verticies
					vertexIt.getConnectedVertices(umbVerteces);
					
					for (int umbV = 0;umbV < (umbVerteces.length());umbV++)
						umbVerticesOfRing.append(umbVerteces[umbV]);
				}
				//Clean UmbVertices to detect Ring
				removeEquals(umbVerticesOfRing,UsedVerteces);
				tempPoint = tempPoint/4.0;
				MVector radiusVec(tempPoint-FirstVertex);
				double radius = radiusVec.length();

				MPoint ring1Point ((vertRingPos[0]+tempPoint)/2.0);
				controlVertices2.append(ring1Point*pMmatrix);
				MPoint ring2Point ((vertRingPos[1]+tempPoint)/2.0);
				controlVertices3.append(ring2Point*pMmatrix);
				MPoint ring3Point ((vertRingPos[2]+tempPoint)/2.0);
				controlVertices4.append(ring3Point*pMmatrix);
				MPoint ring4Point ((vertRingPos[3]+tempPoint)/2.0);
				controlVertices5.append(ring4Point*pMmatrix);
				/*
				//DEBUGUIN
				MString msg ("Radius: ");
				msg = msg + radius;
				//msg = msg + controlVertices[i][0] + " " + controlVertices[i][1] + " " + controlVertices[i][2];
				MGlobal::displayInfo(msg);
				*/
				MDataHandle outRadHandle = radBuilder.addElement(ring);
				outRadHandle.setDouble(radius);

				MPoint finalPoint (tempPoint);
				finalPoint = finalPoint*pMmatrix;
				controlVertices1.append(finalPoint);
				rings.push_back( umbVerticesOfRing);
			}
			float knVal = 0.0;
			MDataHandle outDisFirstHandle = disBuilder.addElement(0);
			outDisFirstHandle.setDouble(0.0);				
			for (int i = 0;i < controlVertices1.length();i++)
			{
				if (i < 3)
					knotSequences.append( 0.0 );
				else if(i==(controlVertices1.length()-1))
				{
					knVal = knVal + 1.0;
					knotSequences.append( knVal );
					knotSequences.append( knVal );
					knotSequences.append( knVal );
				}
				else
				{
					knVal = knVal + 1.0;
					knotSequences.append( knVal );
				}
				if(i<controlVertices1.length()-1)
				{
					MVector vec1(controlVertices1[i]);
					MVector vec2(controlVertices1[i+1]);
					MVector finalVec(vec1-vec2);
					double dist = finalVec.length();
					MDataHandle outDisHandle = disBuilder.addElement(i+1);
					outDisHandle.setDouble(dist);
				}

			}
			
			//I need to compute the others 5 curves
			MArrayDataHandle outCurveHandle = data.outputArrayValue( outCurve );
			MArrayDataBuilder curvBuilder = outCurveHandle.builder();
			//OUTPUT CURVES
			MDataHandle OutCurve1Handle = curvBuilder.addElement(0);
			HairCurveFn.create(controlVertices1, knotSequences,3,MFnNurbsCurve::kOpen, false, false,outCurveData);
			OutCurve1Handle.set(outCurveData);

			MDataHandle OutCurve2Handle = curvBuilder.addElement(1);
			HairCurveFn.create(controlVertices2, knotSequences,3,MFnNurbsCurve::kOpen, false, false,outCurveData);
			OutCurve2Handle.set(outCurveData);

			MDataHandle OutCurve3Handle = curvBuilder.addElement(2);
			HairCurveFn.create(controlVertices3, knotSequences,3,MFnNurbsCurve::kOpen, false, false,outCurveData);
			OutCurve3Handle.set(outCurveData);

			MDataHandle OutCurve4Handle = curvBuilder.addElement(3);
			HairCurveFn.create(controlVertices4, knotSequences,3,MFnNurbsCurve::kOpen, false, false,outCurveData);
			OutCurve4Handle.set(outCurveData);

			MDataHandle OutCurve5Handle = curvBuilder.addElement(4);
			HairCurveFn.create(controlVertices5, knotSequences,3,MFnNurbsCurve::kOpen, false, false,outCurveData);
			OutCurve5Handle.set(outCurveData);

			data.setClean(outRadius);
			data.setClean(outDistance);
			data.setClean(plug);
		}
	} else {
		return MS::kUnknownParameter;
	}

	return MS::kSuccess;
}

void removeEquals(MIntArray &Array1, MIntArray &Array2)
{
	MIntArray itemsToRemove;
	for (int i=0;i<Array1.length();++i)
	{
		for (int j=0;j<Array2.length();++j)
		{
			if (Array1[i] == Array2[j])
			{
				//Array1.remove(i);
				itemsToRemove.append(i);
			}
		}
	}
	for (int r=(itemsToRemove.length()-1);r >= 0;r--)
	{
		Array1.remove(itemsToRemove[r]);
	}
}

void* curvesFromMesh::creator()
//
//	Description:
//		this method exists to give Maya a way to create new objects
//      of this type. 
//
//	Return Value:
//		a new object of this type
//
{
	return new curvesFromMesh();
}

MStatus curvesFromMesh::initialize()
//
//	Description:
//		This method is called to create and initialize all of the attributes
//      and attribute dependencies for this node type.  This is only called 
//		once when the node type is registered with Maya.
//
//	Return Values:
//		MS::kSuccess
//		MS::kFailure
//		
{
	// This sample creates a single input float attribute and a single
	// output float attribute.
	//

	MStatus				stat;
	MFnTypedAttribute   tAttr;
	MFnNumericAttribute nAttr;

	inMesh = tAttr.create( "inMesh", "inm", MFnData::kMesh);
	// Attribute will be written to files when this type of node is stored
 	tAttr.setHidden(true);

	curvesAmount = nAttr.create( "curvesCount", "cc", MFnNumericData::kInt );
	// Attribute is read-only because it is an output attribute
	nAttr.setWritable(true);
	// Attribute will not be written to files when this type of node is stored
	nAttr.setStorable(true);

	outCurve = tAttr.create( "outCurve", "ocr", MFnData::kNurbsCurve );
	// Attribute is read-only because it is an output attribute
	tAttr.setWritable(false);
	// Attribute will not be written to files when this type of node is stored
	tAttr.setStorable(false);
	tAttr.setArray(true);
	tAttr.setUsesArrayDataBuilder( true );

	MFnMatrixAttribute mAttr;
	inWorldMatrixAttr = mAttr.create("inWorldMatrix", "twM", MFnMatrixAttribute::kFloat);
	mAttr.setHidden(true);

	//radius array output
	outRadius = nAttr.create( "outRadius", "outr",MFnNumericData::kDouble);
	// Attribute is read-only because it is an output attribute
	nAttr.setWritable(false);
	// Attribute will not be written to files when this type of node is stored
	nAttr.setStorable(false);
	nAttr.setArray(true);
	nAttr.setUsesArrayDataBuilder( true );


	//Distance array output
	outDistance = nAttr.create( "outDistance", "outd",MFnNumericData::kDouble);
	// Attribute is read-only because it is an output attribute
	nAttr.setWritable(false);
	// Attribute will not be written to files when this type of node is stored
	nAttr.setStorable(false);
	nAttr.setArray(true);
	nAttr.setUsesArrayDataBuilder( true );
	// Add the attributes we have created to the node
	//
	stat = addAttribute( outDistance );
		if (!stat) { stat.perror("addAttribute"); return stat;}
	stat = addAttribute( outRadius );
		if (!stat) { stat.perror("addAttribute"); return stat;}
	stat = addAttribute( inWorldMatrixAttr );
		if (!stat) { stat.perror("addAttribute"); return stat;}
	stat = addAttribute( inMesh );
		if (!stat) { stat.perror("addAttribute"); return stat;}
	stat = addAttribute( outCurve );
		if (!stat) { stat.perror("addAttribute"); return stat;}

	// Set up a dependency between the input and the output.  This will cause
	// the output to be marked dirty when the input changes.  The output will
	// then be recomputed the next time the value of the output is requested.
	//
	stat = attributeAffects( inMesh, outCurve );
		if (!stat) { stat.perror("attributeAffects"); return stat;}

	stat = attributeAffects( inWorldMatrixAttr, outCurve );
		if (!stat) { stat.perror("attributeAffects"); return stat;}

	stat = attributeAffects( inMesh, outRadius );
		if (!stat) { stat.perror("attributeAffects"); return stat;}

	stat = attributeAffects( inMesh, outDistance );
		if (!stat) { stat.perror("attributeAffects"); return stat;}

	return MS::kSuccess;

}

