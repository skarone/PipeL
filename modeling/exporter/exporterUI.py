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
'''

import general.ui.pySideHelper as uiH
reload( uiH )
uiH.set_qt_bindings()
from Qt import QtGui,QtCore

import pipe.project.project as prj
reload( prj)
import os
import modeling.exporter.exporter as ex
reload( ex)
import pipe.asset.asset as ass
reload( ass)

try:
	import maya.cmds as mc
	import maya.mel as mm
except:
	print 'running from outside maya'

PYFILEDIR = os.path.dirname( os.path.abspath( __file__ ) )
uifile    = PYFILEDIR + '/exporter.ui'
fom, base = uiH.loadUiType( uifile )


class ExporterUI(base, fom):
	def __init__(self, parent  = uiH.getMayaWindow(), *args ):
		if uiH.USEPYQT:
			super(base, self).__init__(parent)
		else:
			super(ExporterUI, self).__init__(parent)
		self.setupUi(self)
		self._projectData()
		self._fillData()
		self._makeConnections()
		self.exporter = ''
		self.setObjectName( 'exporter_WIN' )
		uiH.loadSkin( self, 'QTDarkGreen' )

	def _fillData(self):
		"""add information to UI based on project and scene data"""
		self._fillProjects()
		self._fillSetName()

	def _projectData(self):
		"""try to get set name from scene"""
		fi = mc.file(q =1 ,sn = 1 )
		if fi == '':
			self.projectName = ''
			self.setName = ''
			return
		folders = fi.split( '/' )
		self.projectName = folders[2]
		self.setName     = folders[4]

	def _fillSetName(self):
		"""edit setName with set information --> WTF!"""
		self.setName_le.setText( self.setName )

	def _fillProjects(self):
		"""add all the projects to the ui"""
		for i,p in enumerate( prj.projects() ):
			self._insertProjectToUI( p, i )

	def _insertProjectToUI(self, projectName, index):
		"""docstring for _insertProjectToUI"""
		self.projects_cb.insertItems( index,[projectName])
		if self.projectName == projectName:
			self.projects_cb.setCurrentIndex( index )

	def _makeConnections(self):
		"""docstring for _makeConnections"""
		QtCore.QObject.connect( self.createPivot_btn, QtCore.SIGNAL( "clicked()" ), self._createPivot )
		QtCore.QObject.connect( self.export_btn, QtCore.SIGNAL( "clicked()" ), self._export )
		QtCore.QObject.connect( self.savePosition_btn, QtCore.SIGNAL( "clicked()" ), self._savePosition )

	def _savePosition(self):
		"""save position for selected asset"""
		sel = mc.ls( sl = True )
		if not sel:
			mc.error( 'PLEASE SELECT SOME OBJECT OF THE ASSET' )
		selSplit = sel[0].split( ':' )
		if not len(selSplit) == 2:
			mc.error( 'THIS OBJECT NEVER WAS EXPORTED, FIRST YOU NEED TO EXPORT THE ASSET')
		asset = ass.Asset( selSplit[0], prj.Project(  self.getProjectName() ))
		exporter = ex.AssetExporter( asset.name, asset.project.name, [] )
		setName = self.getSetName()
		exporter.grp =  exporter.asset.name + ':' + exporter.grp.name
		exporter.saveCoordsForSet( setName )


	def getProjectName(self):
		"""return the selected project from UI"""
		projectName = self.projects_cb.currentText()
		if projectName == '':
			return None
		print 'mierda',str( projectName )
		return str( projectName )

	def getAssetName(self):
		"""return the asset name in the UI"""
		assetName = self.assetName_le.text()
		if assetName == '':
			mc.error( 'PLEASE SET A NAME FOR THE ASSET' )
		return str( assetName )

	def getSetName(self):
		"""return the set name from the UI"""
		return str( self.setName_le.text() )

	def _createPivot(self):
		"""create Pivot for asset"""
		asset = ass.Asset( self.getAssetName(), prj.Project( self.getProjectName() ) )
		if asset.exists:
			mc.error( 'THIS ASSET ALREADY EXISTS IN THE PROYECT EDIT IT THERE! -->' + asset.name )
			return
		selection = mc.ls( sl = True )
		if not selection:
			mc.error( 'PLEASE SELECT THE OBJECTS OF THE ASSET' )
		self.exporter = ex.AssetExporter( asset.name, asset.project.name, selection )
		self.exporter.createPivot()

	def _createReferencedAsset(self):
		"""return if is checked the referenced checkbox item"""
		return self.referenced_cbx.isChecked()

	def _export(self):
		"""export asset"""
		if self.exporter == '':
			asset = ass.Asset( self.getAssetName(), prj.Project(  self.getProjectName() ))
			selection = mc.ls( sl = True )
			if not selection:
				mc.error( 'PLEASE SELECT THE OBJECTS OF THE ASSET' )
			self.exporter = ex.AssetExporter( asset.name, asset.project.name, selection )
		if not self.exporter.piv.piv.exists:
			if not self.exporter.grp.exists:
				mc.error( 'THERE IS NO GRP CREATED FOR THIS ASSET! -->' + self.getAssetName() )
			mc.error( 'THERE IS NO PIVOT CREATED FOR THIS ASSET! -->' + self.getAssetName() )
		self.exporter.export( self._createReferencedAsset(), self.getSetName() )

def main():
	"""call this from inside maya"""
	if mc.window( 'exporter_WIN', q = 1, ex = 1 ):
		mc.deleteUI( 'exporter_WIN' )
	expor = ExporterUI()
	expor.show()
