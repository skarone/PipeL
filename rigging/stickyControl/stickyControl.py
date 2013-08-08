import general.mayaNode.mayaNode   as mn
reload( mn)
import maya.cmds                   as mc
import general.transform.transform as trf

"""
import rigging.stickyControl.stickyControl as stk
reload( stk )
stk.createControlForSelection( name = 'controlOnMesh', baseJoint = '' )

import rigging.stickyControl.stickyControl as stk
reload( stk )
stk.createControlInRig( mesh = 'defaultShape1' )

"""
mc.loadPlugin( "C:/Program Files/Autodesk/Maya2013/bin/plug-ins/MayaMuscle.mll" )

def createControlForSelection( name = 'controlOnMesh', baseJoint = '' ):
	"""create a control based on selection...
	1- Select Transform( locator )
	2- Select Mesh
	3- You can run procedural with a specific base joint 
	3- run createControlForSelection()"""
	sel = mn.ls( sl = True )
	if not sel:
		mc.error( 'PLEASE SELECT A TRANSFORM AND A MESH IN THAT ORDER' )
	elif not len(sel) == 2:
		mc.error( 'PLEASE SELECT A TRANSFORM AND A MESH IN THAT ORDER' )
	else:
		trans = sel[0]
		mesh  = mn.ls( sel[1].name, dag = True, s = True, ni = True )
		if not mesh:
			mc.error( 'PLEASE SELECT A TRANSFORM AND A MESH IN THAT ORDER' )
		control = ControlOnMesh( name = name, baseJoint = baseJoint, position = trans.a.translate.v[0], mesh = mesh[0] )
		control.create()

def createControlInRig( mesh = '', baseJoint = '' ):
	"""create a control based on control points setted on rig,
	take names from that control points and make mirror if the control starts with l_"""
	conPoints = mn.ls( '*_point' )
	for c in conPoints:
		name = c.name.replace( '_point', '' )
		control = ControlOnMesh( name = name, baseJoint = baseJoint, position = c.a.translate.v[0], mesh = mesh )
		control.create()
		if name.startswith( 'l_' ):
			name = 'r_' + name[2:]
			pos  = [-c.a.tx.v, c.a.ty.v, c.a.tz.v]
			control = ControlOnMesh( name = name, baseJoint = baseJoint, position = pos, mesh = mesh )
			control.create()


class ControlOnMesh(object):
	"""class to create and handle a Control on a mesh"""
	def __init__(self, name, baseJoint = '', position = (0,0,0), mesh = ''):
		self._name         = name
		self._baseJoint    = baseJoint
		self._initPosition = position
		if isinstance( mesh, mn.Node ):
			self._mesh     = mesh
		else:
			self._mesh     = mn.Node( mesh )
		self._control      = None

	@property
	def mesh(self):
		"""return the mesh used in the control"""
		return self._mesh

	@property
	def control(self):
		"""return the control object"""
		if self._control:
			return self._control

	@property
	def name(self):
		"""return the name of the control"""
		return self._name
		
	@property
	def initPosition(self):
		"""return the initPosition of the control"""
		return self._initPosition
		
	def create(self):
		"""create Control system
		1- Create Joint on position
		2- Create Muscle Constraint
		3- Create Curve Control
		4- Make Connections
		"""
		self.rivet = self._createConstraint()
		self._createJoint()
		control = self._createControl()
		trf.snap( self.rivet.name , control.name )
		nullTrf = mn.createNode( 'transform' )
		nullTrf.name = self.name + '_baseControl'
		trf.snap( self.rivet.name , nullTrf.name )
		nullTrf.parent = self.rivet
		control.parent = nullTrf
		#make connections
		multi = mn.createNode( 'multiplyDivide' )
		multi.name = self.name + '_multi'
		multi.a.input2.v = [-1,-1,-1]
		multi.a.output >> nullTrf.a.translate
		control.a.t >> multi.a.input1
		control.a.t >> mn.Node( self.skinJoint ).a.t
		control.a.r >> mn.Node( self.skinJoint ).a.r
		control.a.s >> mn.Node( self.skinJoint ).a.s
	
	def _createControl(self):
		"""create control object"""
		#curve = mc.circle( c = (0,0,0), nr = (0,0,1), sw = 360, r = 1, d = 3, ut = 0, tol = 0.01, s = 8, ch = 0, n = self.name + '_ctl' )
		curve = mc.sphere( r=0.2, n = self.name + '_ctl' )
		self._control = mn.Node( curve[0] )
		return self._control

	@property
	def skinJoint(self):
		"""return skin Joint name"""
		return self.name + '_skin'

	@property
	def baseJoint(self):
		"""return base Joint name"""
		return self._baseJoint

	def _createJoint(self):
		"""create joint on poistion"""
		mc.select( cl = True )
		mc.joint( p = self.rivet.a.translate.v[0], o = self.rivet.a.rotate.v[0], n = self.name + '_joint' )
		mc.joint( p = self.rivet.a.translate.v[0], o = self.rivet.a.rotate.v[0], n = self.skinJoint )
		if self._baseJoint != '':
			mn.Node( self.name + '_joint' ).parent = self._baseJoint

	def _createConstraint(self):
		"""create constraint to mesh for the control"""
		edge1, edge2 = self._getClosestEdgesFromMesh()
		rebuild,loft  = self._loftFromEdges( edge1, edge2 )
		u,v = self._uvParamFromPositionOnLoft( rebuild )
		rivet = mn.createNode( 'cMuscleSurfAttach' )
		rivet.a.uLoc.v = u
		rivet.a.vLoc.v = v
		rivet.a.edgeIdx1.v = edge1
		rivet.a.edgeIdx2.v = edge2
		rivet.a.fixPolyFlip.v = 1
		rivetPar = rivet.parent
		self.mesh.a.worldMesh >> rivet.a.surfIn
		rivet.a.outRotate >> rivetPar.a.rotate
		rivet.a.outTranslate >> rivetPar.a.translate
		#need to check if the uv are ok or we have to flip them

		rivetPar.name = self.name + '_rivet'
		return rivetPar

	def _getClosestEdgesFromMesh(self):
		"""return the closets edges from the mesh to use"""
		clos = mn.createNode( 'closestPointOnMesh' )
		self.mesh.a.worldMesh >> clos.a.inMesh
		clos.a.inPosition.v = self.initPosition
		closeFace = clos.a.closestFaceIndex.v
		edges = mc.polyInfo( self.mesh.name + '.f[%i'%closeFace + ']', faceToEdge = True )
		edges = edges[0].split()
		edge1 = int( edges[2] )
		edge2 = int( edges[4] )
		clos.delete()
		return edge1, edge2
		
	def _loftFromEdges( self, edge1, edge2 ):
		"""Create a loft nurbs from edges"""
		#EDGE 1
		edge1_cme = mn.createNode('curveFromMeshEdge',n='edfe1')
		self.mesh.a.worldMesh >> edge1_cme.a.inputMesh
		edge1_cme.attr( 'edgeIndex[0]' ).v = edge1
		
		#EDGE 2
		edge2_cme = mn.createNode('curveFromMeshEdge',n='edfe2')
		self.mesh.a.worldMesh >> edge2_cme.a.inputMesh
		edge2_cme.attr( 'edgeIndex[0]' ).v = edge2
		
		mesh_lft = mn.createNode('loft',n='loft')
		edge1_cme.a.outputCurve >> mesh_lft.attr( 'inputCurve[0]' )
		edge2_cme.a.outputCurve >> mesh_lft.attr( 'inputCurve[1]' )
		mesh_lft.a.degree.v = 1
		rebuild = mn.createNode( 'rebuildSurface', n = 'rebuild' )
		mesh_lft.a.outputSurface >> rebuild.a.inputSurface
		rebuild.a.spansU.v = 0
		rebuild.a.spansV.v = 0
		rebuild.a.degreeU.v = 1
		rebuild.a.degreeV.v = 1
		rebuild.a.keepRange.v = 0
		return rebuild, mesh_lft

	def _uvParamFromPositionOnLoft(self, loft):
		"""return the uvs values to set up on constrain"""
		clos = mn.createNode( 'closestPointOnSurface' )
		loft.a.outputSurface >> clos.a.inputSurface
		clos.a.inPosition.v = self.initPosition
		u = clos.a.parameterU.v
		v = clos.a.parameterV.v
		clos.delete()
		return u,v

