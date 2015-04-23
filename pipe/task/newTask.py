import os
import general.ui.pySideHelper as uiH
reload( uiH )
uiH.set_qt_bindings()
from Qt import QtGui,QtCore

INMAYA = True
try:
	import maya.cmds as mc
except:
	INMAYA = False
	pass

import pipe.database.database as db
reload( db )
import pipe.settings.settings as sti
reload( sti )
import pipe.project.project as prj
reload( prj )
import pipe.shot.shot as sht
import pipe.asset.asset as ass
import pipe.sequence.sequence as sq

import pipe.database.database as db
reload( db )

PYFILEDIR = os.path.dirname( os.path.abspath( __file__ ) )

uifile = PYFILEDIR + '/newTask.ui'
fom, base = uiH.loadUiType( uifile )

uiUserfile = PYFILEDIR + '/newUser.ui'
fomUser, baseUser = uiH.loadUiType( uiUserfile )

class NewTaskUi(base, fom):
	def __init__(self,projectName, user = '', parent  = uiH.getMayaWindow() ):
		if INMAYA:
			if uiH.USEPYQT:
				super(base, self).__init__(parent)
			else:
				super(NewTaskUi, self).__init__(parent)
		else:
			if uiH.USEPYQT:
				super(base, self).__init__(parent)
			else:
				super(NewTaskUi, self).__init__(parent)
		self.setupUi(self)
		self._user = user
		self.setObjectName( 'NewTaskUi' )
		self._makeConnections()
		self.settings = sti.Settings()
		self.projectName = projectName
		self.fillProjects()
		self.dataBase = db.ProjectDataBase( self.projectName )
		self.taskName_le.setVisible( False )
		self.fillUsers()
		self.fillTasks()
		self.fillStatus()
		self.settings = sti.Settings()
		skin = self.settings.General[ "skin" ]
		if skin:
			uiH.loadSkin( self, skin )

	def fillProjects(self):
		"""docstring for fillProjects"""
		projects = prj.projects( self.settings.General[ "serverpath" ] )
		self.projects_cmb.addItems( projects )
		index = self.projects_cmb.findText( self.projectName )
		if not index == -1:
			self.projects_cmb.setCurrentIndex(index)

	def fillStatus(self):
		"""docstring for fillStatus"""
		its = [ 'waitingStart', 'ready', 'inProgress', 'omit', 'paused', 'pendingReview', 'final' ]
		itsText = [ 'Waiting to Start', 'Ready to Start', 'In Progress', 'Omit', 'Paused', 'Pending Review','Final' ]
		for t,i in enumerate(its ):
			icon = QtGui.QIcon( PYFILEDIR + '/icons/' + i + '.png' )
			self.status_cmb.addItem( icon, itsText[t] )

	@property
	def database(self):
		"""docstring for database"""
		return db.ProjectDataBase( self.project.name )

	def fillUsers(self):
		"""docstring for fillUsers"""
		self.users_cmb.clear()
		self.users_cmb.addItems( self.dataBase.getUsers() )
		if not self._user == '':
			index = self.users_cmb.findText( self._user )
			self.users_cmb.setCurrentIndex( index )

	@property
	def project(self):
		"""docstring for project"""
		return prj.Project( str( self.projects_cmb.currentText() ), self.settings.General['serverpath'] )

	def fillTasks(self):
		"""docstring for fillTasks"""
		self.assets_cmb.clear()
		self.areas_cmb.clear()
		if self.isShot_chb.isChecked():
			self.assets_cmb.addItems( [a.name for a in self.project.sequences] )
			self.areas_cmb.addItems( sht.AREAS )
			self.fillShots()
		else:
			self.assets_cmb.addItems( [a.name for a in self.project.assets] )
			self.areas_cmb.addItems( ass.AREAS )

	def fillShots(self):
		"""docstring for updateShots"""
		self.shots_cmb.clear()
		self.shots_cmb.addItems( [a.name for a in sq.Sequence( self.asset, self.project ).shots ] )

	def _makeConnections(self):
		"""docstring for _makeConnections"""
		self.connect( self.newUser_btn    , QtCore.SIGNAL("clicked()") , self.newUser )
		self.connect( self.newAsset_btn   , QtCore.SIGNAL("clicked()") , self.newAsset )
		self.connect( self.createTask_btn , QtCore.SIGNAL("clicked()") , self.createTask )
		QtCore.QObject.connect( self.isShot_chb, QtCore.SIGNAL( "stateChanged  (int)" ), self.fillTasks )
		QtCore.QObject.connect( self.custom_chb, QtCore.SIGNAL( "stateChanged  (int)" ), self.setCustom )
		QtCore.QObject.connect( self.projects_cmb, QtCore.SIGNAL( "activated( const QString& )" ), self.setProject )
		QtCore.QObject.connect( self.assets_cmb, QtCore.SIGNAL( "activated( const QString& )" ), self.fillShots )

	def setProject(self):
		"""docstring for setProject"""
		self.dataBase = db.ProjectDataBase( self.project.name )
		self.fillUsers()
		self.fillTasks()

	def setCustom(self, state):
		"""docstring for setCustom"""
		self.assets_cmb.setVisible( not self.custom_chb.isChecked() )
		self.shots_cmb.setVisible( not self.custom_chb.isChecked() )
		self.shot_lbl.setVisible( not self.custom_chb.isChecked() )
		self.isShot_chb.setVisible( not self.custom_chb.isChecked() )
		self.areas_cmb.setVisible( not self.custom_chb.isChecked() )
		self.area_lbl.setVisible( not self.custom_chb.isChecked() )
		self.taskName_le.setVisible( self.custom_chb.isChecked() )

	@property
	def startDate(self):
		"""docstring for startDate"""
		return str( self.startDate_cal.selectedDate().toString( "dd-MM-yyyy" ) )

	@property
	def endDate(self):
		"""docstring for endDate"""
		return str( self.endDate_cal.selectedDate().toString( "dd-MM-yyyy" ) )

	@property
	def note(self):
		"""docstring for note"""
		return str( self.note_le.toPlainText())

	@property
	def user(self):
		"""docstring for user"""
		return str ( self.users_cmb.currentText() )

	@property
	def asset(self):
		"""this is the asset name or sequence name"""
		return str ( self.assets_cmb.currentText() )

	@property
	def shot(self):
		"""docstring for shot"""
		return str ( self.shots_cmb.currentText() )

	@property
	def area(self):
		"""docstring for area"""
		return str ( self.areas_cmb.currentText() )

	@property
	def priority(self):
		"""docstring for priority"""
		return self.priority_spb.value()

	@property
	def custom(self):
		"""docstring for custom"""
		return str( self.taskName_le.text() )
	
	@property
	def status(self):
		"""docstring for status"""
		return self.status_cmb.currentIndex()

	def newUser(self):
		"""docstring for newUser"""
		dia = NewUserUi( self )
		dia.show()
		res = dia.exec_()
		if res:
			self.fillUsers()

	def newAsset(self):
		"""docstring for newAsset"""
		print 'in newAsset'
		pass

	def createTask(self):
		"""docstring for createTask"""
		if self.custom_chb.isChecked():
			self.dataBase.addAsset( self.custom, '', '', self.user, self.priority, self.status, self.startDate, self.endDate )
		else:
			if self.isShot_chb.isChecked():
				self.dataBase.addAsset( self.shot, self.area, self.asset, self.user, self.priority, self.status, self.startDate, self.endDate )
			else:
				self.dataBase.addAsset( self.asset, self.area, '', self.user, self.priority, self.status, self.startDate, self.endDate )

class NewUserUi(baseUser, fomUser):
	"""docstring for NewUser"""
	def __init__(self, parent = None ):
		if uiH.USEPYQT:
			super(baseUser, self).__init__(parent)
		else:
			super(NewUserUi, self).__init__(parent)
		self.setupUi(self)
		self.connect(self.buttonBox, QtCore.SIGNAL("accepted()"), self.createUser)

	def createUser(self):
		"""docstring for createUser"""
		db.BaseDataBase().addUser( str( self.asset_le.text() ), str( self.mail_le.text() ), self.area_cmb.currentIndex() )

def main(projectname, user = ''):
	"""use this to create project in maya"""
	if INMAYA:
		if mc.window( 'NewTaskUi', q = 1, ex = 1 ):
			mc.deleteUI( 'NewTaskUi' )
	PyForm=NewTaskUi(projectname, user, parent=QtGui.QApplication.activeWindow())
	PyForm.show()

"""
import pipe.task.newTask as newTsk
reload( newTsk )
newTsk.main( 'Catsup_Tobogan' )
"""

