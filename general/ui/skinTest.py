import os
import general.ui.pySideHelper as uiH
reload( uiH )
uiH.set_qt_bindings()
from Qt import QtGui,QtCore
import maya.cmds as mc

PYFILEDIR = os.path.dirname( os.path.abspath( __file__ ) )

uifile = PYFILEDIR + '/skinTest.ui'
fom, base = uiH.loadUiType( uifile )


class SkinTestUI(base, fom):
	"""docstring for ProjectCreator"""
	def __init__(self, parent  = uiH.getMayaWindow(), *args ):
		if uiH.USEPYQT:
			super(base, self).__init__(parent)
		else:
			super(SkinTestUI, self).__init__(parent)
		self.setupUi(self)
		self.setObjectName( 'SkinTestUI' )
		uiH.loadSkin( self, 'QTDarkGreen' )

def main():
	"""use this to create project in maya"""
	if mc.window( 'SkinTestUI', q = 1, ex = 1 ):
		mc.deleteUI( 'SkinTestUI' )
	PyForm=SkinTestUI()
	PyForm.show()
