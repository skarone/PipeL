import os
import general.ui.pySideHelper as uiH
reload( uiH )
uiH.set_qt_bindings()
from Qt import QtGui,QtCore

import maya.cmds as mc

import pipe.database.database as db
reload( db )

PYFILEDIR = os.path.dirname( os.path.abspath( __file__ ) )

uifile = PYFILEDIR + '/tasks.ui'
fom, base = uiH.loadUiType( uifile )

uiTaskfile = PYFILEDIR + '/TaskWidget.ui'
fomTask, baseTask = uiH.loadUiType( uiTaskfile )

uiNotefile = PYFILEDIR + '/NoteWidget.ui'
fomNote, baseNote = uiH.loadUiType( uiNotefile )

class TasksUi(base, fom):
	def __init__(self,projectName, userName, parent  = uiH.getMayaWindow() ):
		if uiH.USEPYQT:
			super(base, self).__init__(parent)
		else:
			super(TasksUi, self).__init__(parent)
		self.setupUi(self)
		self.setObjectName( 'TasksUi' )
		self.project = projectName
		self.userName = userName
		if userName == "":
			return
		self.fillTasks()
		self._makeConnections()

	def _makeConnections(self):
		"""docstring for _makeConnections"""
		QtCore.QObject.connect( self.task_lw, QtCore.SIGNAL( "itemClicked( QListWidgetItem* )" ), self.updateTaskDataUi )

	def fillTasks(self):
		"""fill tasks for project and user"""
		self.task_lw.clear()
		dataBase = db.ProjectDataBase( self.project )
		for a in dataBase.getAssetsForUser( self.userName ):
			itemN = QtGui.QListWidgetItem()
			itemN.setData(32, a )
			itemN.setSizeHint(QtCore.QSize(200,70));
			self.task_lw.addItem( itemN )
			self.task_lw.setItemWidget(itemN, TaskUi( a ) )

	def updateTaskDataUi(self):
		item = self.task_lw.selectedItems()[0]
		if uiH.USEPYQT:
			taskItem = item.data(32).toPyObject()
		else:
			taskItem = item.data(32)
		self.note_lw.clear()
		self.priority_val_lbl.setText( str( taskItem.priority ) )
		self.startDate_lbl.setText( taskItem.timeStart )
		self.endDate_lbl.setText( taskItem.timeEnd )
		self.taskName_lbl.setText( taskItem.name )
		for n in taskItem.notes:
			itemN = QtGui.QListWidgetItem()
			itemN.setData(32, n )
			itemN.setSizeHint(QtCore.QSize(200,70))
			self.note_lw.addItem( itemN )
			self.note_lw.setItemWidget(itemN, NoteUi( n ) )

class TaskUi(baseTask, fomTask):
	def __init__(self, task ):
		if uiH.USEPYQT:
			super(baseTask, self).__init__()
		else:
			super(TaskUi, self).__init__()
		self.setupUi(self)
		self.taskName_lbl.setText( task.name )
		self.startDate_lbl.setText( task.timeStart )
		self.endDate_lbl.setText( task.timeEnd )

class NoteUi(baseNote, fomNote):
	def __init__(self, note ):
		if uiH.USEPYQT:
			super(baseNote, self).__init__()
		else:
			super(NoteUi, self).__init__()
		self.setupUi(self)
		self.userName_lbl.setText( note.user )
		self.note_lbl.setText( note.note )

def main(projectName, userName):
	"""use this to create project in maya"""
	if mc.window( 'TasksUi', q = 1, ex = 1 ):
		mc.deleteUI( 'TasksUi' )
	PyForm=TasksUi(projectName, userName)
	PyForm.show()
