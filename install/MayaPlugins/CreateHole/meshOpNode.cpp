//-
// ==========================================================================
// Copyright 1995,2006,2008 Autodesk, Inc. All rights reserved.
//
// Use of this software is subject to the terms of the Autodesk
// license agreement provided at the time of installation or download,
// or which otherwise accompanies this software in either electronic
// or hard copy form.
// ==========================================================================
//+

#include "meshOpNode.h"

// Function Sets
//
#include <maya/MFnTypedAttribute.h>
#include <maya/MFnNumericAttribute.h>
#include <maya/MFnMeshData.h>
#include <maya/MFnComponentListData.h>
#include <maya/MFnSingleIndexedComponent.h>
#include <maya/MFnEnumAttribute.h>

// General Includes
//
#include <maya/MGlobal.h>
#include <maya/MPlug.h>
#include <maya/MDataBlock.h>
#include <maya/MDataHandle.h>
#include <maya/MIOStream.h>

// Macros
//
#define MCheckStatus(status,message)	\
	if( MStatus::kSuccess != status ) {	\
		cerr << message << "\n";		\
		return status;					\
	}


// Unique Node TypeId
MTypeId     meshOpNode::id( 0x00085000 );

// Node attributes
// (in addition to inMesh and outMesh defined by polyModifierNode)
//
MObject     meshOpNode::cpList;
MObject     meshOpNode::opType;
MObject     meshOpNode::distance;
MObject     meshOpNode::radius;
MObject		meshOpNode::outRing;
MObject		meshOpNode::outRingValue;
MObject		meshOpNode::outRingsCount;
MObject		meshOpNode::createHole;
MObject		meshOpNode::innerRadius;
MObject		meshOpNode::additionalEdges;
MObject		meshOpNode::innerRingsCount;
MObject		meshOpNode::extrudeRingsCount;
MObject		meshOpNode::rotationAngle;
MObject		meshOpNode::flatCap;
meshOpNode::meshOpNode()
{}

meshOpNode::~meshOpNode()
{}

MStatus meshOpNode::compute( const MPlug& plug, MDataBlock& data )
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
	MStatus status = MS::kSuccess;
 
	MDataHandle stateData = data.outputValue( state, &status );
	MCheckStatus( status, "ERROR getting state" );

	// Check for the HasNoEffect/PassThrough flag on the node.
	//
	// (stateData is an enumeration standard in all depend nodes)
	// 
	// (0 = Normal)
	// (1 = HasNoEffect/PassThrough)
	// (2 = Blocking)
	// ...
	//
	if( stateData.asShort() == 1 )
	{
		MDataHandle inputData = data.inputValue( inMesh, &status );
		MCheckStatus(status,"ERROR getting inMesh");

		MDataHandle outputData = data.outputValue( outMesh, &status );
		MCheckStatus(status,"ERROR getting outMesh");

		// Simply redirect the inMesh to the outMesh for the PassThrough effect
		//
		outputData.set(inputData.asMesh());
	}
	else
	{
		// Check which output attribute we have been asked to 
		// compute. If this node doesn't know how to compute it, 
		// we must return MS::kUnknownParameter
		// 
		if (plug == outMesh)
		{
			MDataHandle inputData = data.inputValue( inMesh, &status );
			MCheckStatus(status,"ERROR getting inMesh");

			MDataHandle outputData = data.outputValue( outMesh, &status );
			MCheckStatus(status,"ERROR getting outMesh"); 

			// Now, we get the value of the component list and the operation
			// type and use it to perform the mesh operation on this mesh
			//
			MDataHandle inputIDs = data.inputValue( cpList, &status);
			MCheckStatus(status,"ERROR getting componentList"); 
			
			MDataHandle opTypeData = data.inputValue( opType, &status);
			MCheckStatus(status,"ERROR getting opType"); 

			MDataHandle additionalEdgesData = data.inputValue( additionalEdges, &status);
			MCheckStatus(status,"ERROR getting outRing"); 
			bool qAdditionalEdges = additionalEdgesData.asBool();

			MDataHandle innerRadiusData = data.inputValue( innerRadius, &status);
			MCheckStatus(status,"ERROR getting distance"); 
			float qInnerRadius = innerRadiusData.asFloat();
			
			MDataHandle flatCapData = data.inputValue( flatCap, &status);
			MCheckStatus(status,"ERROR getting distance"); 
			float qFlatCap = flatCapData.asFloat();

			MDataHandle distanceData = data.inputValue( distance, &status);
			MCheckStatus(status,"ERROR getting distance"); 
			float qDistance = distanceData.asFloat();

			MDataHandle radiusData = data.inputValue( radius, &status);
			MCheckStatus(status,"ERROR getting radius"); 
			float qRadius = radiusData.asFloat();

			
			MDataHandle rotationData = data.inputValue( rotationAngle, &status);
			MCheckStatus(status,"ERROR getting radius"); 
			float qRotation = rotationData.asFloat();

			MDataHandle createHoleData = data.inputValue( createHole, &status);
			MCheckStatus(status,"ERROR getting outRing"); 
			bool qCreateHole = createHoleData.asBool();

			MDataHandle outRingData = data.inputValue( outRing, &status);
			MCheckStatus(status,"ERROR getting outRing"); 
			float qOutRing = outRingData.asBool();

			MDataHandle outRingValueData = data.inputValue( outRingValue, &status);
			MCheckStatus(status,"ERROR getting outRingValue"); 
			float qOutRingValue = outRingValueData.asFloat();

			
			MDataHandle extrudeRingsCountData = data.inputValue( extrudeRingsCount, &status);
			MCheckStatus(status,"ERROR getting outRingsCount"); 
			int qExtrudeRingsCount = extrudeRingsCountData.asInt();

			MDataHandle innerRingsCountData = data.inputValue( innerRingsCount, &status);
			MCheckStatus(status,"ERROR getting outRingsCount"); 
			int qInnerRignsCount = innerRingsCountData.asInt();

			MDataHandle outRingsCountData = data.inputValue( outRingsCount, &status);
			MCheckStatus(status,"ERROR getting outRingsCount"); 
			int qOutRingsCount = outRingsCountData.asInt();
			// Copy the inMesh to the outMesh, so you can
			// perform operations directly on outMesh
			//
			outputData.set(inputData.asMesh());
			MObject mesh = outputData.asMesh();

			// Retrieve the ID list from the component list.
			//
			// Note, we use a component list to store the components
			// because it is more compact memory wise. (ie. comp[81:85]
			// is smaller than comp[81], comp[82],...,comp[85])
			//
			MObject compList = inputIDs.data();
			MFnComponentListData compListFn( compList );

			// Get what operation is requested and 
			// what type of component is expected for this operation.
			MeshOperation operationType = (MeshOperation) opTypeData.asShort();
			MFn::Type componentType =
				meshOpFty::getExpectedComponentType(operationType);

			unsigned i;
			int j;
			MIntArray cpIds;

			for( i = 0; i < compListFn.length(); i++ )
			{
				MObject comp = compListFn[i];
				if( comp.apiType() == componentType )
				{
					MFnSingleIndexedComponent siComp( comp );
					for( j = 0; j < siComp.elementCount(); j++ )
						cpIds.append( siComp.element(j) );
				}
			}

			// Set the mesh object and component List on the factory
			//
			fmeshOpFactory.setMesh( mesh );
			fmeshOpFactory.setComponentList( compList );
			fmeshOpFactory.setComponentIDs( cpIds );
			fmeshOpFactory.setMeshOperation( operationType );
			fmeshOpFactory.setHoleData( qRadius, qDistance, qOutRing, qOutRingValue, qOutRingsCount, qCreateHole, qInnerRadius, qAdditionalEdges, qInnerRignsCount, qExtrudeRingsCount, qRotation, qFlatCap );

			// Now, perform the meshOp
			//
			status = fmeshOpFactory.doIt();

			// Mark the output mesh as clean
			//
			outputData.setClean();
		}
		else
		{
			status = MS::kUnknownParameter;
		}
	}

	return status;
}

void* meshOpNode::creator()
//
//	Description:
//		this method exists to give Maya a way to create new objects
//      of this type. 
//
//	Return Value:
//		a new object of this type
//
{
	return new meshOpNode();
}

MStatus meshOpNode::initialize()
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
	MStatus				status;

	MFnTypedAttribute attrFn;
	MFnEnumAttribute enumFn;
	MFnNumericAttribute nAttr;

	cpList = attrFn.create("inputComponents", "ics",
		MFnComponentListData::kComponentList);
	attrFn.setStorable(true);	// To be stored during file-save

	opType = enumFn.create("operationType", "oprt", 0, &status);
	enumFn.addField("subd_edges", 0);
	enumFn.addField("subd_faces", 1);
	enumFn.addField("extr_edges", 2);
	enumFn.addField("extr_faces", 3);
	enumFn.addField("collapse_edges", 4);
	enumFn.addField("collapse_faces", 5);
	enumFn.addField("dup_faces", 6);
	enumFn.addField("extract_faces", 7);
	enumFn.addField("split_lighting", 8);
	enumFn.addField("hole_vertex", 9);
	enumFn.setHidden(false);
	enumFn.setKeyable(true);
	enumFn.setStorable(true);	// To be stored during file-save

	flatCap = nAttr.create("flatCap", "fc",MFnNumericData::kFloat, 1.0, &status);
	nAttr.setMin( 0.0 );
	nAttr.setMax( 1.0 );
	nAttr.setHidden(false);
	nAttr.setKeyable(true);
	nAttr.setStorable(true);	// To be stored during file-save

	innerRadius = nAttr.create("innerRadius", "ir",MFnNumericData::kFloat, 1.0, &status);
	nAttr.setMin( 0.0 );
	nAttr.setHidden(false);
	nAttr.setKeyable(true);
	nAttr.setStorable(true);	// To be stored during file-save

	distance = nAttr.create("distance", "dist",MFnNumericData::kFloat, 0.5, &status);
	nAttr.setHidden(false);
	nAttr.setKeyable(true);
	nAttr.setStorable(true);	// To be stored during file-save

	radius = nAttr.create("radius", "rad",MFnNumericData::kFloat, 0.5, &status);
	nAttr.setMin( 0.0 );
	nAttr.setHidden(false);
	nAttr.setKeyable(true);
	nAttr.setStorable(true);	// To be stored during file-save

	rotationAngle = nAttr.create("rotation", "rot",MFnNumericData::kFloat, 0.0, &status);
	nAttr.setHidden(false);
	nAttr.setKeyable(true);
	nAttr.setStorable(true);	// To be stored during file-save

	additionalEdges = nAttr.create("additionalEdges", "ae",MFnNumericData::kBoolean, true, &status);
	nAttr.setHidden(false);
	nAttr.setKeyable(true);
	nAttr.setStorable(true);	

	createHole = nAttr.create("createHole", "ch",MFnNumericData::kBoolean, true, &status);
	nAttr.setHidden(false);
	nAttr.setKeyable(true);
	nAttr.setStorable(true);	

	outRing = nAttr.create("outRing", "or",MFnNumericData::kBoolean, true, &status);
	nAttr.setHidden(false);
	nAttr.setKeyable(true);
	nAttr.setStorable(true);	// To be stored during file-save

	outRingValue = nAttr.create("outRingValue", "ov",MFnNumericData::kFloat, 0.5, &status);
	nAttr.setMin( 0.0 );
	nAttr.setHidden(false);
	nAttr.setKeyable(true);
	nAttr.setStorable(true);	// To be stored during file-save

	innerRingsCount = nAttr.create("innerRingsCount", "ic",MFnNumericData::kInt, 0, &status);
	nAttr.setMin(0);
	nAttr.setHidden(false);
	nAttr.setKeyable(true);
	nAttr.setStorable(true);	// To be stored during file-save

	extrudeRingsCount = nAttr.create("extrudeRingsCount", "ec",MFnNumericData::kInt, 3, &status);
	nAttr.setMin(0);
	nAttr.setHidden(false);
	nAttr.setKeyable(true);
	nAttr.setStorable(true);	// To be stored during file-save

	outRingsCount = nAttr.create("outRingsCount", "oc",MFnNumericData::kInt, 1, &status);
	nAttr.setMin(0);
	nAttr.setHidden(false);
	nAttr.setKeyable(true);
	nAttr.setStorable(true);	// To be stored during file-save

	inMesh = attrFn.create("inMesh", "im", MFnMeshData::kMesh);
	attrFn.setStorable(true);	// To be stored during file-save

	// Attribute is read-only because it is an output attribute
	//
	outMesh = attrFn.create("outMesh", "om", MFnMeshData::kMesh);
	attrFn.setStorable(false);
	attrFn.setWritable(false);

	// Add the attributes we have created to the node
	//
	
	status = addAttribute( additionalEdges );
		if (!status)
		{
			status.perror("addAttribute");
			return status;
		}
	status = addAttribute( createHole );
		if (!status)
		{
			status.perror("addAttribute");
			return status;
		}

	status = addAttribute( rotationAngle );
		if (!status)
		{
			status.perror("addAttribute");
			return status;
		}
	status = addAttribute( outRing );
		if (!status)
		{
			status.perror("addAttribute");
			return status;
		}
	status = addAttribute( outRingValue );
		if (!status)
		{
			status.perror("addAttribute");
			return status;
		}
	status = addAttribute( outRingsCount );
		if (!status)
		{
			status.perror("addAttribute");
			return status;
		}
	status = addAttribute( extrudeRingsCount );
		if (!status)
		{
			status.perror("addAttribute");
			return status;
		}
	status = addAttribute( innerRadius );
		if (!status)
		{
			status.perror("addAttribute");
			return status;
		}
	status = addAttribute( flatCap );
		if (!status)
		{
			status.perror("addAttribute");
			return status;
		}
	status = addAttribute( innerRingsCount );
		if (!status)
		{
			status.perror("addAttribute");
			return status;
		}
	status = addAttribute( distance );
		if (!status)
		{
			status.perror("addAttribute");
			return status;
		}
	status = addAttribute( radius );
		if (!status)
		{
			status.perror("addAttribute");
			return status;
		}
	status = addAttribute( cpList );
		if (!status)
		{
			status.perror("addAttribute");
			return status;
		}
	status = addAttribute( opType );
		if (!status)
		{
			status.perror("addAttribute");
			return status;
		}
	status = addAttribute( inMesh );
		if (!status)
		{
			status.perror("addAttribute");
			return status;
		}
	status = addAttribute( outMesh);
		if (!status)
		{
			status.perror("addAttribute");
			return status;
		}

	// Set up a dependency between the input and the output.  This will cause
	// the output to be marked dirty when the input changes.  The output will
	// then be recomputed the next time the value of the output is requested.
	//
	status = attributeAffects( flatCap, outMesh );
		if (!status)
		{
			status.perror("attributeAffects");
			return status;
		}
	status = attributeAffects( rotationAngle, outMesh );
		if (!status)
		{
			status.perror("attributeAffects");
			return status;
		}
	status = attributeAffects( extrudeRingsCount, outMesh );
		if (!status)
		{
			status.perror("attributeAffects");
			return status;
		}
	status = attributeAffects( innerRingsCount, outMesh );
		if (!status)
		{
			status.perror("attributeAffects");
			return status;
		}
	status = attributeAffects( additionalEdges, outMesh );
		if (!status)
		{
			status.perror("attributeAffects");
			return status;
		}
	status = attributeAffects( innerRadius, outMesh );
		if (!status)
		{
			status.perror("attributeAffects");
			return status;
		}
	status = attributeAffects( createHole, outMesh );
		if (!status)
		{
			status.perror("attributeAffects");
			return status;
		}
	status = attributeAffects( outRing, outMesh );
		if (!status)
		{
			status.perror("attributeAffects");
			return status;
		}
	status = attributeAffects( outRingValue, outMesh );
		if (!status)
		{
			status.perror("attributeAffects");
			return status;
		}
	status = attributeAffects( outRingsCount, outMesh );
		if (!status)
		{
			status.perror("attributeAffects");
			return status;
		}
	status = attributeAffects( radius, outMesh );
		if (!status)
		{
			status.perror("attributeAffects");
			return status;
		}
	status = attributeAffects( distance, outMesh );
		if (!status)
		{
			status.perror("attributeAffects");
			return status;
		}
	status = attributeAffects( inMesh, outMesh );
		if (!status)
		{
			status.perror("attributeAffects");
			return status;
		}

	status = attributeAffects( cpList, outMesh );
		if (!status)
		{
			status.perror("attributeAffects");
			return status;
		}

	status = attributeAffects( opType, outMesh );
		if (!status)
		{
			status.perror("attributeAffects");
			return status;
		}

	return MS::kSuccess;

}
