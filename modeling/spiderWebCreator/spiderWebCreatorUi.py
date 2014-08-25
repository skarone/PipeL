'''
File: check.py
Author: Ignacio Urruty
Description: Create Spider webs
'''
import general.utils.utils as gutils
reload( gutils )

import general.ui.pySideHelper as uiH
reload( uiH )
uiH.set_qt_bindings()
from Qt import QtGui,QtCore

import modeling.spiderWebCreator.spiderWebCreator as spb
reload( spb )

import os
try:
	import general.mayaNode.mayaNode as mn
	import maya.OpenMayaUI as mui
	import maya.cmds as mc
	INMAYA = True
except:
	pass

#load UI FILE
PYFILEDIR = os.path.dirname( os.path.abspath( __file__ ) )

uifile = PYFILEDIR + '/spiderWebCreator.ui'
fom, base = uiH.loadUiType( uifile )


class spiderWebCreatorUi(base,fom):
	"""manager ui class"""
	def __init__(self, parent  = uiH.getMayaWindow(), *args ):
		if uiH.USEPYQT:
			super(base, self).__init__(parent)
		else:
			super(spiderWebCreatorUi, self).__init__(parent)
		self.setupUi(self)
		self._makeConnections()
		self.setObjectName( 'spiderWebCreatorUi_WIN' )

	def _makeConnections(self):
		"""create connection in the UI"""
		self.connect( self.create_btn, QtCore.SIGNAL("clicked()") , self.createSpiderWeb )

	def createSpiderWeb(self):
		"""create a spider web based on ui"""
		loops = self.loops_spb.value()
		spb.create( loops )

def main():
	"""use this to create project in maya"""
	if mc.window( 'spiderWebCreatorUi_WIN', q = 1, ex = 1 ):
		mc.deleteUI( 'spiderWebCreatorUi_WIN' )
	PyForm=spiderWebCreatorUi()
	PyForm.show()

