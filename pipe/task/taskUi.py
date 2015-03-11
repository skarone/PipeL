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
		self.settings = sti.Settings()
		self._makeConnections()
		self.currentTask = None
		self.tasks_tw.setContextMenuPolicy(QtCore.Qt.CustomContextMenu)
		self.tasks_tw.customContextMenuRequested.connect(self.showMenu)
		skin = self.settings.General[ "skin" ]
		if skin:
			uiH.loadSkin( self, skin )

	def showMenu(self, pos):
		menu=QtGui.QMenu(self)
		propIcon = QtGui.QIcon( PYFILEDIR + '/icons/question.png' )
		actionProperties = QtGui.QAction(propIcon, "Properties", menu)
		menu.addAction( actionProperties )
		self.connect( actionProperties, QtCore.SIGNAL( "triggered()" ), self.properties )
		folderIcon = QtGui.QIcon( PYFILEDIR + '/icons/folder.png' )
		actionOpenInExplorer = QtGui.QAction(folderIcon,"Open File in explorer", menu)
		menu.addAction( actionOpenInExplorer )
		self.connect( actionOpenInExplorer, QtCore.SIGNAL( "triggered()" ), self.openFileLocation )
		#COPY PATH
		actionSaveScene = QtGui.QAction("Copy File Path", menu)
		menu.addAction( actionSaveScene )
		self.connect( actionSaveScene, QtCore.SIGNAL( "triggered()" ), self.copyFilePath )
		#OPEN RENDER PATH
		actionSaveScene = QtGui.QAction(folderIcon,"Open Render Folder", menu)
		menu.addAction( actionSaveScene )
		self.connect( actionSaveScene, QtCore.SIGNAL( "triggered()" ), self.openRenderFolder )
		menu.addSeparator()
		#DOWNLOAD UPLOAD
		downIcon = QtGui.QIcon( PYFILEDIR + '/icons/download.png' )
		uploIcon = QtGui.QIcon( PYFILEDIR + '/icons/upload.png' )
		actionCopyServer = QtGui.QAction( downIcon, "Download From Server", menu)
		actionCopyServer.setIcon( downIcon )
		menu.addAction(actionCopyServer)
		self.connect( actionCopyServer, QtCore.SIGNAL( "triggered()" ), self.copyFromServer )
		actionToServer = QtGui.QAction( uploIcon, "Upload To Server", menu)
		menu.addAction(actionToServer)
		self.connect( actionToServer, QtCore.SIGNAL( "triggered()" ), self.copyToServer )
		menu.addSeparator()
		if INMAYA:
			#OPEN IN CURRENT MAYA
			mayaIcon = QtGui.QIcon( PYFILEDIR + '/icons/maya.png' )
			actionOpenInCurrent = QtGui.QAction(mayaIcon,"Open in This Maya", menu)
			menu.addAction( actionOpenInCurrent )
			self.connect( actionOpenInCurrent, QtCore.SIGNAL( "triggered()" ), self.openFileInCurrentMaya )
			menu.addSeparator()
			#IMPORT
			impIcon = QtGui.QIcon( PYFILEDIR + '/icons/import.png' )
			actionImport = QtGui.QAction(impIcon,"Import", menu)
			menu.addAction( actionImport )
			self.connect( actionImport, QtCore.SIGNAL( "triggered()" ), self.importFile )
			menu.addSeparator()
			#COPY TIME SETTINGS
			timeIcon = QtGui.QIcon( PYFILEDIR + '/icons/time.png' )
			actionCopyTime = QtGui.QAction(timeIcon,"Copy Time Settings", menu)
			menu.addAction( actionCopyTime )
			self.connect( actionCopyTime, QtCore.SIGNAL( "triggered()" ), self.copyTimeSettings )
			menu.addSeparator()
			#REFERENCE
			refIcon = QtGui.QIcon( PYFILEDIR + '/icons/reference.png' )
			actionReference = QtGui.QAction(refIcon,"Reference", menu)
			menu.addAction( actionReference )
			self.connect( actionReference, QtCore.SIGNAL( "triggered()" ), self.reference )
			menu.addSeparator()
			#SAVE IN THIS SCENE
			savIcon = QtGui.QIcon( PYFILEDIR + '/icons/save.png' )
			actionSaveScene = QtGui.QAction(savIcon,"Save Scene Here!", menu)
			menu.addAction( actionSaveScene )
			self.connect( actionSaveScene, QtCore.SIGNAL( "triggered()" ), self.saveScene )
		elif INNUKE:
			#OPEN IN CURRENT MAYA
			nukIcon = QtGui.QIcon( PYFILEDIR + '/icons/nuke.png' )
			actionOpenInCurrent = QtGui.QAction(nukIcon,"Open in This Nuke", menu)
			menu.addAction( actionOpenInCurrent )
			self.connect( actionOpenInCurrent, QtCore.SIGNAL( "triggered()" ), self.openFileInCurrentNuke )
			#SAVE IN THIS SCENE
			savIcon = QtGui.QIcon( PYFILEDIR + '/icons/save.png' )
			actionSaveScene = QtGui.QAction(savIcon,"Save Scene Here!", menu)
			menu.addAction( actionSaveScene )
			self.connect( actionSaveScene, QtCore.SIGNAL( "triggered()" ), self.saveNukeScene )
		menu.popup(self.tasks_tw.viewport().mapToGlobal(pos))

	#MENU FUNCTIONS
	def copyFilePath(self):
		"""docstring for copyFilePath"""
		assetPath = self.getAssetFromTaks()
		if assetPath:
			command = 'echo ' + assetPath.path + '| clip'
			os.popen(command)

	def openFile(self,item):
		"""open selected Asset"""
		asset = self.getAssetFromTaks()
		os.system("start "+ str( asset.path ) )

	def properties(self):
		"""get ui with properties of asset"""
		asset = self.getAssetFromTaks()
		if asset.extension == '.ma':
			props = mfp.MayaFilePropertiesUi(asset,self, False )
		elif asset.extension == '.nk':
			props = nkp.NukeFilePropertiesUi(asset,self, False)
		props.show()

	def openFileLocation(self):
		"""openFile in explorer"""
		asset = self.getAssetFromTaks()
		subprocess.Popen(r'explorer /select,"'+ asset.path.replace( '/','\\' ) +'"')

	def saveScene(self):
		"""save scene here"""
		quit_msg = "Are you sure you want to save in this file?"
		reply = QtGui.QMessageBox.question(self, 'Message', quit_msg, QtGui.QMessageBox.Yes, QtGui.QMessageBox.No)
		if reply == QtGui.QMessageBox.Yes:
			asset = self.getAssetFromTaks()
			asset.newVersion()
			asset.save()

	def openRenderFolder(self):
		"""docstring for openRenderFolder"""
		asset = self.getAssetFromTaks()
		if not asset:
			return
		assOrShot = prj.shotOrAssetFromFile( asset )
		if assOrShot:
			if assOrShot.type == 'asset':
				#versionNumber = self._getVersionNumber( renderPath + assOrShot.project.name + '/Asset/' + assOrShot.name )
				pat = self.settings.General[ 'renderpath' ] + assOrShot.project.name + '/Asset/' + assOrShot.name + '/'
			elif assOrShot.type == 'shot':
				#R:\Pony_Halloween_Fantasmas\Terror\s013_T13\Chicos_Beauty
				#versionNumber = self._getVersionNumber( renderPath + assOrShot.project.name + '/' + assOrShot.sequence.name + '/' + assOrShot.name )
				pat =  self.settings.General[ 'renderpath' ] + assOrShot.project.name + '/' + assOrShot.sequence.name + '/' + assOrShot.name + '/'
			subprocess.Popen(r'explorer "'+ pat.replace( '/','\\' ) +'"')

	def importFile(self):
		"""import file to current Maya"""
		asset = self.getAssetFromTaks()
		if not asset:
			return
		asset.imp()

	def copyTimeSettings(self):
		"""copy time settings from selected scene"""
		asset = self.getAssetFromTaks()
		if not asset:
			return
		tim = asset.time
		mc.currentUnit( time=tim['tim'], linear = tim['lin'], angle = tim[ 'angle' ] )
		mc.playbackOptions( min = tim[ 'min' ],
							ast = tim[ 'ast' ], 
							max = tim[ 'max' ], 
							aet = tim[ 'aet' ] )

	def reference(self):
		"""reference file into scene"""
		asset = self.getAssetFromTaks()
		if not asset:
			return
		#TODO HERE WE NEED TO DETECT IF WE ARE IN A SHOT
		gen = self.settings.General
		assetPerShot = gen[ "useassetspershot" ]
		if assetPerShot == 'True':
			shotSel = prj.shotOrAssetFromFile( mfl.currentFile() )
			#assetspath + assetname + department + file
			newFil = asset.copy( shotSel.assetsPath + asset.path.split( 'Assets/' )[-1] )
			newFil.reference()
		else:
			asset.reference()

	def saveNukeScene(self):
		"""docstring for saveNukeScene"""
		asset = self.getAssetFromTaks()
		if not asset:
			return
		asset.newVersion()
		asset.save()

	def openFileInCurrentMaya(self):
		"""docstring for openFileInCurrentMaya"""
		asset = self.getAssetFromTaks()
		if not asset:
			return
		if asset.isZero:
			mc.file( new = True, force = True )
			asset.save()
		else:
			asset.open()

	def copyFromServer(self):
		"""copy selected asset from server"""
		asset = self.getAssetFromTaks()
		if not asset:
			return
		self.copyAssetFromServer( asset )
		self.updateUi()

	def copyToServer(self):
		"""copy selected asset to server"""
		quit_msg = "Are you sure you want to copy this file to SERVER?"
		reply = QtGui.QMessageBox.question(self, 'Message', quit_msg, QtGui.QMessageBox.Yes, QtGui.QMessageBox.No)
		if reply == QtGui.QMessageBox.Yes:
			asset = self.getAssetFromTaks()
			if not asset:
				return
			self.copyAssetToServer( asset )
			self.updateUi()

	def getAssetFromTaks(self):
		"""docstring for getAssetFromTaks"""
		if self.currentTask.seq == '':
			return prj.Project( self.project, self.settings.General[ 'serverpath' ] ).getAssetPath( self.currentTask.name, self.currentTask.area )
		else:
			return prj.Project( self.project, self.settings.General[ 'serverpath' ] ).getShotPath( self.currentTask.seq, self.currentTask.name, self.currentTask.area )

	#END MENU FUNCTIONS

	def fillUsers(self):
		"""docstring for fillUsers"""
		self.users_cmb.clear()
		if self.project == 'All':
			self.users_cmb.addItems( [ 'All' ] )
			users = []
			for p in prj.projects( self.settings.General[ 'serverpath' ] ):
				users.extend( db.ProjectDataBase( p ).getUsers() )
			print list(set( users ))
			self.users_cmb.addItems( list(set( users )) )
		else:
			self.users_cmb.addItems( ['All'] + db.ProjectDataBase( self.project ).getUsers() )

	def fillUsersNote(self):
		"""docstring for fillUsersNote"""
		self.usersNote_cmb.clear()
		if self.project == 'All':
			users = []
			for p in prj.projects( self.settings.General[ 'serverpath' ] ):
				users.extend( db.ProjectDataBase( p ).getUsers() )
			self.usersNote_cmb.addItems( list(set( users )) )
		else:
			self.usersNote_cmb.addItems( [' '] + db.ProjectDataBase( self.project ).getUsers() )

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
		data = {}
		if self.project == 'All':
			for p in prj.projects( self.settings.General[ 'serverpath' ] ):
				dataBase = db.ProjectDataBase( p )
				if dataBase.exists:
					data[ p ] = []
					if not self.currentUser:
						return
					if self.currentUser == 'All':
						for u in dataBase.getUsers():
							data[ p ].extend(dataBase.getAssetsForUser( u ))
					else:
						data[ p ].extend( dataBase.getAssetsForUser( self.currentUser ) )
		else:
			dataBase = db.ProjectDataBase( self.project )
			if not self.currentUser:
				return
			if self.currentUser == 'All':
				data[self.project] = []
				for u in dataBase.getUsers():
					data[self.project].extend(dataBase.getAssetsForUser( u ))
			else:
				data[self.project] = dataBase.getAssetsForUser( self.currentUser )
		dataLen = 0
		for d in data.keys():
			dataLen += len( data[d] )
		self.tasks_tw.setRowCount( dataLen )
		self.mapper = QtCore.QSignalMapper(self)
		i = 0
		for d in data.keys():
			dataBase = db.ProjectDataBase( d )
			for a in data[d]:
				#NAME
				tmpA = a
				item = QtGui.QTableWidgetItem( a.fullname )
				item.setData(32, a )
				self.tasks_tw.setItem( i, 0, item )
				#USER
				cmbStatus = QtGui.QComboBox()
				cmbStatus.addItems( dataBase.getUsers() )
				index = cmbStatus.findText( a.user )
				if not index == -1:
					cmbStatus.setCurrentIndex(index)
				item = QtGui.QTableWidgetItem( a.user )
				self.tasks_tw.setItem( i, 1, item )
				self.tasks_tw.setCellWidget(i,1, cmbStatus);
				self.connect( cmbStatus, QtCore.SIGNAL("currentIndexChanged( const int& )" ), self.mapper, QtCore.SLOT("map()") )
				self.mapper.setMapping(cmbStatus, i)
				#PROJECT
				item = QtGui.QTableWidgetItem( d )
				item.setData(32, a )
				self.tasks_tw.setItem( i, 2, item )
				#PRIORITY
				spin = QtGui.QSpinBox()
				spin.setValue( a.priority )
				spin.setRange( 0, 100 )
				item = QtGui.QTableWidgetItem( str( a.priority ) )
				self.tasks_tw.setItem( i, 3, item )
				self.tasks_tw.setCellWidget(i,3, spin);
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
				self.tasks_tw.setItem( i, 4, item )
				self.tasks_tw.setCellWidget(i,4, cmbStatus);
				self.connect( cmbStatus, QtCore.SIGNAL("currentIndexChanged( const int& )" ), self.mapper, QtCore.SLOT("map()") )
				self.mapper.setMapping(cmbStatus, i)
				#Start DATE
				dsplit =  a.timeStart.split( '-' )
				if '-' in a.timeStart:
					date = QtGui.QDateEdit( QtCore.QDate( int(dsplit[2]),int(dsplit[1]),int(dsplit[0]) ))
				else:
					date = QtGui.QDateEdit()
				date.setCalendarPopup(True)
				item = QtGui.QTableWidgetItem( a.timeStart )
				self.tasks_tw.setItem( i, 5, item )
				self.tasks_tw.setCellWidget(i,5, date);
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
				self.tasks_tw.setItem( i, 6, item )
				self.tasks_tw.setCellWidget(i,6, date);
				self.connect( date, QtCore.SIGNAL("dateChanged( const QDate& )" ), self.mapper, QtCore.SLOT("map()") )
				self.mapper.setMapping(date, i)
				i += 1
		self.mapper.mapped.connect(self.updateTask)

	def updateTask(self, row):
		"""docstring for updateTask"""
		tas = self._getTaskByRowIndex( row )
		print row
		user, priority, status, timeStart, timeEnd, project = self._taskDataFromUi( row )
		data = db.ProjectDataBase( project )
		print 'UPDATING', tas.name, tas.area, tas.seq
		print user, priority, status, timeStart, timeEnd
		data.updateAsset( tas.name, tas.area, tas.seq, user, priority, status, timeStart, timeEnd )
		#print tas.user, tas.timeStart, tas.timeEnd
		#print 'in updateTask'

	def _taskDataFromUi(self, row):
		"""docstring for _taskDataFromUi"""
		wid = self.tasks_tw.cellWidget( row, 1 )
		user = str( wid.currentText() )
		wid = self.tasks_tw.cellWidget( row, 3 )
		priority = wid.value()
		wid = self.tasks_tw.cellWidget( row, 4 )
		status = wid.currentIndex()
		wid = self.tasks_tw.cellWidget( row, 5 )
		print user, priority, status
		startDate = str( wid.date().toString( "dd-MM-yyyy" ) )
		wid = self.tasks_tw.cellWidget( row, 6 )
		endDate = str( wid.date().toString( "dd-MM-yyyy" ) )
		project =  self.tasks_tw.item( row, 2 ).text()
		return user, priority, status, startDate, endDate, project

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
		self.project = self.tasks_tw.item( item.row(), 2 ).text()
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
