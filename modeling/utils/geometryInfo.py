# the OpenMaya module has many of the general Maya classes
# note that some Maya classes require extra modules to use which is noted in the API docs
import maya.OpenMaya as OpenMaya

def getInfoFromSelectedMesh():
	"""docstring for getInfoFromMesh"""
	# This shows how to use the MSelectionList and MGlobal class
	# Get the selection and create a selection list of all the nodes meshes
	selection = OpenMaya.MSelectionList()
	OpenMaya.MGlobal.getActiveSelectionList( selection );

	# Create an MItSelectionList class to iterate over the selection
	# Use the MFn class to as a filter to filter node types
	iter = OpenMaya.MItSelectionList ( selection, OpenMaya.MFn.kGeometric );

	# This uses build in functions of the MItSelectionList class to loop through the list of objects
	# Note this is not a basic array you must use its built in functions iterate on its objects
	# Iterate through selection
	while not iter.isDone():
		vertexList = []
		edgeList = []
		polytriVertsList = []
		polyList = []
		conpolyList = []
		# Get MDagPath from current iterated node
		dagPath = OpenMaya.MDagPath()
		iter.getDagPath( dagPath )
		# Get the selection as an MObject
		mObj = OpenMaya.MObject()
		iter.getDependNode( mObj )
		# This shows how to use the MItMeshPolygon class to work with meshes
		# Create an iterator for the polygons of the mesh
		iterPolys = OpenMaya.MItMeshPolygon( mObj )
		# Iterate through polys on current mesh
		while not iterPolys.isDone():
			# Get current polygons index
			polyList.append (iterPolys.index())	
			# Get current polygons vertices
			verts = OpenMaya.MIntArray()
			iterPolys.getVertices( verts )
			# Append the current polygons vertex indices
			for i in range( verts.length() ):
				vertexList.append (verts[i])
			# Get current polygons edges
			edges = OpenMaya.MIntArray()
			iterPolys.getEdges( edges )
			# Append the current polygons edge indices
			for i in range( edges.length() ):
				edgeList.append (edges[i])	
			# Get current polygons connected faces
			indexConFaces = OpenMaya.MIntArray()
			iterPolys.getConnectedFaces( indexConFaces )
			# Append the connected polygons indices
			for i in range( indexConFaces.length() ):
				conpolyList.append (indexConFaces[i])
			# Get current polygons triangles
			pntAry = OpenMaya.MPointArray()
			intAry = OpenMaya.MIntArray()
			space = OpenMaya.MSpace.kObject
			# Get the vertices and vertex positions of all the triangles in the current face's triangulation.
			iterPolys.getTriangles(pntAry, intAry, space)	
			# Append vertices that are part of the triangles
			for i in range( intAry.length() ):
				polytriVertsList.append (intAry[i])
			# Move to next polygon in the mesh list
			iterPolys.next()

		# print data for current node being iterated on
		print (dagPath.fullPathName()), '//////////////////////////////////'
		print 'Vertex list: ', vertexList
		print 'Edge list: ', edgeList
		print 'Poly Triangle Vertices: ', polytriVertsList
		print 'Polygon index list: ', polyList
		print 'Connected Polygons list: ', conpolyList

		# Move to the next selected node in the list
		iter.next()
