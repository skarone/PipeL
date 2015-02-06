import os
import general.ui.pySideHelper as uiH
reload( uiH )
uiH.set_qt_bindings()
from Qt import QtGui,QtCore

import pipe.database.database as db
reload( db )
import pipe.settings.settings as sti
reload( sti )
import pipe.project.project as prj
reload( prj )
import pipe.shot.shot as sht
import pipe.asset.asset as ass
import pipe.sequence.sequence as sq

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
		self.settings = sti.Settings()
		self.projectName = projectName
		self.dataBase = db.ProjectDataBase( self.projectName )
		self.fillUsers()
		self.fillTasks()
		self.fillStatus()

	def fillStatus(self):
		"""docstring for fillStatus"""
		its = { 'waitingStart':'Waiting to Start', 'ready':'Ready to Start', 'inProgress':'In Progress', 'omit':'Omit', 'paused':'Paused', 'pendingReview':'Pending Review', 'final':'Final' }
		for i in its.keys():
			icon = QtGui.QIcon( PYFILEDIR + '/icons/' + i + '.png' )
			self.status_cmb.addItem( icon, its[i] )

	def fillUsers(self):
		"""docstring for fillUsers"""
		self.users_cmb.clear()
		self.users_cmb.addItems( self.dataBase.getUsers() )

	@property
	def project(self):
		"""docstring for project"""
		return prj.Project( self.projectName, self.settings.General['serverpath'] )

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
		QtCore.QObject.connect( self.assets_cmb, QtCore.SIGNAL( "activated( const QString& )" ), self.fillShots )

	@property
	def startDate(self):
		"""docstring for startDate"""
		return self.startDate_cal.selectedDate().toString( "dd-MM-yyyy" ) 

	@property
	def endDate(self):
		"""docstring for endDate"""
		return self.endDate_cal.selectedDate().toString( "dd-MM-yyyy" ) 

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
	def status(self):
		"""docstring for status"""
		return self.shots_cmb.currentIndex()

	def newUser(self):
		"""docstring for newUser"""
		print 'in newUser'
		pass

	def newAsset(self):
		"""docstring for newAsset"""
		print 'in newAsset'
		pass

	def createTask(self):
		"""docstring for createTask"""
		if self.isShot_chb.isChecked():
			self.dataBase.addAsset( self.shot, self.area, self.asset, self.user, self.priority, self.status, self.startDate, self.endDate )
		else:
			self.dataBase.addAsset( self.asset, self.area, '', self.user, self.priority, self.status, self.startDate, self.endDate )
		print self.startDate, self.endDate
		print self.user
		print self.note
		print 'in createTask'
		pass

def main(projectname):
	"""use this to create project in maya"""
	if mc.window( 'NewTaskUi', q = 1, ex = 1 ):
		mc.deleteUI( 'NewTaskUi' )
	PyForm=NewTaskUi(projectname)
	PyForm.show()

"""
import pipe.task.newTask as newTsk
reload( newTsk )
newTsk.main( 'Catsup_Tobogan' )
"""

