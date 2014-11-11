import general.mayaNode.mayaNode as mn
try:
	import maya.cmds as mc
	import maya.OpenMaya as api
except:
	pass

def copyVertexFromLeftToRight():
	"""move vertices from right blendshape to match left one"""
	ais = mn.ls( sl = True )
	dups = []
	for a in ais:
		dup = a.duplicate( 'dup_' + a.name[2:] )
		dup()
		dups.append( dup.name )
		mm.eval( 'abSymCtl( "fsBn" )' )
		for v in mc.ls( dup.name + '.vtx[*]', fl = True ):
			pos = mc.xform( v, q = True, t = True )
			mc.xform( v.replace( 'dup_', 'r_' ), t = pos )
		dup.delete()
		
def resetBlendshape( originalMesh = '', blendToReset = '' ):
	"""reset blendshape position to original face"""
	if not isinstance( originalMesh, mn.Node ):
		originalMesh = mn.Node( originalMesh )
	if not isinstance( blendToReset, mn.Node ):
		blendToReset = mn.Node( blendToReset )
	for v in mc.ls( originalMesh.name + '.vtx[*]', fl = True ):
		pos = mc.xform( v, q = True, t = True )
		mc.xform( v.replace( originalMesh.name, blendToReset.name ), t = pos )

def blendTargetsCount( blendNode ):
	"""
	Return the amount of blendshape targets in blend node
	"""
	return blendNode.a.weight.size

def extractBlendsTargets( blendNode, mesh, prefix = "" ):
	"""
	extract all blendshapes from blendshape node
	"""
	for i in range( blendTargetsCount( blendNode ) ):
		at = blendNode.attr( "weight[" +str( i )+"]" )
		geoName = prefix + mc.listAttr( at.fullname, sn = True )[0]
		at.v = 1
		mesh.duplicate( geoName )
		at.v = 0

def createMirror( meshes, baseMesh, axis = 'x', searchAndReplace = [ 'L_', 'R_' ], vertexList = [] ):
	"""create mirror of meshes """
	base = BlendShapeMesh( baseMesh, baseMesh )
	base.createReflectionTable( axis, vertexList )
	for m in mn.Nodes( meshes ):
		newNode = m.duplicate( m.name.replace( searchAndReplace[0], searchAndReplace[1] ) )
		blend = BlendShapeMesh( newNode.name, baseMesh, base.reflectionVertexTable )
		blend.mirror( axis. vertexList )

def createReflect( meshes, baseMesh, axis = 'x', searchAndReplace = [ 'L_', 'R_' ], vertexList = [] ):
	"""create mirror of meshes """
	base = BlendShapeMesh( baseMesh, baseMesh )
	base.createReflectionTable( axis, vertexList )
	for m in mn.Nodes( meshes ):
		newNode = m.duplicate( m.name.replace( searchAndReplace[0], searchAndReplace[1] ) )
		blend = BlendShapeMesh( newNode.name, baseMesh, base.reflectionVertexTable )
		blend.reflect( axis, vertexList )

class BlendShapeMesh( mn.Node ):
	"""docstring for BlendShapeMesh"""
	AXIS = {'x':0, 'y':1, 'z':2}
	def __init__(self, name, baseMesh, reflectionTable = {} ):
		super(BlendShapeMesh, self).__init__(name)
		self._baseMesh = mn.Node( baseMesh )
		self._reflectionTable = reflectionTable

	@property
	def baseMesh(self):
		"""return original mesh"""
		return self._baseMesh

	@property
	def reflectionVertexTable(self):
		"""docstring for reflectionVertexTable"""
		return self._reflectionTable

	def createReflectionTable(self, axis = 'x', vertexList = []):
		"""create the table that relates vertex from one side to the other"""
		#createVertexList from one side
		xVerts = []
		tolerance = 0.0001
		if not vertexList:
			vertexList = mn.ls( self.baseMesh.name + '.vtx[*]', fl = True )
		else:
			vertexList = mn.Nodes( [ self.baseMesh.name + '.' + a.split( '.' )[-1] for a in vertexList ] )
		for a in vertexList:
			vPos = mc.xform( a, q = True, os = True, t = True )
			if vPos[self.AXIS[axis]] + tolerance >= 0 or vPos[self.AXIS[axis]] - tolerance >= 0:
				xVerts.append( int( a.name[a.name.index('[')+1: a.name.index( ']' )]) )
		clos = mn.createNode( 'closestPointOnMesh' )
		self.baseMesh.a.worldMesh >> clos.a.inMesh
		for v in xVerts:
			vPos = mc.xform( self.baseMesh.name + '.vtx[' + str( v ) + ']', q = True, os = True, t = True )
			vPos[self.AXIS[axis]] *= -1
			clos.a.inPosition.v = [vPos[0],vPos[1],vPos[2] ]
			self._reflectionTable[v] = clos.a.closestVertexIndex.v
		clos.delete()

	def mirror(self, axis = 'x', vertexList = [] ):
		"""mirror blendshape only on vertexList, if non.. mirror all"""
		if not self.reflectionVertexTable:
			self.createReflectionTable( axis, vertexList )
		for s in self.reflectionVertexTable.keys():
			vPos1 = mc.xform( self.name + '.vtx[' + str( s ) + ']', q = True, os = True, t = True )
			vPos1[self.AXIS[axis]] *= -1
			if s == self.reflectionVertexTable[ s ]: #middle vertex, only move once
				vPos1[self.AXIS[axis]] = (( vPos1[self.AXIS[axis]] * -1) + vPos1[self.AXIS[axis]]) / 2
			mc.xform( self.name + '.vtx[' + str(  self.reflectionVertexTable[ s ] ) + ']', os = True, t = vPos1 )

	def reflect(self, axis = 'x', vertexList = [] ):
		"""reflect blendshape only on vertexList, if non.. reflect all"""
		if not self.reflectionVertexTable:
			self.createReflectionTable( axis, vertexList )
		for s in self.reflectionVertexTable.keys():
			vPos1 = mc.xform( self.name + '.vtx[' + str( s ) + ']', q = True, os = True, t = True )
			vPos1[self.AXIS[axis]] *= -1
			vPos2 = mc.xform( self.name + '.vtx[' + str( self.reflectionVertexTable[ s ] ) + ']', q = True, os = True, t = True )
			mc.xform( self.name + '.vtx[' + str( self.reflectionVertexTable[ s ] ) + ']', os = True, t = vPos1 )
			if s == self.reflectionVertexTable[ s ]: #middle vertex, only move once
				continue
			vPos2[self.AXIS[axis]] *= -1
			mc.xform( self.name + '.vtx[' + str( s ) + ']', os = True, t = vPos2 )

	def asBase(self, vertexList = None):
		"""set vertex of blendshape as baseMesh"""
		if not vertexList:
			vertexList = mn.ls( self.name + '.vtx[*]', fl = True )
		for a in vertexList:
			vPos = mc.xform( a.name.replace( self.name, self.baseMesh.name ), q = True, os = True, t = True )
			mc.xform( a.name, os = True, t = vPos )


class BlendShapeNode( mn.Node ):
	"""docstring for BlendShapeNode"""
	def __init__(self, name):
		super(BlendShapeNode, self).__init__( name )

	def create(self, meshes, baseMesh ):
		"""create blendshape and add meshes as targets"""
		self.__init__( mc.blendShape( meshes, baseMesh, n = self.name )[0] )
		
	@property
	def meshes(self):
		"""return all the blendshapes that this blendshape node has"""
		blends = ads.listAttr( st = 'weight', m = True )
		result = []
		for a in blends:
			result.append( BlendShapeMesh( a.name ) )
		return result

	@property
	def meshesCount(self):
		"""return the number of targets that the blendshape has"""
		return len(self.meshes)

	def getMeshIndex(self, mesh):
		"""docstring for getMeshIndex"""
		res = [m.name for m in self.meshes ]
		return res.index( mesh )

	@property
	def isMeshTarget(self, mesh):
		"""docstring for isMeshTarget"""
		return mesh in [m.name for m in self.meshes ]

	@property
	def baseMesh(self):
		"""docstring for baseMesh"""
		return mn.Node( mc.ls( mc.listHistory(self.name, future=True), typ = 'mesh' )[0] )

	def addMesh(self, mesh):
		"""add Mesh to blendshape node"""
		if self.isMeshTarget( mesh ):
			print 'This mesh is allready a target for this blendshape', mesh, self.name
			return
		mc.blendShape( self.name, edit=True, t=(self.baseMesh.name, len(self.meshes), mesh, 1.0) )

	def addInBetween(self, mesh, inBetweenMesh, percent ):
		"""add mesh for inbetween"""
		mc.blendShape( self.name, edit=True, t=(self.baseMesh.name, self.getMeshIndex( mesh ), inBetweenMesh, percent) )

	def removeMesh(self, mesh):
		"""remove mesh from target mesh"""
		mc.blendShape( self.name, edit=True, rm = True, t=(self.baseMesh.name, self.getMeshIndex( mesh ), mesh, 1.0) )

	def makeCorrectiveBlend(self, mesh1, mesh2 ):
		"""create a corrective blendshape"""
		corrective = self.baseMesh.duplicate( mesh1 + mesh2 + '_corrective' )
		corrective.a.corrective.add( at = 'bool' )
		self.a.envelope.v = 0
		dummy = self.baseMesh.duplicate( mesh1 + mesh2 + '_dummy' )
		dummy.a.dummy.add( at = 'bool' )
		self.a.envelope.v = 1
		blend = BlendShapeNode( mesh1 + mesh2 + '_blend' )
		blend.create( [mesh1, mesh2, corrective], dummy )
		dummy.attr( mesh1 ).v = -1
		dummy.attr( mesh2 ).v = -1
		dummy.attr( corrective.name ).v = 1
		self.addMesh( dummy.name )
		#connect mesh1 and mesh 2 to controls dummy weight
		mul = mn.createNode( 'multiplyDivide' )
		mul.name = mesh1 + mesh2 + '_MUL'
		self.attr( mesh1 ) >> mul.a.input1X
		self.attr( mesh2 ) >> mul.a.input2X
		mul.a.outputX >> self.attr( dummy.name )
		


