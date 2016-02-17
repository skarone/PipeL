import os
import general.ui.pySideHelper as uiH
reload( uiH )

from Qt import QtGui,QtCore

import maya.cmds as mc
import general.mayaNode.mayaNode as mn
import rigging.eyelids.eyelids as eyeLids
reload( eyeLids )

PYFILEDIR = os.path.dirname( os.path.abspath( __file__ ) )

uifile = PYFILEDIR + '/eyelids.ui'
fom, base = uiH.loadUiType( uifile )


class eyeLidsRigUi(base, fom):
	"""docstring for ProjectCreator"""
	def __init__(self, parent  = uiH.getMayaWindow(), *args ):
		if uiH.USEPYQT:
			super(base, self).__init__(parent)
		else:
			super(eyeLidsRigUi, self).__init__(parent)
		self.setupUi(self)
		self.setObjectName( 'eyeLidsRigUi' )
		self.connect(self.fillUpperLidsVerteces_btn, QtCore.SIGNAL("clicked()"), self.fillUpperLidsVerteces)
		self.connect(self.selectUpperLids_btn, QtCore.SIGNAL("clicked()"), self.selectUpperLids)
		self.connect(self.fillLowerLidsVerteces_btn, QtCore.SIGNAL("clicked()"), self.fillLowerLidsVerteces)
		self.connect(self.selectLowerLids_btn, QtCore.SIGNAL("clicked()"), self.selectLowerLids)
		self.connect(self.fillCenterPivot_btn, QtCore.SIGNAL("clicked()"), self.fillCenterPivot)
		self.connect(self.create_btn, QtCore.SIGNAL("clicked()"), self.create)

	def fillUpperLidsVerteces(self):
		"""docstring for fname"""
		self.upperLidsVerteces_lw.clear()
		self.upperLidsVerteces_lw.addItems( mc.ls( fl = True, orderedSelection = True ) )

	def selectUpperLids(self):
		"""docstring for fname"""
		mc.select( self.upperLidVerteces )

	def fillLowerLidsVerteces(self):
		"""docstring for fname"""
		self.lowerLidsVerteces_lw.clear()
		self.lowerLidsVerteces_lw.addItems( mc.ls( fl = True, orderedSelection = True ) )

	def selectLowerLids(self):
		"""docstring for fname"""
		mc.select( self.lowerLidVerteces )

	def fillCenterPivot(self):
		"""docstring for fname"""
		self.centerPivot_le.setText( mn.ls( sl = True )[0].name )

	@property
	def lowerLidVerteces(self):
		"""docstring for lowerLidVerteces"""
		vertexToSelect = []
		for index in xrange(self.lowerLidsVerteces_lw.count()):
			vertexToSelect.append( str( self.lowerLidsVerteces_lw.item(index).text() ) )
		return vertexToSelect 

	@property
	def upperLidVerteces(self):
		"""docstring for upperLidVerteces"""
		vertexToSelect = []
		for index in xrange(self.upperLidsVerteces_lw.count()):
			vertexToSelect.append( str( self.upperLidsVerteces_lw.item(index).text() ) )
		return vertexToSelect

	def create(self):
		"""docstring for fname"""
		eyelids = eyeLids.EyeLidsRig( 
					topEyelidsVertexList = self.upperLidVerteces, 
					lowEyelidsVertexList = self.lowerLidVerteces, 
					centerPivot = str(self.centerPivot_le.text()) , 
					mirror = self.mirror_chb.isChecked(), 
					initialSide = 'L'
					)


def main():
	"""use this to create project in maya"""
	if mc.window( 'eyeLidsRigUi', q = 1, ex = 1 ):
		mc.deleteUI( 'eyeLidsRigUi' )
	PyForm=eyeLidsRigUi()
	PyForm.show()
