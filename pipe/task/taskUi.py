import os
import general.ui.pySideHelper as uiH
reload( uiH )
uiH.set_qt_bindings()
from Qt import QtGui,QtCore
import pipe.task.newTask as newTsk
reload( newTsk )

import maya.cmds as mc

import pipe.database.database as db
reload( db )

PYFILEDIR = os.path.dirname( os.path.abspath( __file__ ) )

uifile = PYFILEDIR + '/TasksUi.ui'
fom, base = uiH.loadUiType( uifile )

uiNotefile = PYFILEDIR + '/NoteWidget.ui'
fomNote, baseNote = uiH.loadUiType( uiNotefile )

class TasksUi(base, fom):
	def __init__(self,projectName, parent  = uiH.getMayaWindow() ):
		if uiH.USEPYQT:
			super(base, self).__init__(parent)
		else:
			super(TasksUi, self).__init__(parent)
		self.setupUi(self)
		self.setObjectName( 'TasksUi' )
		self.project = projectName
		self.userName = None
		self.fillUsers()
		self.fillTasks()
		self._makeConnections()
		self.currentTask = None

	def fillUsers(self):
		"""docstring for fillUsers"""
		self.users_cmb.clear()
		self.users_cmb.addItems( db.ProjectDataBase( self.project ).getUsers() )

	def fillStatus(self):
		"""docstring for fillStatus"""
		its = { 'waitingStart':'Waiting to Start', 'ready':'Ready to Start', 'inProgress':'In Progress', 'omit':'Omit', 'paused':'Paused', 'pendingReview':'Pending Review', 'final':'Final' }
		for i in sorted( its.keys() ):
			icon = QtGui.QIcon( PYFILEDIR + '/icons/' + i + '.png' )
			self.taskStatus_cmb.addItem( icon, its[i] )

	def _makeConnections(self):
		"""docstring for _makeConnections"""
		QtCore.QObject.connect( self.users_cmb, QtCore.SIGNAL( "currentIndexChanged( const QString& )" ), self.fillTasks )
		QtCore.QObject.connect( self.tasks_tw, QtCore.SIGNAL( "itemClicked (QTableWidgetItem *)" ), self.updateTaskDataUi )
		self.connect( self.addNote_btn             , QtCore.SIGNAL("clicked()") , self.addNote )
		self.connect( self.newTask_btn             , QtCore.SIGNAL("clicked()") , self.newTask )
		self.connect( self.refresh_btn             , QtCore.SIGNAL("clicked()") , self.fillTasks )

	def newTask(self):
		"""docstring for newTask"""
		newTsk.main( self.project )

	@property
	def currentUser(self):
		"""docstring for currentUser"""
		return str ( self.users_cmb.currentText() )

	def addNote(self):
		"""add note to currentTask"""
		if not self.currentTask:
			return
		self.currentTask.addNote( db.ProjectDataBase( self.project ), str( self.note_te.toPlainText()), self.currentUser, self.currentTask.name, self.currentTask.area, self.currentTask.seq)
		self.updateNotes()
		self.note_te.clear()

	def fillTasks(self):
		"""fill tasks for project and user"""
		self.tasks_tw.clearContents()
		dataBase = db.ProjectDataBase( self.project )
		if not self.currentUser:
			return
		data = dataBase.getAssetsForUser( self.currentUser )
		self.tasks_tw.setRowCount( len( data ) )
		for i,a in enumerate(data):
			#NAME
			item = QtGui.QTableWidgetItem( a.fullname )
			item.setData(32, a )
			self.tasks_tw.setItem( i, 0, item )
			#USER
			item = QtGui.QTableWidgetItem( a.user )
			item.setData(32, a )
			self.tasks_tw.setItem( i, 1, item )
			#PRIORITY
			item = QtGui.QTableWidgetItem( a.priority )
			item.setData(32, a )
			self.tasks_tw.setItem( i, 2, item )
			#Status
			item = QtGui.QTableWidgetItem( a.status )
			item.setData(32, a )
			self.tasks_tw.setItem( i, 3, item )
			#Start DATE
			item = QtGui.QTableWidgetItem( a.timeStart )
			item.setData(32, a )
			self.tasks_tw.setItem( i, 4, item )
			#End DATE
			item = QtGui.QTableWidgetItem( a.timeEnd )
			item.setData(32, a )
			self.tasks_tw.setItem( i, 5, item )

	def updateTaskDataUi(self, item):
		if uiH.USEPYQT:
			taskItem = item.data(32).toPyObject()
		else:
			taskItem = item.data(32)
		self.currentTask = taskItem
		self.updateNotes()
		
	def updateNotes(self):
		if not self.currentTask:
			return
		self.note_lw.clear()
		for n in self.currentTask.notes(db.ProjectDataBase( self.project )):
			itemN = QtGui.QListWidgetItem()
			itemN.setData(32, n )
			itemN.setSizeHint(QtCore.QSize(200,70))
			self.note_lw.addItem( itemN )
			self.note_lw.setItemWidget(itemN, NoteUi( n ) )

	def changeTaskStatus(self):
		"""docstring for fname"""

class NoteUi(baseNote, fomNote):
	def __init__(self, note ):
		if uiH.USEPYQT:
			super(baseNote, self).__init__()
		else:
			super(NoteUi, self).__init__()
		self.setupUi(self)
		self.userName_lbl.setText( note.user )
		self.note_lbl.setText( note.note )
		self.noteDate_lbl.setText( note.date )

def main(projectName):
	"""use this to create project in maya"""
	if mc.window( 'TasksUi', q = 1, ex = 1 ):
		mc.deleteUI( 'TasksUi' )
	PyForm=TasksUi(projectName)
	PyForm.show()

"""
import pipe.task.taskUi as tskUi
reload(tskUi)
tskUi.main( 'Catsup_Tobogan' )
"""
