import os
import general.ui.pySideHelper as uiH
reload( uiH )
uiH.set_qt_bindings()
from Qt import QtGui,QtCore

import maya.cmds as mc

"""
import animation.poseMan.poseManUi as posUi
reload( posUi )

posUi.main()
"""

PYFILEDIR = os.path.dirname( os.path.abspath( __file__ ) )

uifile = PYFILEDIR + '/poseThumbnailUi.ui'
fom, base = uiH.loadUiType( uifile )

class PoseThumbnailUi(base, fom):
	def __init__(self, parent  = uiH.getMayaWindow() ):
		if uiH.USEPYQT:
			super(base, self).__init__(parent)
		else:
			super(PoseThumbnailUi, self).__init__(parent)
		self.setupUi(self)
		self.executer = mc.modelPanel( mbv = False, camera = 'Capture_Pose')
		mc.modelEditor(self.executer, e = True, grid = 0, da = "smoothShaded", allObjects = 0, nurbsSurfaces = 1, polymeshes = 1, subdivSurfaces = 1 )
		self.viewport_lay.addWidget( uiH.toQtObject( self.executer ) )
		self.setObjectName( 'PoseThumbnailUi' )

def main():
	"""use this to create project in maya"""
	if mc.window( 'PoseThumbnailUi', q = 1, ex = 1 ):
		mc.deleteUI( 'PoseThumbnailUi' )
	PyForm=PoseThumbnailUi()
	PyForm.show()
