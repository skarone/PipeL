import os
import general.ui.pySideHelper as uiH
reload( uiH )
uiH.set_qt_bindings()
from Qt import QtGui,QtCore

import pipe.database.database as db

PYFILEDIR = os.path.dirname( os.path.abspath( __file__ ) )

uifile = PYFILEDIR + '/tasks.ui'
fom, base = uiH.loadUiType( uifile )

uiTaskfile = PYFILEDIR + '/TaskWidget.ui'
fomTask, baseTask = uiH.loadUiType( uiTaskfile )

class TaskUi(base, fom):
	def __init__(self,projectName, userName, parent  = uiH.getMayaWindow() ):
		if uiH.USEPYQT:
			super(base, self).__init__(parent)
		else:
			super(TaskUi, self).__init__(parent)
		self.setupUi(self)
		self.setObjectName( 'TaskUi' )
		self.project = projectName
		self.userName = userName
		if userName == "":
			return
		self.fillTasks()

	def fillTasks(self):
		"""fill tasks for project and user"""
		self.task_lw.clear()
		dataBase = db.ProjectDataBase( project )
		for a in dataBase.getAssetsForUser( self.userName ):
			itemN = QtGui.QListWidgetItem()
			self.task_lw.setItemWidget(itemN, TaskUi( a ) )

class TaskUi(baseTask, fomTask):
	def __init__(self, task, parent  = uiH.getMayaWindow() ):
		self.setupUi(self)
		self.taskName_lbl.setText( task.name )
		self.startDate_lbl.setText( task.startDate )
		self.endDate_lbl.setText( task.endDate )

def main():
	"""use this to create project in maya"""
	if mc.window( 'TaskUi', q = 1, ex = 1 ):
		mc.deleteUI( 'TaskUi' )
	PyForm=TaskUi()
	PyForm.show()
