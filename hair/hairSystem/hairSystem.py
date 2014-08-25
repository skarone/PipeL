"""
Documentation about hairSystemAutomator has not been written yet...
Shame on mlyndon!

DEV shelf button:

import sys
sys.path.append('y:/vfx/ftb_vfx_hairSystemAutomator')
import ftb_vfx_hairSystemAutomator_v001 as ftb_vfx_hairSystemAutomator
reload (ftb_vfx_hairSystemAutomator)
ftb_vfx_hairSystemAutomator.ftb_vfx_hairSystemAutomator()

PUB shelf button:

import sys
sys.path.append('t:/vfx/ftb_vfx_hairSystemAutomator')
import ftb_vfx_hairSystemAutomator
reload (ftb_vfx_hairSystemAutomator)
ftb_vfx_hairSystemAutomator.ftb_vfx_hairSystemAutomator()



"""

#-----------------------------------------------------------------------------------------------
# Imports
#-----------------------------------------------------------------------------------------------
import sys
import os
from pymel.core import *
import general.mayaNode.mayaNode as mn
reload( mn )
import maya.cmds as mc

"""
import hair.hair as hr
reload( hr )
hr.hairSystemAutomator( 'cejas' )

import hair.hair as hr
import general.mayaNode.mayaNode as mn
import maya.cmds as mc
reload( hr )
sel = mn.ls( sl = True )
scalp = ''
for s in sel:
	mc.select( sel.children )
	asd = hr.hairSystemAutomator( sysName = sel.name.replace( '_lock_grp', '' ), scalp = scalp )


"""
full_path = os.path.realpath(__file__)

#Y:\PipeL\hair\hairSystem
#Y:\PipeL\install\MayaPlugins

mc.loadPlugin( os.path.dirname(full_path).replace( 'hair/hairSystem', 'install/MayaPlugins' ) + '/'+ mc.about( version = True ) +  '/curvesFromMesh.mll' )


def hairSystemAutomator( sysName = '', scalp = None ):
	"""creates a hair system based on selected lock meshes, 
	if you specify a scalp it will use that to place follicles"""
	hair_polygons = mn.ls(sl=1)
	all_grp = mn.Node( mc.group( n = sysName + '_hair_grp', em = True ) )
	hairSystem = mn.createNode('hairSystem')
	hairSystemPar = hairSystem.parent
	hairSystemPar.name = sysName + '_hairSystem'
	hairSystemPar.parent = all_grp
	hairSystem = hairSystemPar.shape
	pfxHair = mn.createNode( 'pfxHair' )
	pfxHairPar = pfxHair.parent
	pfxHairPar.name = sysName + '_pfxHair'
	pfxHairPar.parent = all_grp
	pfxHair = pfxHairPar.shape
	foll_grp = mn.Node( mc.group( n = sysName + '_foll_grp', em = True ) )
	foll_grp.parent = all_grp
	curve_grp = mn.Node( mc.group( n = sysName + '_crv_grp', em = True ) )
	curve_grp.parent = all_grp
	allFollicles = []
	allHairCurves = []
	allFtbHairCurves = []
	hairCount = 0
	plugCount = 0
	badMesh = []
	for hair_poly in hair_polygons:
		hairLock = HairLock( hair_poly, hairSystem, scalp )
		hairLock.create()
		for i in range( 5 ):
			hairLock.follicles[i].parent = foll_grp
			#if not scalp:
			hairLock.curves[i].parent    = curve_grp
	#hairSystem.attr( "clumpFlatness[0].clumpFlatness_Position" ).v = 0
	#hairSystem.attr( "clumpFlatness[0].clumpFlatness_FloatValue" ).v = 0.5
	hairSystem.a.simulationMethod.v = 1
	hairSystem.a.outputRenderHairs >> pfxHair.a.renderHairs
	ti = mn.Node( 'time1' )
	ti.a.outTime >> hairSystem.a.currentTime


class HairLock(object):
	"""this is the hair lock class"""
	def __init__( self, mesh, hairSystem = None, scalp = None ):
		self._curveMesh  = None
		self._curves     = []
		self._follicles  = []
		self._scalp      = None
		self._mesh   = mesh
		self._hairSystem = hairSystem
		if isinstance( scalp, mn.Node ):
			self._scalp   = scalp
		else:
			self._scalp   = mn.Node( scalp )

	@property
	def mesh(self):
		"""return the mesh of the HairLock"""
		return self._mesh

	@property
	def follicles(self):
		"""return the follicles that are conected to"""
		if self._follicles:
			return self._follicles

	@property
	def hairSystem(self):
		"""return the hair system of the current HairLock"""
		if self._hairSystem:
			return self._hairSystem

	@property
	def curves(self):
		"""return the 5 curves that are conected to"""
		if self._curves:
			return self._curves

	@property
	def scalp(self):
		"""return the scalp mesh"""
		if self._scalp:
			return self._scalp

	@property
	def curveMesh(self):
		"""return the mesh to curve node"""
		if self._curveMesh:
			return self._curveMesh

	def create(self):
		"""create hairsystem for lock"""
		numFace = mc.polyEvaluate( self.mesh.shape.name, f = True )
		numVert = mc.polyEvaluate( self.mesh.shape.name, v = True )
		if not self.hairSystem:
			print 'There is no hairSystem assigned to this HairLock --> init with one or assign one.... '
		if not numFace % 2 or not numVert == ( numFace + 3 ):
			print 'This mesh dosen\'t have odd number of faces', self.mesh.name, 'SKYPING'
			return
		self._curveMesh = mn.createNode('curvesFromMesh' )
		self._curveMesh.name = self.mesh.name + '_curveMesh'
		self.mesh.shape.a.outMesh     >> self._curveMesh.a.inMesh
		self.mesh.shape.a.worldMatrix >> self._curveMesh.a.inWorldMatrix
		for i in range(5):	
			hairCurve = mn.createNode('nurbsCurve' )
			hairCurveParent = hairCurve.parent
			hairCurveParent.name = self.mesh.name + '_%i'%i + '_crv'
			hairCurve = hairCurveParent.shape
			self._curveMesh.attr( 'outCurve[%i'%i + ']' ) >> hairCurve.a.create
			
			follicle = mn.createNode('follicle')
			folliclePar = follicle.parent
			folliclePar.name = self.mesh.name + '_%i'%i + '_foll'
			follicle = folliclePar.shape
			hairSustemOutHairSize = self.hairSystem.a.outputHair.size 
			follicle.a.outHair >> self.hairSystem.attr( 'inputHair[%i'%hairSustemOutHairSize + ']' )
			#follicle.a.outHair >> self.hairSystem.attr( 'inputHair[%i'%i + ']' )
			hairCurve.a.worldSpace >> follicle.a.startPosition
			self.hairSystem.attr( 'outputHair[%i'%hairSustemOutHairSize + ']' ) >> follicle.a.currentPosition
			self._follicles.append(follicle)
			self._curves.append(hairCurve)
			#if there is a scalp mesh use that for the position of the follicle
			if self.scalp:
				self.scalp.shape.a.outMesh >> follicle.a.inputMesh
				self.scalp.a.worldMatrix   >> follicle.a.inputWorldMatrix
				u,v = self._getUVCoordFromScalpForFollicle( hairCurve )
				follicle.a.parameterV.v       = v
				follicle.a.parameterU.v       = u
				#hairCurveParent.parent        = folliclePar
			else:
				self.mesh.shape.a.outMesh  >> follicle.a.inputMesh
				self.mesh.a.worldMatrix    >> follicle.a.inputWorldMatrix
				follicle.a.parameterV.v       = 0.5
				follicle.a.parameterU.v       = 0.5
			follicle.a.overrideDynamics.v = 0
			follicle.a.startDirection.v   = 1
			follicle.a.clumpWidthMult.v   = 1.5
			follicle.a.densityMult.v      = 0.5
			follicle.a.sampleDensity.v    = 1.5
			follicle.a.outTranslate >> follicle.parent.a.translate
			follicle.a.outRotate >> follicle.parent.a.rotate

	def _getUVCoordFromScalpForFollicle(self, curve):
		"""return the closest uv coord for the follicle based on first cv of the curve"""
		if not self.scalp:
			print 'There is no scalp mesh for this process'
			return 
		clos = mn.createNode( 'closestPointOnMesh' )
		self.scalp.shape.a.worldMesh >> clos.a.inMesh
		pos = mc.xform( curve.name + '.cv[0]', q = True, ws = True, t = True )
		clos.a.inPosition.v = pos
		u = clos.a.parameterU.v
		v = clos.a.parameterV.v
		clos.delete()
		return u,v

def hairLockRenamer():
	"""docstring for hairLockRenamer"""
	i = 0
	for a in mn.ls( sl =True ):
		a.name = 'hair_%i'%i + '_lock'
		i += 1

