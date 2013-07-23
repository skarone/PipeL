'''
File: exporter.py
Author: Ignacio Urruty
Description: 
	Create asset with folders from objects selected in current scene
	-Export Seleccion
	-Export World Coordinates
	-Rename Objects
	-Delete History
	-Set 0 for visual smooth
	-Interactive position for pivot
	Workarround:
		1-Select Objects
		2-In UI set Name for asset and Proyect
			2a- Check if asset name already exists
		3-Rename all objects with assetName
		4-Delete Hisotry in objects and set 0 for visual Smooth
		5-Create Control to set pivot for position
		6-Create Group with asset Name and set pivot in the selected position
		7-Move Group to 000 of worldspace
		8-Freeze Transforms
		9-Make folders for asset
		10-Export Group --> Asset_MODEL.ma
		11-Export World Coordinates( FINAL POSITION ) for the asset
		12-Add Asset to Set.breakdown
'''
import general.mayaNode.mayaNode as mn
reload(mn)
import maya.cmds as mc
import maya.mel as mm
import pipe.asset.asset as ass
reload(ass)
import pipe.project.project as prj
reload(prj)
import pipe.sets.sets as seT
reload( seT )
import os
import shutil

class Pivot(object):
	"""Pivot object that help to setup asset final pivot"""
	def __init__(self, assetName):
		self._assetName = assetName

	@property
	def name(self):
		"""return the name of the pivot"""
		return self._assetName + '_obj_pivot'

	@property
	def assetName(self):
		"""return the name of the asset"""
		return self._assetName

	def create(self):
		"""create pivot object"""
		front = mc.textCurves( n= self.assetName + 'front_grp', f='Courier|w400|h-11', t='Front' )
		mc.delete( front[1] )
		front = mn.Node( front[0] )
		left  = mc.textCurves( n= self.assetName + 'left_grp', f='Courier|w400|h-11', t='Left' )
		mc.delete( left[1] )
		left  = mn.Node( left[0] )
		left.a.ry.v = 90
		left.a.tx.v = 10
		top   = mc.textCurves( n= self.assetName + 'top_grp', f='Courier|w400|h-11', t='Top' )
		mc.delete( top[1] )
		top   = mn.Node( top[0] )
		top.a.rx.v = -90
		top.a.ty.v = 10
		box = mc.curve( d = 1, p = [(0,0,0), (10,0,0), (10,10,0), (0,10,0), 
									(0,0,0), (0,0,-10), (10,0,-10), (10,0,0), 
									(10,10,0), (10,10,-10), (10,0,-10), (10,10,-10), 
									(10, 10, 0), (0,10,0), (0,10,-10), (10,10,-10), 
									(10,0,-10), (0,0,-10), (0,10,-10)], 
								k = [0,1,2,3,4,5,6,7,8,9,10,11,12,13,14,15,16,17,18], n = self.assetName + 'box' )
		grp = mn.Node( mc.group( front.name, left.name, top.name, box, n = self.name ) )
		self.setPivot( [5,5,-5] )
		grp.a.t.v = [-5,-5,5]
		mc.makeIdentity( grp.name, apply = True, t = True, r = True, s = True, n = 1 )
		curves = mc.ls( grp.name, dag = True, typ = 'nurbsCurve' )
		mc.parent( curves, grp.name, add=True, shape = True )
		mc.delete( front.name, left.name, top.name, box )

	def select(self):
		"""select pivot"""
		if mc.objExists( self.name ):
			mc.select( self.name )

	def setPivot(self, coords):
		"""set Pivot from world coords"""
		self.piv.a.scalePivot.v  = coords
		self.piv.a.rotatePivot.v = coords

	@property
	def piv(self):
		"""return piv object"""
		return mn.Node( self.name ) 

	def delete(self):
		"""delete Pivot"""
		mc.delete( self.piv )

	@property
	def matrix(self):
		"""return worldMatrix pivot"""
		return self.piv.a.matrix

	@property
	def rotation(self):
		"""return rotate attribute of pivot"""
		return self.piv.a.rotate.v

	@property
	def translate(self):
		"""return translate attribute of pivot"""
		return mc.xform( self.name, q = True, ws = True, rp = True)

class AssetExporter(object):
	"""current Asset to export"""
	def __init__(self, name, project, objects):
		self._objects     = objects
		self._project     = prj.Project( project )
		self._asset       = ass.Asset( name, self._project )
		self._grp         = self.name + '_grp'

	@property
	def name(self):
		"""return the name of the asset"""
		return self.asset.name

	@property
	def asset(self):
		"""return the asset object"""
		return self._asset

	@property
	def objects(self):
		"""return the objects list of the asset"""
		return self._objects

	@property
	def project(self):
		"""return the project"""
		return self._project

	def renameAssetObjects(self):
		"""rename all the objects of the asset"""
		for i,o in enumerate( self.objects ):
			mn.Node( o ).name = self.name + '%i'%i
		
	def deleteHistory(self):
		"""delete the history in all the objects"""
		mc.delete( self.objects, ch = True )

	def createPivot(self):
		"""create a Pivot object to handle final transformation and get world coordinates"""
		piv = Pivot( self.name )
		piv.create()
		piv.select()
		#TODO move pivot to a better position

	@property
	def piv(self):
		"""return piv object"""
		return Pivot( self.name )

	@property
	def grp(self):
		"""return grp name"""
		return mn.Node( self._grp )

	@grp.setter
	def grp(self, grpNode):
		"""set a new grp node"""
		self._grp =  grpNode

	def createMainGroup(self):
		"""create the main group for the asset"""
		mc.group( n = self.grp.name, em = True )
	
	def addObjectsToGroup(self):
		"""add all the objects to the group"""
		mc.parent( self.objects, self.grp.name )

	def setCoordsToMainFromPivot(self):
		"""set rotation and translate of the main group from the pivot"""
		self.grp.a.t.v = self.piv.translate
		self.grp.a.r.v = self.piv.rotation[0]

	def freezeObjectsTransforms(self):
		"""set to Zero all the transforms of the objects"""
		mc.makeIdentity( self.objects, apply = True, t = 1, r = 1, s = 1, n = 0, pn = 1 )

	def moveToZero(self):
		"""move grp to zero.. and then move again to final position =)"""
		self.grp.a.t.v = [0,0,0]
		self.grp.a.r.v = [0,0,0]

	def export(self, referenced = False, seT = ''):
		"""export asset"""
		self.deleteHistory()
		if not self.grp.exists:
			self.createMainGroup()
		if self.piv.piv.exists:
			self.setCoordsToMainFromPivot()
		self.addObjectsToGroup()
		self.renameAssetObjects()
		self.exportGrp( referenced )
		if self.piv.piv.exists:
			self.piv.delete()
		if referenced and seT != '':
			self.saveCoordsForSet( seT )

	def exportGrp(self, referenced = True):
		"""export grp"""
		#export and create reference file
		if not self.asset.exists():
			self.project.addAsset( self.asset.name )
		self.moveToZero()
		mc.select( self.grp.name )
		#move referenced file to final position!
		if referenced:
			mc.file( self.asset.finalPath, type='mayaAscii', namespace=self.asset.name, exportAsReference=referenced, force = True)
			self.grp = self.asset.name + ':' + self.grp.name
		else:
			mc.file( self.asset.finalPath, type='mayaAscii', es = True, force = True)
		self.setCoordsToMainFromPivot()
		shutil.copy( self.asset.finalPath, self.asset.modelPath )

	def saveCoordsForSet(self, setName):
		"""save the coords of the asset in set.breakdown"""
		se = seT.Set( setName, self.project )
		se.saveAsset( self.asset.name, {'translate':self.grp.a.t.v[0],'rotate':self.grp.a.r.v[0] } )

