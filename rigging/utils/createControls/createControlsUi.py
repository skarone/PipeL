import os
import general.ui.pySideHelper as uiH
reload( uiH )
uiH.set_qt_bindings()
from Qt import QtGui,QtCore
import pipe.settings.settings as sti
reload( sti )
import rigging.utils.createControls.createControls as ctls
reload( ctls )
import maya.cmds as mc

PYFILEDIR = os.path.dirname( os.path.abspath( __file__ ) )

uifile = PYFILEDIR + '/createControlsUi.ui'
fom, base = uiH.loadUiType( uifile )


class ControlsUi(base,fom):
	def __init__(self, parent = None):
		if uiH.USEPYQT:
			super(base, self).__init__(uiH.getMayaWindow())
		else:
			super(ControlsUi, self).__init__(uiH.getMayaWindow())
		self.setupUi(self)
		self.setObjectName( 'ControlsUi' )
		self.settings = sti.Settings()
		gen = self.settings.General
		if gen:
			skin = gen[ "skin" ]
			if skin:
				uiH.loadSkin( self, skin )
		self.create_btn.clicked.connect(self.create)

	def create(self):
		"""create controls based on selection"""
		shape = str( self.shape_cmb.currentText())
		childsAlso = self.recursive_chb.isChecked()
		lastAlso = self.last_chb.isChecked()
		constraint = self.constraint_rb.isChecked()
		connect = self.connect_rb.isChecked()
		offsetGroup = self.offsetGroup_chb.isChecked()
		ctls.createControlsForSelection(shape ,childsAlso, None, lastAlso, constraint, connect, offsetGroup )

def main():
	"""use this to create project in maya"""
	global PyForm
	if mc.window( 'ControlsUi', q = 1, ex = 1 ):
		mc.deleteUI( 'ControlsUi' )
	PyForm=ControlsUi()
	PyForm.show()

