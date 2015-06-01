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

#include "meshOpFty.h"

// General Includes
//
#include <maya/MGlobal.h>
#include <maya/MIOStream.h>
#include <maya/MFloatPointArray.h>
#include <maya/MDagPath.h>
#include <maya/MString.h>

// Function Sets
//
#include <maya/MFnMesh.h>

// Iterators
//
#include <maya/MItMeshPolygon.h>
#include <maya/MItMeshEdge.h>
#include <maya/MItMeshVertex.h>
#include <maya/MUintArray.h>

#define CHECK_STATUS(st) if ((st) != MS::kSuccess) { break; }

MStatus meshOpFty::doIt()
//
//	Description:
//		Performs the operation on the selected mesh and components
//
{
	MStatus status;
	unsigned int i, j;

	// Get access to the mesh's function set
	//
	MFnMesh meshFn(fMesh);

	// The division count argument is used in many of the operations
	// to execute the operation multiple subsequent times. For example,
	// with a division count of 2 in subdivide face, the given faces will be
	// divide once and then the resulting inner faces will be divided again.
	//
	int divisionCount = 2;

	MFloatVector translation;
	if (fOperationType == kExtrudeEdges
		|| fOperationType == kExtrudeFaces
		|| fOperationType == kDuplicateFaces
		|| fOperationType == kExtractFaces)
	{
		// The translation vector is used for the extrude, extract and 
		// duplicate operations to move the result to a new position. For 
		// example, if you extrude an edge on a mesh without a subsequent 
		// translation, the extruded edge will be on at the position of the 
		// orignal edge and the created faces will have no area.
		// 
		// Here, we provide a translation that is in the same direction as the
		// average normal of the given components.
		//
		MFn::Type componentType = getExpectedComponentType(fOperationType);
		MIntArray adjacentVertexList;
		switch (componentType)
		{
		case MFn::kMeshEdgeComponent:
			for (i = 0; i < fComponentIDs.length(); ++i)
			{
				int2 vertices;
				meshFn.getEdgeVertices(fComponentIDs[i], vertices);
				adjacentVertexList.append(vertices[0]);
				adjacentVertexList.append(vertices[1]);
			}
			break;

		case MFn::kMeshPolygonComponent:
			for (i = 0; i < fComponentIDs.length(); ++i)
			{
				MIntArray vertices;
				meshFn.getPolygonVertices(fComponentIDs[i], vertices);
				for (j = 0; j < vertices.length(); ++j)
					adjacentVertexList.append(vertices[j]);
			}
			break;
		default:	
			break;
		}
		MVector averageNormal(0, 0, 0);
		for (i = 0; i < adjacentVertexList.length(); ++i)
		{
			MVector vertexNormal;
			meshFn.getVertexNormal(adjacentVertexList[i], vertexNormal,
				MSpace::kWorld);
			averageNormal += vertexNormal;
		}
		if (averageNormal.length() < 0.001)
			averageNormal = MVector(0.0, 1.0, 0.0);
		else averageNormal.normalize();
		translation = averageNormal;
	}

	// When doing an extrude operation, there is a choice of extrude the
	// faces/edges individually or together. If extrudeTogether is true and 
	// multiple adjacent components are selected, they will be extruded as if
	// it were one more complex component.
	//
	// The following variable sets that option.
	//
	bool extrudeTogether = true;

	// Execute the requested operation
	//
	switch (fOperationType)
	{
	case kSubdivideEdges: {
		status = meshFn.subdivideEdges(fComponentIDs, divisionCount);
		CHECK_STATUS(status);
		break; }

	case kSubdivideFaces: {
		status = meshFn.subdivideFaces(fComponentIDs, divisionCount);
		CHECK_STATUS(status);
		break; }

	case kExtrudeEdges: {
		status = meshFn.extrudeEdges(fComponentIDs, divisionCount,
			&translation, extrudeTogether);
		CHECK_STATUS(status);
		break; }

	case kExtrudeFaces: {
		status = meshFn.extrudeFaces(fComponentIDs, divisionCount,
			&translation, extrudeTogether);
		CHECK_STATUS(status);
		break; }

	case kCollapseEdges: {
		status = meshFn.collapseEdges(fComponentIDs);
		CHECK_STATUS(status);
		break; }

	case kCollapseFaces: {
		status = meshFn.collapseFaces(fComponentIDs);
		CHECK_STATUS(status);
		break; }

	case kDuplicateFaces: {
		status = meshFn.duplicateFaces(fComponentIDs, &translation);
		CHECK_STATUS(status);
		break; }

	case kExtractFaces: {
		status = meshFn.extractFaces(fComponentIDs, &translation);
		CHECK_STATUS(status);
		break; }

	case kSplitLightning: {
		status = doLightningSplit(meshFn);
		CHECK_STATUS(status);
		break; }

	case kChamferVertex:{
		status = doHoleVertex(meshFn);
		CHECK_STATUS(status);
		break; }

	default:
		status = MS::kFailure;
		break;
	}

	return status;
}

MStatus meshOpFty::doHoleVertex(MFnMesh& meshFn)
{
	
	MIntArray facesToDelete;
	for (int i = 0; i < fComponentIDs.length(); i++)
	{
		//create additional edges
		MItMeshVertex vIt(fMesh);	
		if (bAdditionalEdges)
			createAdditionalEdges( meshFn, vIt, fComponentIDs[i] );
		//create Outer Loop
		if (bOuterRing){
			createChamfer(meshFn, vIt, fComponentIDs[i], 1.0f + fOuterRingValue);
			//reorder verteces to make perfect circle!
			orderForCircle( meshFn, vIt, fComponentIDs[i] );
			for (int out = iOutRingsCount; out > 0; out-- )
			{
				//MGlobal::displayInfo(  MString("Offset: ") + (1.0 + (fOuterRingValue/(iOutRingsCount+1) * out ) ));
				createChamfer(meshFn, vIt, fComponentIDs[i], (1.0f + (fOuterRingValue/(iOutRingsCount+1) * out) ));
			}
		}
		//Create Main Ring
		createChamfer(meshFn, vIt, fComponentIDs[i], 1.0f);
		
		if(!bOuterRing)
			orderForCircle( meshFn, vIt, fComponentIDs[i] );
			
		//create Inner Ring
		if (fDistance != 0.0){
			createChamfer(meshFn, vIt, fComponentIDs[i], 0.5f);
			//Extrude Face
			extrudeHole( meshFn , vIt, fComponentIDs[i] );
			//Scale Hole
			scaleHole( meshFn, vIt, fComponentIDs[i] );
			//Subdivide Extrude
			subdivideExtrude( meshFn, vIt, fComponentIDs[i] );
		}
		//Create Inner rings for cap
		if (!bCreateHole){
			for (int in = iInnerRingsCount; in > 0; in-- )
			{
				//MGlobal::displayInfo(  MString("Offset: ") + (1.0 + (fOuterRingValue/(innerRingsCount+1) * out ) ));
				createChamfer(meshFn, vIt, fComponentIDs[i], ( fInnerRadius/(iInnerRingsCount+1.0) * in) );
			}
		}

	}

	//Make Hole
	if (bCreateHole){
			for (int i = 0; i < fComponentIDs.length(); i++)
			{
				MItMeshVertex vIt(fMesh);	
				MIntArray currentFacesToDelete;
				currentFacesToDelete = getFacesToDelete( meshFn, vIt, fComponentIDs[i] );
				for (int f = 0; f < currentFacesToDelete.length(); f++ ){
					facesToDelete.append( currentFacesToDelete[f] );
				}
			}
			BubbleSort(facesToDelete);
			makeHole(meshFn, facesToDelete);
	}
	
	return MS::kSuccess;

}

MFloatVector meshOpFty::getAverageNormal(MItMeshVertex &vIt, int vertex)
{
	MFloatVector averageNormal(0, 0, 0);
	MVectorArray normals;
	int prevIndex;
	vIt.setIndex( vertex, prevIndex);
	vIt.getNormals(normals);
	for ( int n = 0; n < normals.length(); n++)
	{
		averageNormal += normals[n];
	}
	averageNormal.normalize();
	return averageNormal;
}

void meshOpFty::orderForCircle(MFnMesh &meshFn, MItMeshVertex &vIt, int vertex)
{
	int prevIndex;
	vIt.setIndex( vertex, prevIndex );
	MIntArray connVerteces, connFaces;
	vIt.getConnectedVertices( connVerteces );
	vIt.getConnectedFaces( connFaces );
	MPoint v0 = vIt.position();
	MFloatVector axisToRotate = getAverageNormal(vIt, vertex);
	vIt.setIndex( connVerteces[0], prevIndex );
	MVector v1 = vIt.position();
	MVector v0v1( v1 - v0 );
	float radius = v0v1.length();
	float anglePerVert = (-360.0 / connVerteces.length() ) ;
	anglePerVert = anglePerVert * 0.0174532925; //angle in radians
	float baseAngle = anglePerVert;
	for( int v = 0; v < connVerteces.length(); v++ )
	{
		MVector vFinal;
		if ( v == 0 )
			vFinal = rotatePointAroundVector( v0v1,  axisToRotate,  (fRotationAngle * 0.0174532925) );
		else
			vFinal = rotatePointAroundVector( v0v1,  axisToRotate,  baseAngle + (fRotationAngle * 0.0174532925) );
		vFinal = vFinal + v0;
		//hitFacePtr = OpenMaya.MScriptUtil().asIntPtr()
		//accelParams  = None
		MFloatPoint	hitPoint;
		meshFn.closestIntersection( MFloatPoint( vFinal ),
									axisToRotate,
									NULL,
									NULL,
									false,
									MSpace::kWorld,
									1e+99,
									true,
									NULL,
									hitPoint,
									NULL,
									NULL,
									NULL,
									NULL,
									NULL );
		vIt.setIndex( connVerteces[v], prevIndex );
		vIt.setPosition( MPoint( hitPoint ) );
		if ( v != 0 )
			baseAngle += anglePerVert;
	}
}

MVector meshOpFty::rotatePointAroundVector(MVector input, MVector axis, float angle )
{
	float ux = axis[0]*input[0];
	float uy = axis[0]*input[1];
	float uz = axis[0]*input[2];
	float vx = axis[1]*input[0];
	float vy = axis[1]*input[1];
	float vz = axis[1]*input[2];
	float wx = axis[2]*input[0];
	float wy = axis[2]*input[1];
	float wz = axis[2]*input[2];
	float sa = sin(angle);
	float ca = cos(angle);
	float x = axis[0]*(ux+vy+wz)+(input[0]*(axis[1]*axis[1]+axis[2]*axis[2])-axis[0]*(vy+wz))*ca+(-wy+vz)*sa;
	float y = axis[1]*(ux+vy+wz)+(input[1]*(axis[0]*axis[0]+axis[2]*axis[2])-axis[1]*(ux+wz))*ca+(wx-uz)*sa;
	float z = axis[2]*(ux+vy+wz)+(input[2]*(axis[0]*axis[0]+axis[1]*axis[1])-axis[2]*(ux+vy))*ca+(-vx+uy)*sa;
	return MVector(x, y , z);
}

void meshOpFty::subdivideExtrude(MFnMesh &meshFn, MItMeshVertex &vIt, int vertex )
{
	MIntArray connFaces;
	int prevIndex;
	float edgeFactor;
	int counter = 0;
	for( int ex = iExtrudeRingsCount; ex > 0; ex-- ){
		vIt.setIndex(vertex, prevIndex);
		vIt.getConnectedFaces( connFaces );
		MIntArray  ringEdges, faceEdges;
		MItMeshPolygon pIt(fMesh);
		//get edges the that are connected to the faces of the main vertex but not connected to him
		for (int f = 0; f < connFaces.length(); f++)
		{
			MIntArray edges;
			pIt.setIndex( connFaces[f], prevIndex );
			pIt.getEdges( edges );
			int edge;
			for (int e = 0; e < edges.length(); e++)
			{
				bool edgeMatch = false;
				if (vIt.connectedToEdge( edges[e]))
					edgeMatch = true;
				if (!edgeMatch)
					faceEdges.append( edges[e] );
					//MGlobal::displayInfo(  MString("Border Edge: ") + edges[e] );
					//break;
			}
		}
		BubbleSort( faceEdges );
		MItMeshEdge eIt(fMesh);
		for( int e = 0; e < faceEdges.length(); e++ )
		{
			eIt.setIndex( faceEdges[e], prevIndex );
			int v0 = eIt.index(0);
			vIt.setIndex( v0, prevIndex );
			MIntArray edges;
			vIt.getConnectedEdges( edges );
			for( int ev = 0; ev < edges.length(); ev++ )
			{
				eIt.setIndex( edges[ev], prevIndex );
				bool edgeMatch = false;
				for( int f = 0; f < connFaces.length(); f++ )
				{
					if (eIt.connectedToFace(connFaces[f]))
					{
						edgeMatch = true;
						break;
					}
				}
				if (!edgeMatch)
					ringEdges.append( edges[ev] );
			}

		}
		//create splits
		MIntArray placements;
		MIntArray edgeIDs;
		MFloatArray edgeFactors;
		MFloatPointArray internalPoints;
		float factorE0;
		for (int e = 0; e < ringEdges.length(); e++)
		{
			float factor;
			factor = ( 1.0/(iExtrudeRingsCount - counter + 1));
			eIt.setIndex( ringEdges[e], prevIndex );
			int v0 = eIt.index(0);
			vIt.setIndex( v0, prevIndex );
			MIntArray connVerteces;
			vIt.getConnectedVertices(connVerteces);
			//check if this v is the one closest to main vertex
			bool vertClosestMainVertex = false;
			for (int v = 0; v < connVerteces.length(); v++)
			{
				if (vertex == connVerteces[v])
					vertClosestMainVertex = true;
			}
			if( vertClosestMainVertex )
				factor = 1.0 - factor;
			if (e == 0)
				factorE0 = factor;
			placements.append( (int) MFnMesh::kOnEdge );
			edgeFactors.append(  factor );
			edgeIDs.append( ringEdges[e] );
		}

		placements.append( (int) MFnMesh::kOnEdge );
		edgeFactors.append( factorE0 );
		//MGlobal::displayInfo(  MString("Factor: ") + factorE0);
		edgeIDs.append( ringEdges[0] );
		meshFn.split(placements, edgeIDs, edgeFactors, internalPoints );
		counter++;
	}

}

MIntArray meshOpFty::getFacesToDelete(MFnMesh &meshFn, MItMeshVertex &vIt, int vertex )
{	
	MIntArray faceToDelete;
	int prevIndex;
	vIt.setIndex(vertex, prevIndex);
	vIt.getConnectedFaces( faceToDelete );
	return faceToDelete;
}

void meshOpFty::BubbleSort(MIntArray &a)
{
     int i, j, temp;
	 for (i = 0; i < (a.length() - 1); ++i)
     {
          for (j = 0; j < a.length() - 1 - i; ++j )
          {
               if (a[j] > a[j+1])
               {
                    temp = a[j+1];
                    a[j+1] = a[j];
                    a[j] = temp;
               }
          }
     }

}

void meshOpFty::createAdditionalEdges(MFnMesh &meshFn, MItMeshVertex &vIt, int vertex )
{
	int prevIndex;
	vIt.setIndex(vertex, prevIndex);
	MIntArray connVertecies, connFaces, nonConnVertices, edges;
	vIt.getConnectedEdges( edges );
	vIt.getConnectedVertices( connVertecies );
	vIt.getConnectedFaces( connFaces );
	MItMeshPolygon pIt( fMesh );
	for ( int f = 0; f < connFaces.length(); f++ )
	{
		pIt.setIndex( connFaces[f], prevIndex );
		MIntArray vertFaces;
		pIt.getVertices( vertFaces );
		for (int fv = 0; fv < vertFaces.length(); fv ++)
		{
			bool vertMatch = false;
			if ( vertFaces[fv] == vertex )
				vertMatch = true;
			else{

				for (int v = 0; v < connVertecies.length(); v++)
				{
					if ( vertFaces[fv] == connVertecies[v] )
					{
						vertMatch = true; 
					}
				}
			}
			if (!vertMatch)
				nonConnVertices.append( vertFaces[fv] );
		}
	}
	for (int v = 0; v < nonConnVertices.length(); v++)
	{
		vIt.setIndex(nonConnVertices[v], prevIndex);
		MIntArray nonConnEdges, placements, edgeIDs;
		MFloatPointArray internalPoints;
		MFloatArray edgeFactors;
		vIt.getConnectedEdges( nonConnEdges );
		placements.append( (int) MFnMesh::kOnEdge );
		edgeFactors.append( 1.0 );
		edgeIDs.append( nonConnEdges[0] );
		placements.append( (int) MFnMesh::kOnEdge );
		edgeFactors.append( 0.0 );
		edgeIDs.append( edges[0] );
		placements.append( (int) MFnMesh::kOnEdge );
		edgeFactors.append( 0.0 );
		edgeIDs.append( nonConnEdges[0] );
		meshFn.split( placements, edgeIDs, edgeFactors, internalPoints);
		//MGlobal::displayInfo(  MString("Vertices in Face: ") + nonConnVertices[v] );
	}
}

void meshOpFty::scaleHole(MFnMesh &meshFn, MItMeshVertex &vIt, int vertex)
{
	int prevIndex;
	vIt.setIndex(vertex, prevIndex);
	MIntArray vertexes;
	vIt.getConnectedVertices( vertexes );
	MPoint vPos( vIt.position() );
	for (int v = 0; v < vertexes.length(); v++)
	{
		vIt.setIndex(vertexes[v], prevIndex);
		MVector vPos2( vIt.position() );
		MVector vFinal( vPos2 - vPos );
		
		//vFinal.normalize();
		MVector vfi(  vPos + vFinal.normal() *fRadius* fInnerRadius  );
		vIt.setPosition( vfi );
	}

}


void meshOpFty::makeHole(MFnMesh &meshFn, MIntArray faces)
{

	for (int f = faces.length(); f > 0; f--)
	{
		meshFn.deleteFace( faces[f-1] );
		meshFn.updateSurface();
	}
}



void meshOpFty::extrudeHole(MFnMesh &meshFn, MItMeshVertex &vIt, int vertex)
{
	MFloatVector averageNormal;
	averageNormal = getAverageNormal( vIt, vertex );

	//averageNormal = averageNormal * fDistance;

	int prevIndex;
	vIt.setIndex( vertex, prevIndex );
	MIntArray vertexes;
	//vIt.getConnectedFaces(faces);
	//meshFn.extrudeFaces(faces, 1, &averageNormal, true);
	vIt.getConnectedVertices( vertexes );
	//IF make cap flat
	//project al vectors with the normal and see wichone is the longuest
	MVector point0( vIt.position() );
	vIt.setPosition( vIt.position() + MPoint( (averageNormal ) * fDistance ) );
	for (int v = 0; v < vertexes.length(); v++)
	{
		vIt.setIndex( vertexes[v], prevIndex );
		MVector pointN( point0 - MVector( vIt.position()) );
		MVector projNtoNorm(( (pointN * averageNormal) / averageNormal.length() * averageNormal.length() ) * averageNormal );
		vIt.setPosition( vIt.position() + MPoint(projNtoNorm * fFlatCap) +  MPoint( (averageNormal ) * fDistance ) );
	}
}

void meshOpFty::createChamfer(MFnMesh &meshFn, MItMeshVertex &vIt, int vertexIndex, float offset )
{
		MIntArray placements;
		MIntArray edgeIDs;
		MFloatArray edgeFactors;
		MFloatPointArray internalPoints;
		MIntArray edges;
		int prevIndex;
		MItMeshEdge itEdge(fMesh, MObject::kNullObj );
		
		vIt.setIndex( vertexIndex, prevIndex );
		vIt.getConnectedEdges( edges );	
		placements.append( (int) MFnMesh::kOnEdge );
		edgeIDs.append( edges[0] );
		float edgeFactor0 = getNormalizedFactorOfEdge( itEdge, edges[0], (fRadius * offset), vertexIndex);
		edgeFactors.append( edgeFactor0 );
		//MFloatPoint point1(0.0f,0.0f,0.0f);
		//internalPoints.append( point1 );
		//MGlobal::displayInfo( MString("Edges: " )+ edges[0] );
	
		for (int e = 1; e < edges.length(); e++)
		{
			//MGlobal::displayInfo( MString("Edges: " )+ edges[e] );
			placements.append( (int) MFnMesh::kOnEdge );
			edgeIDs.append( edges[e] );
			edgeFactors.append(getNormalizedFactorOfEdge( itEdge, edges[e], (fRadius* offset), vertexIndex ) );
			//internalPoints.append( point1 );
		}
		
		placements.append( (int) MFnMesh::kOnEdge );
		edgeIDs.append( edges[0] );
		edgeFactors.append( edgeFactor0 );
		//internalPoints.append( point1 );
		
		meshFn.split(placements, edgeIDs, edgeFactors, internalPoints);
}

float meshOpFty::getNormalizedFactorOfEdge( MItMeshEdge& itEdge,int edge, float distance, int originVertex )
{
	MPoint edge0vert0, edge0vert1;
	double length;
	int prevIndex;
	itEdge.setIndex( edge, prevIndex );
	itEdge.getLength( length );
	float factor = distance / length;
	if (factor > 1.0)
		factor = 1.0;
	if (itEdge.index( 1 ) == originVertex)
		factor = 1 - factor;
	/*
	MGlobal::displayInfo( MString("distance: " )+ distance );
	MGlobal::displayInfo( MString("length: " )+ length );
	MGlobal::displayInfo( MString("factor: " )+ factor );
	*/
	return factor;
	
}


MStatus meshOpFty::doLightningSplit(MFnMesh& meshFn)
//
//	Description:
//		Performs the kSplitLightning operation on the selected mesh
//      and components. It may not split all the selected components.
//
{
	unsigned int i, j;

	// These are the input arrays to the split function. The following
	// algorithm fills them in with the arguments for a continuous
	// split that goes through some of the selected faces.
	//
	MIntArray placements;
	MIntArray edgeIDs;
	MFloatArray edgeFactors;
	MFloatPointArray internalPoints;
	
	// The following array is going to be used to determine which faces
	// have been split. Since the split function can only split faces
	// which are adjacent to the earlier face, we may not split
	// all the faces
	//
	bool* faceTouched = new bool[fComponentIDs.length()];
	for (i = 0; i < fComponentIDs.length(); ++i)
		faceTouched[i] = false;
	
	// We need a starting point. For this example, the first face in
	// the component list is picked. Also get a polygon iterator
	// to this face.
	// 
	MItMeshPolygon itPoly(fMesh);
	for (; !itPoly.isDone(); itPoly.next())
	{
		if (fComponentIDs[0] == (int)itPoly.index()) break;
	}
	if (itPoly.isDone())
	{
		// Should never happen.
		//
		delete [] faceTouched;
		return MS::kFailure;
	}
	
	// In this example, edge0 is called the starting edge and
	// edge1 is called the destination edge. This algorithm will split
	// each face from the starting edge to the destination edge
	// while going through two inner points inside each face.
	//
	int edge0, edge1;
	MPoint innerVert0, innerVert1;
	int nextFaceIndex = 0;
	
	// We need a starting edge. For this example, the first edge in the
	// edge list is used.
	//
	MIntArray edgeList;
	itPoly.getEdges(edgeList);
	edge0 = edgeList[0];
	
	bool done = false;
	while (!done)
	{
		// Set this face as touched so that we don't try to split it twice
		//
		faceTouched[nextFaceIndex] = true;
		
		// Get the current face's center. It is used later in the
		// algorithm to calculate inner vertices.
		//
		MPoint faceCenter = itPoly.center();
			
		// Iterate through the connected faces to find an untouched,
		// selected face and get the ID of the shared edge. That face
		// will become the next face to be split.
		//
		MIntArray faceList;
		itPoly.getConnectedFaces(faceList);
		nextFaceIndex = -1;
		for (i = 0; i < fComponentIDs.length(); ++i)
		{
			for (j = 0; j < faceList.length(); ++j)
			{
				if (fComponentIDs[i] == faceList[j] && !faceTouched[i])
				{
					nextFaceIndex = i;
					break;
				}
			}
			if (nextFaceIndex != -1) break;
		}
		
		if (nextFaceIndex == -1)
		{
			// There is no selected and untouched face adjacent to this
			// face, so this algorithm is done. Pick the first edge that
			// is not the starting edge as the destination edge.
			//
			done = true;
			edge1 = -1;
			for (i = 0; i < edgeList.length(); ++i)
			{
				if (edgeList[i] != edge0)
				{
					edge1 = edgeList[i];
					break;
				}
			}
			if (edge1 == -1)
			{
				// This should not happen, since there should be more than
				// one edge for each face
				//
				delete [] faceTouched;
				return MS::kFailure;
			}
		}
		else
		{
			// The next step is to find out which edge is shared between
			// the two faces and use it as the destination edge. To do
			// that, we need to iterate through the faces and get the
			// next face's list of edges.
			//
			itPoly.reset();
			for (; !itPoly.isDone(); itPoly.next())
			{
				if (fComponentIDs[nextFaceIndex] == (int)itPoly.index()) break;
			}
			if (itPoly.isDone()) 
			{
				// Should never happen.
				//
				delete [] faceTouched;
				return MS::kFailure;
			}
			
			// Look for a common edge ID in the two faces edge lists
			//
			MIntArray nextFaceEdgeList;
			itPoly.getEdges(nextFaceEdgeList);
			edge1 = -1;
			for (i = 0; i < edgeList.length(); ++i)
			{
				for (j = 0; j < nextFaceEdgeList.length(); ++j)
				{
					if (edgeList[i] == nextFaceEdgeList[j])
					{
						edge1 = edgeList[i];
						break;
					}
				}
				if (edge1 != -1) break;
			}
			if (edge1 == -1)
			{
				// Should never happen.
				//
				delete [] faceTouched;
				return MS::kFailure;
			}
			
			// Save the edge list for the next iteration
			//
			edgeList = nextFaceEdgeList;
		}
		
		// Calculate the two inner points that the split will go through.
		// For this example, the midpoints between the center and the two
		// farthest vertices of the edges are used.
		//
		// Find the 3D positions of the edges' vertices
		//
		MPoint edge0vert0, edge0vert1, edge1vert0, edge1vert1;
		MItMeshEdge itEdge(fMesh, MObject::kNullObj );
		for (; !itEdge.isDone(); itEdge.next())
		{
			if (itEdge.index() == edge0)
			{
				edge0vert0 = itEdge.point(0);
				edge0vert1 = itEdge.point(1);
			}
			if (itEdge.index() == edge1)
			{
				edge1vert0 = itEdge.point(0);
				edge1vert1 = itEdge.point(1);
			}
		}
		
		// Figure out which are the farthest from each other
		//
		double distMax = edge0vert0.distanceTo(edge1vert0);
		MPoint max0, max1;
		max0 = edge0vert0;
		max1 = edge1vert0;
		double newDist = edge0vert1.distanceTo(edge1vert0);
		if (newDist > distMax)
		{
			max0 = edge0vert1;
			max1 = edge1vert0;
			distMax = newDist;
		}
		newDist = edge0vert0.distanceTo(edge1vert1);
		if (newDist > distMax)
		{
			max0 = edge0vert0;
			max1 = edge1vert1;
			distMax = newDist;
		}
		newDist = edge0vert1.distanceTo(edge1vert1);
		if (newDist > distMax)
		{
			max0 = edge0vert1;
			max1 = edge1vert1;
		}
		
		// Calculate the two inner points
		//
		innerVert0 = (faceCenter + max0) / 2.0;
		innerVert1 = (faceCenter + max1) / 2.0;
		
		// Add this split's information to the input arrays. If this is
		// the last split, also add the destination edge's split information.
		//
		placements.append((int) MFnMesh::kOnEdge);
		placements.append((int) MFnMesh::kInternalPoint);
		placements.append((int) MFnMesh::kInternalPoint);
		if (done) placements.append((int) MFnMesh::kOnEdge);
		
		edgeIDs.append(edge0);
		if (done) edgeIDs.append(edge1);
		
		edgeFactors.append(0.5f);
		if (done) edgeFactors.append(0.5f);
		
		MFloatPoint point1((float)innerVert0[0], (float)innerVert0[1],
			(float)innerVert0[2], (float)innerVert0[3]);
		MFloatPoint point2((float)innerVert1[0], (float)innerVert1[1],
			(float)innerVert1[2], (float)innerVert1[3]);
		internalPoints.append(point1);
		internalPoints.append(point2);
		
		// For the next iteration, the current destination
		// edge becomes the start edge.
		//
		edge0 = edge1;
	}

	// Release the dynamically-allocated memory and do the actual split
	//
	delete [] faceTouched;
	return meshFn.split(placements, edgeIDs, edgeFactors, internalPoints);
}
