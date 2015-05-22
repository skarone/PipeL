#ifndef _meshOpFty
#define _meshOpFty

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

//
// ***************************************************************************
//
// Overview:
//
//		The meshOp factory implements the actual meshOperation operation. 
//		It takes in three parameters:
//
//			1) A polygonal mesh
//			2) An array of component IDs
//          3) A mesh operation identifier
//
// Please refer to MFnMeshOperations to get more information on the different 
// mesh operations.
//

#include "polyModifierFty.h"

// General Includes
//
#include <maya/MObject.h>
#include <maya/MIntArray.h>
#include <maya/MString.h>
#include <maya/MItMeshEdge.h>
#include <maya/MItMeshVertex.h>

class MFnMesh;

enum MeshOperation
{
	kSubdivideEdges = 0,
	kSubdivideFaces = 1,
	kExtrudeEdges = 2,
	kExtrudeFaces = 3,
	kCollapseEdges = 4,
	kCollapseFaces = 5,
	kDuplicateFaces = 6,
	kExtractFaces = 7,
	kSplitLightning = 8,
	kChamferVertex = 9,
	
	// Number of valid operations
	kMeshOperationCount = 10
};

class meshOpFty : public polyModifierFty
{

public:
				meshOpFty();
	virtual		~meshOpFty();

	// Modifiers
	//
	void		setMesh( MObject& mesh );
	void		setComponentList( MObject& componentList );
	void		setComponentIDs( MIntArray& componentIDs );
	void		setMeshOperation( MeshOperation operationType );
	void		setHoleData(float radius, float distance, bool outerRing, float outerRingValue, int outRingsCount, bool createHole );

	// Returns the type of component expected by a given mesh operation
	//
	static MFn::Type getExpectedComponentType( MeshOperation operationType );

	// polyModifierFty inherited methods
	//
	MStatus		doIt();

private:
	// Mesh Node - Note: We only make use of this MObject during a single 
	//					 call of the meshOperation plugin. It is never 
	//					 maintained and used between calls to the plugin as 
	//					 the MObject handle could be invalidated between 
	//                   calls to the plugin.
	//
	MObject		fMesh;

	// Selected Components and Operation to execute
	//
	MIntArray		fComponentIDs;
	MeshOperation	fOperationType;
	MObject			fComponentList;
	float			fRadius;
	float			fDistance;
	bool			bOuterRing;
	float			fOuterRingValue;
	int				iOutRingsCount;
	bool			bCreateHole;

	MStatus doLightningSplit(MFnMesh& meshFn);
	MStatus doHoleVertex(MFnMesh& meshFn);
	void createChamfer(MFnMesh &meshFn, MItMeshVertex &vIt, int vertexIndex, float offset );
	void extrudeHole(MFnMesh &meshFn, MItMeshVertex &vIt);
	void makeHole(MFnMesh &meshFn, MItMeshVertex &vIt, int vertex);
	void scaleHole(MFnMesh &meshFn, MItMeshVertex &vIt, int vertex);

	float getNormalizedFactorOfEdge( MItMeshEdge& itEdge,int edge, float distance, int originVertex );

};

#endif
