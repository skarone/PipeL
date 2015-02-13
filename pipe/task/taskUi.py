import os
import general.ui.pySideHelper as uiH
reload( uiH )
uiH.set_qt_bindings()
from Qt import QtGui,QtCore
import pipe.task.newTask as newTsk
reload( newTsk )

import pipe.project.project as prj
import pipe.settings.settings as sti
reload( sti )
INMAYA = True
try:
	import maya.cmds as mc
except:
	INMAYA = False
	pass

import pipe.database.database as db
reload( db )

PYFILEDIR = os.path.dirname( os.path.abspath( __file__ ) )

uifile = PYFILEDIR + '/TasksUi.ui'
fom, base = uiH.loadUiType( uifile )

uiNotefile = PYFILEDIR + '/NoteWidget.ui'
fomNote, baseNote = uiH.loadUiType( uiNotefile )

class TasksUi(base, fom):
	def __init__(self,projectName, parent  = uiH.getMayaWindow() ):
		if INMAYA:
			if uiH.USEPYQT:
				super(base, self).__init__(parent)
			else:
				super(TasksUi, self).__init__(parent)
		else:
			if uiH.USEPYQT:
				super(base, self).__init__()
			else:
				super(TasksUi, self).__init__()
		self.setupUi(self)
		self.setObjectName( 'TasksUi' )
		self.project = projectName
		self.userName = None
		self.fillUsers()
		self.fillUsersNote()
		self.fillTasks()
		self._makeConnections()
		self.currentTask = None
		self.settings = sti.Settings()
		skin = self.settings.General[ "skin" ]
		if skin:
			uiH.loadSkin( self, skin )

	def fillUsers(self):
		"""docstring for fillUsers"""
		self.users_cmb.clear()
		self.users_cmb.addItems( ['All'] + db.ProjectDataBase( self.project ).getUsers() )

	def fillUsersNote(self):
		"""docstring for fillUsersNote"""
		self.usersNote_cmb.clear()
		self.usersNote_cmb.addItems( db.ProjectDataBase( self.project ).getUsers() )

	def fillStatus(self, widget):
		"""docstring for fillStatus"""
		its = [ 'waitingStart', 'ready', 'inProgress', 'omit', 'paused', 'pendingReview', 'final' ]
		itsText = [ 'Waiting to Start', 'Ready to Start', 'In Progress', 'Omit', 'Paused', 'Pending Review','Final' ]
		for t,i in enumerate(its ):
			icon = QtGui.QIcon( PYFILEDIR + '/icons/' + i + '.png' )
			widget.addItem( icon, itsText[t] )

	def _makeConnections(self):
		"""docstring for _makeConnections"""
		QtCore.QObject.connect( self.users_cmb, QtCore.SIGNAL( "currentIndexChanged( const QString& )" ), self.fillTasks )
		QtCore.QObject.connect( self.tasks_tw, QtCore.SIGNAL( "itemClicked (QTableWidgetItem *)" ), self.updateTaskDataUi )
		self.connect( self.addNote_btn             , QtCore.SIGNAL("clicked()") , self.addNote )
		self.connect( self.newTask_btn             , QtCore.SIGNAL("clicked()") , self.newTask )
		self.connect( self.refresh_btn             , QtCore.SIGNAL("clicked()") , self.refresh )

	def refresh(self):
		"""docstring for refresh"""
		self.fillUsers()
		self.fillUsersNote()
		self.fillTasks()

	def newTask(self):
		"""docstring for newTask"""
		user = ''
		if not self.currentUser == 'All':
			user = self.currentUser
		newTsk.main( self.project, user )

	@property
	def currentUser(self):
		"""docstring for currentUser"""
		return str ( self.users_cmb.currentText() )

	def setUser(self, user):
		"""docstring for setUser"""
		index = self.users_cmb.findText( user )
		if not index == -1:
			self.users_cmb.setCurrentIndex(index)

	def setUserNote(self, user):
		"""docstring for setUserNote"""
		index = self.usersNote_cmb.findText( user )
		if not index == -1:
			self.usersNote_cmb.setCurrentIndex(index)

	@property
	def currentUserNote(self):
		"""docstring for currentUserNote"""
		return str ( self.usersNote_cmb.currentText() )

	def addNote(self):
		"""add note to currentTask"""
		if not self.currentTask:
			return
		self.currentTask.addNote( db.ProjectDataBase( self.project ), str( self.note_te.toPlainText()), self.currentUserNote, self.currentTask.name, self.currentTask.area, self.currentTask.seq)
		self.updateNotes()
		self.note_te.clear()

	def fillTasks(self):
		"""fill tasks for project and user"""
		self.tasks_tw.clearContents()
		dataBase = db.ProjectDataBase( self.project )
		if not self.currentUser:
			return
		if self.currentUser == 'All':
			data = []
			for u in db.ProjectDataBase( self.project ).getUsers():
				data.extend(dataBase.getAssetsForUser( u ))
		else:
			data = dataBase.getAssetsForUser( self.currentUser )
		self.tasks_tw.setRowCount( len( data ) )
		self.mapper = QtCore.QSignalMapper(self)
		for i,a in enumerate(data):
			#NAME
			tmpA = a
			item = QtGui.QTableWidgetItem( a.fullname )
			item.setData(32, a )
			self.tasks_tw.setItem( i, 0, item )
			#USER
			cmbStatus = QtGui.QComboBox()
			cmbStatus.addItems( db.ProjectDataBase( self.project ).getUsers() )
			index = cmbStatus.findText( a.user )
			if not index == -1:
				cmbStatus.setCurrentIndex(index)
			item = QtGui.QTableWidgetItem( a.user )
			self.tasks_tw.setItem( i, 1, item )
			self.tasks_tw.setCellWidget(i,1, cmbStatus);
			self.connect( cmbStatus, QtCore.SIGNAL("currentIndexChanged( const int& )" ), self.mapper, QtCore.SLOT("map()") )
			self.mapper.setMapping(cmbStatus, i)
			#PRIORITY
			spin = QtGui.QSpinBox()
			spin.setValue( a.priority )
			spin.setRange( 0, 100 )
			item = QtGui.QTableWidgetItem( str( a.priority ) )
			self.tasks_tw.setItem( i, 2, item )
			self.tasks_tw.setCellWidget(i,2, spin);
			self.connect( spin, QtCore.SIGNAL("valueChanged( const int& )" ), self.mapper, QtCore.SLOT("map()") )
			self.mapper.setMapping(spin, i)
			#Status
			item = QtGui.QTableWidgetItem( str( a.status ) )
			cmbStatus = QtGui.QComboBox()
			self.fillStatus( cmbStatus )
			its = [ 'Waiting to Start', 'Ready to Start', 'In Progress', 'Omit', 'Paused', 'Pending Review', 'Final' ]
			index = cmbStatus.findText( its[ a.status ] )
			if not index == -1:
				cmbStatus.setCurrentIndex(index)
			self.tasks_tw.setItem( i, 3, item )
			self.tasks_tw.setCellWidget(i,3, cmbStatus);
			self.connect( cmbStatus, QtCore.SIGNAL("currentIndexChanged( const int& )" ), self.mapper, QtCore.SLOT("map()") )
			self.mapper.setMapping(cmbStatus, i)
			#Start DATE
			dsplit =  a.timeStart.split( '-' )
			print a.timeStart
			if '-' in a.timeStart:
				date = QtGui.QDateEdit( QtCore.QDate( int(dsplit[2]),int(dsplit[1]),int(dsplit[0]) ))
			else:
				date = QtGui.QDateEdit()
			date.setCalendarPopup(True)
			item = QtGui.QTableWidgetItem( a.timeStart )
			self.tasks_tw.setItem( i, 4, item )
			self.tasks_tw.setCellWidget(i,4, date);
			self.connect( date, QtCore.SIGNAL("dateChanged( const QDate& )" ), self.mapper, QtCore.SLOT("map()") )
			self.mapper.setMapping(date, i)
			#End DATE
			dsplit =  a.timeEnd.split( '-' )
			if '-' in a.timeEnd:
				date = QtGui.QDateEdit( QtCore.QDate( int(dsplit[2]),int(dsplit[1]),int(dsplit[0]) ))
			else:
				date = QtGui.QDateEdit()
			date.setCalendarPopup(True)
			item = QtGui.QTableWidgetItem( a.timeEnd )
			self.tasks_tw.setItem( i, 5, item )
			self.tasks_tw.setCellWidget(i,5, date);
			self.connect( date, QtCore.SIGNAL("dateChanged( const QDate& )" ), self.mapper, QtCore.SLOT("map()") )
			self.mapper.setMapping(date, i)
		self.mapper.mapped.connect(self.updateTask)

	def updateTask(self, row):
		"""docstring for updateTask"""
		tas = self._getTaskByRowIndex( row )
		data = db.ProjectDataBase( self.project )
		user, priority, status, timeStart, timeEnd = self._taskDataFromUi( row )
		print 'UPDATING', tas.name, tas.area, tas.seq
		print user, priority, status, timeStart, timeEnd
		data.updateAsset( tas.name, tas.area, tas.seq, user, priority, status, timeStart, timeEnd )
		#print tas.user, tas.timeStart, tas.timeEnd
		#print 'in updateTask'

	def _taskDataFromUi(self, row):
		"""docstring for _taskDataFromUi"""
		wid = self.tasks_tw.cellWidget( row, 1 )
		user = str( wid.currentText() )
		wid = self.tasks_tw.cellWidget( row, 2 )
		priority = wid.value()
		wid = self.tasks_tw.cellWidget( row, 3 )
		status = wid.currentIndex()
		wid = self.tasks_tw.cellWidget( row, 4 )
		startDate = str( wid.date().toString( "dd-MM-yyyy" ) )
		wid = self.tasks_tw.cellWidget( row, 5 )
		endDate = str( wid.date().toString( "dd-MM-yyyy" ) )
		return user, priority, status, startDate, endDate

	def _getTaskByRowIndex(self, row):
		"""docstring for _getTaskByRowIndex"""
		item = self.tasks_tw.item( row, 0 )
		if uiH.USEPYQT:
			asset = item.data(32).toPyObject()
		else:
			asset = item.data(32)
		return asset

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
	if INMAYA:
		if mc.window( 'TasksUi', q = 1, ex = 1 ):
			mc.deleteUI( 'TasksUi' )
	PyForm=TasksUi(projectName)
	PyForm.show()

"""
import pipe.task.taskUi as tskUi
reload(tskUi)
tskUi.main( 'Catsup_Tobogan' )
"""
