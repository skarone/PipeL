import os
import general.ui.pySideHelper as uiH
reload( uiH )
uiH.set_qt_bindings()
from Qt import QtGui,QtCore

import maya.cmds as mc

import pipe.database.database as db
reload( db )

PYFILEDIR = os.path.dirname( os.path.abspath( __file__ ) )

uifile = PYFILEDIR + '/newTask.ui'
fom, base = uiH.loadUiType( uifile )

class NewTaskUi(base, fom):
	def __init__(self,projectName, parent  = uiH.getMayaWindow() ):
		if uiH.USEPYQT:
			super(base, self).__init__(parent)
		else:
			super(NewTaskUi, self).__init__(parent)
		self.setupUi(self)
		self.setObjectName( 'NewTaskUi' )
		self._makeConnections()
	
	def _makeConnections(self):
		"""docstring for _makeConnections"""
		pass

def main():
	"""docstring for manin"""

def main(projectname):
	"""use this to create project in maya"""
	if mc.window( 'NewTaskUi', q = 1, ex = 1 ):
		mc.deleteUI( 'NewTaskUi' )
	PyForm=NewTaskUi(projectname)
	PyForm.show()


