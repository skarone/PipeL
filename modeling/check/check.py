'''
File: check.py
Author: Ignacio Urruty
Description: Check Modeling scene tools
'''
import general.utils.utils as gutils
reload( gutils )

import general.ui.pySideHelper as uiH
reload( uiH )
uiH.set_qt_bindings()
from Qt import QtGui,QtCore

import os
try:
	import general.mayaNode.mayaNode as mn
	reload( mn )
	import maya.OpenMayaUI as mui
	import maya.cmds as mc
	INMAYA = True
except:
	pass
#load UI FILE
PYFILEDIR = os.path.dirname( os.path.abspath( __file__ ) )

uifile = PYFILEDIR + '/check.ui'
fom, base = uiH.loadUiType( uifile )


class checkModelSceneUi(base,fom):
	"""manager ui class"""
	def __init__(self, parent  = uiH.getMayaWindow(), *args ):
		if uiH.USEPYQT:
			super(base, self).__init__(parent)
		else:
			super(checkModelSceneUi, self).__init__(parent)
		self.setupUi(self)
		self._makeConnections()
		self.checkScene()
		self.setObjectName( 'modelSceneCheck_WIN' )

	def _makeConnections(self):
		"""create connection in the UI"""
		self.connect( self.check_btn, QtCore.SIGNAL("clicked()") , self.checkScene )
		self.connect( self.groupAll_btn, QtCore.SIGNAL("clicked()") , self.groupAll )
		self.connect( self.freezeAll_btn, QtCore.SIGNAL("clicked()") , self.freezeAll )
		self.connect( self.deleteHistory_btn, QtCore.SIGNAL("clicked()") , self.deleteHistory )
		self.connect( self.autoRename_btn, QtCore.SIGNAL("clicked()") , self.autoRename )
		self.connect( self.reAssignMaterial_btn, QtCore.SIGNAL("clicked()") , self.reAssignMaterial )
		self.connect( self.fixAll_btn, QtCore.SIGNAL("clicked()") , self.fixAll )
		QtCore.QObject.connect( self.withMaterialPerFace_lw, QtCore.SIGNAL( "itemClicked( QListWidgetItem* )" ), self.selectNode )
		QtCore.QObject.connect( self.withDuplicatedNames_lw, QtCore.SIGNAL( "itemClicked( QListWidgetItem* )" ), self.selectNode )
		QtCore.QObject.connect( self.withHistory_lw,         QtCore.SIGNAL( "itemClicked( QListWidgetItem* )" ), self.selectNode )
		QtCore.QObject.connect( self.withoutFreeze_lw,       QtCore.SIGNAL( "itemClicked( QListWidgetItem* )" ), self.selectNode )

	def groupAll(self):
		"""docstring for groupAll"""
		gutils.groupAll()
		self.checkScene()
		
	def freezeAll(self):
		"""docstring for freezeAll"""
		gutils.freezeAll()
		self.checkScene()

	def deleteHistory(self):
		"""docstring for deleteHistory"""
		gutils.deleteHistory()
		self.checkScene()

	def autoRename(self):
		"""docstring for autoRename"""
		gutils.autoRename()
		self.checkScene()

	def reAssignMaterial(self):
		"""docstring for reAssignMaterial"""
		gutils.reAssignMaterial()
		self.checkScene()

	def fixAll(self):
		"""docstring for fixAll"""
		self.freezeAll()
		self.deleteHistory()
		self.autoRename()
		self.reAssignMaterial()
		self.groupAll()

	def checkScene(self):
		"""docstring for checkScene"""
		color = [
				QtGui.QColor( "green" ),
				QtGui.QColor( "red" )]
		palette = QtGui.QPalette()
		if gutils.isAllInOneGroup():
			palette.setColor(QtGui.QPalette.Foreground,QtCore.Qt.green)
			self.allInOneGrp_lbl.setText( 'YES' )
		else:
			palette.setColor(QtGui.QPalette.Foreground,QtCore.Qt.red)
			self.allInOneGrp_lbl.setText( 'NO' )
		self.allInOneGrp_lbl.setPalette(palette)
		meshesWithHistory, meshesWithMaterialPerFace = gutils.isMeshWithHistory()
		lists = [self.withMaterialPerFace_lw,
				self.withHistory_lw,
				self.withDuplicatedNames_lw,
				self.withoutFreeze_lw]
		nodes = [meshesWithMaterialPerFace,
				meshesWithHistory,
				gutils.checkDuplicatedNamesInScene(),
				gutils.transformsWithoutFreeze()
				]
		for l,n in zip( lists, nodes ):
			l.clear()
			if len(n) == 0:
				continue
			self._fillList( l, n )

	def selectNode(self, item):
		"""docstring for selectNode"""
		mn.Node( str( item.text() ) )()

	def _fillList(self,lis, nodes):
		"""fill lists"""
		lis.addItems( [s.name for s in nodes ])

def main():
	"""use this to create project in maya"""
	if mc.window( 'modelSceneCheck_WIN', q = 1, ex = 1 ):
		mc.deleteUI( 'modelSceneCheck_WIN' )
	PyForm=checkModelSceneUi()
	PyForm.show()

