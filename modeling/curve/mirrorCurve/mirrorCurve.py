import os
import general.ui.pySideHelper as uiH
reload( uiH )
uiH.set_qt_bindings()
from Qt import QtGui,QtCore

import maya.cmds as mc
import general.mayaNode.mayaNode as mn

PYFILEDIR = os.path.dirname( os.path.abspath( __file__ ) )

uifile = PYFILEDIR + '/mirrorCurve.ui'
fom, base = uiH.loadUiType( uifile )

import modeling.curve.curve as crv


class MirrorCurveUi(base, fom):
	"""docstring for ProjectCreator"""
	def __init__(self, parent  = uiH.getMayaWindow(), *args ):
		if uiH.USEPYQT:
			super(base, self).__init__(parent)
		else:
			super(MirrorCurveUi, self).__init__(parent)
		self.setupUi(self)
		self.setObjectName( 'MirrorCurveUi' )
		self.connect(self.mirror_btn, QtCore.SIGNAL("clicked()"), self.mirror)

	def mirror(self):
		"""mirror select curve"""
		src = str( self.search_le.text() )
		replace = str( self.replace_le.text() )
		crv.copyVertexPositionForSelectedCurves( searchAndRelapce = [src, replace], mirrorAxis = 'x', worldSpace = True )
		


def main():
	"""use this to create project in maya"""
	if mc.window( 'MirrorCurveUi', q = 1, ex = 1 ):
		mc.deleteUI( 'MirrorCurveUi' )
	PyForm=MirrorCurveUi()
	PyForm.show()
