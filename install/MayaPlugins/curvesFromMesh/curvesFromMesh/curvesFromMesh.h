
//
// Copyright (C) Ignacio Urruty
// 
// File: curvesFromMesh.h
//
// Dependency Graph Node: curvesFromMesh
//
// Author: Maya Plug-in Wizard 2.0
//

#include <maya/MPxNode.h>
#include <maya/MFnTypedAttribute.h>
#include <maya/MTypeId.h> 
#include <maya/MIntArray.h>
 
class curvesFromMesh : public MPxNode
{
public:
						curvesFromMesh();
	virtual				~curvesFromMesh(); 

	virtual MStatus		compute( const MPlug& plug, MDataBlock& data );

	static  void*		creator();
	static  MStatus		initialize();

public:

	// There needs to be a MObject handle declared for each attribute that
	// the node will have.  These handles are needed for getting and setting
	// the values later.
	//
	static  MObject		inMesh;		// Example input attribute
	static  MObject		outCurve;		// Example output attribute
	static	MObject		inWorldMatrixAttr;
	static	MObject		outRadius;
	static	MObject		outDistance;
	static	MObject		curvesAmount;
	// The typeid is a unique 32bit indentifier that describes this node.
	// It is used to save and retrieve nodes of this type from the binary
	// file format.  If it is not unique, it will cause file IO problems.
	//
	static	MTypeId		id;

};

