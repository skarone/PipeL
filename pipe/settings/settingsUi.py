import os
import general.ui.pySideHelper as uiH
reload( uiH )
from Qt import QtGui,QtCore
import pipe.settings.settings as sti
reload( sti )

PYFILEDIR = os.path.dirname( os.path.abspath( __file__ ) )

uifile = PYFILEDIR + '/settings.ui'
fom, base = uiH.loadUiType( uifile )


class Settings(base, fom):
	"""docstring for ProjectCreator"""
	def __init__(self, parent = None):
		if uiH.USEPYQT:
			super(base, self).__init__(parent)
		else:
			super(Settings, self).__init__(parent)
		self.setupUi(self)
		self._makeConection()
		self.settings = sti.Settings()
		self.skin_cmb.addItems( sti.SKINS )
		self._loadConfig()

	def _makeConection(self):
		"""docstring for _makeConection"""
		self.connect(self.localPath_btn, QtCore.SIGNAL("clicked()"), self.setLocal)
		self.connect(self.serverPath_btn, QtCore.SIGNAL("clicked()"), self.setServer)
		self.connect(self.renderPath_btn, QtCore.SIGNAL("clicked()"), self.setRender)
		self.connect(self.makeTxPath_btn, QtCore.SIGNAL("clicked()"), self.setMakeTx)
		self.connect(self.departmentsPath_btn, QtCore.SIGNAL("clicked()"), self.setDepartmentsPath)
		self.connect(self.save_btn, QtCore.SIGNAL("clicked()"), self.save)

	def _loadConfig(self):
		"""docstring for _loadConfig"""
		gen = self.settings.General
		if gen:
			if gen.has_key( 'basepath' ):
				basePath = gen[ "basepath" ]
				self.localPath_le.setText( basePath )
			if gen.has_key( 'serverpath' ):
				serverPath = gen[ "serverpath" ]
				self.serverPath_le.setText( serverPath )
			if gen.has_key( 'mailserver' ):
				mailserver = gen[ "mailserver" ]
				self.mailServerIp_le.setText( mailserver )
			if gen.has_key( 'mailport' ):
				mailport = gen[ "mailport" ]
				self.mailPort_le.setText( mailport )
			if gen.has_key( 'sendmail' ):
				sendmail = gen[ "sendmail" ]
				if sendmail == 'True':
					state = QtCore.Qt.Checked
				else:
					state = QtCore.Qt.Unchecked
				self.sendMail_chb.setCheckState( state )
			if gen.has_key( 'departmentspath' ):
				departmentspath = gen[ "departmentspath" ]
				self.departmentsPath_le.setText( departmentspath )
			if gen.has_key( 'renderpath' ):
				renderPath = gen[ "renderpath" ]
				self.renderPath_le.setText( renderPath )
			if gen.has_key( 'shotrenderpath' ):
				renderPath = gen[ "shotrenderpath" ]
				self.shotRenderPath_le.setText( renderPath )
			if gen.has_key( 'assetrenderpath' ):
				renderPath = gen[ "assetrenderpath" ]
				self.assetRenderPath_le.setText( renderPath )
			if gen.has_key( 'maketxpath' ):
				self.makeTxPath_le.setText( gen[ 'maketxpath' ] )
			if gen.has_key( 'autoload' ):
				autoLoad = gen[ "autoload" ]
				if autoLoad == 'True':
					state = QtCore.Qt.Checked
				else:
					state = QtCore.Qt.Unchecked
				self.autoLoadManager_chb.setCheckState( state )
			if gen.has_key( 'usemayasubfolder' ):
				usemayasubfolder = gen[ "usemayasubfolder" ]
				if usemayasubfolder == 'True':
					state = QtCore.Qt.Checked
				else:
					state = QtCore.Qt.Unchecked
				self.useMayaSubFolder_chb.setCheckState( state )
			if gen.has_key( 'useassetspershot' ):
				usemayasubfolder = gen[ "useassetspershot" ]
				if usemayasubfolder == 'True':
					state = QtCore.Qt.Checked
				else:
					state = QtCore.Qt.Unchecked
				self.useAssetsPerShot_chb.setCheckState( state )
			if gen.has_key( 'localnukepath' ):
				localnukepath = gen[ 'localnukepath' ]
				self.nukeLocalPath_le.setText( localnukepath )
			if gen.has_key( 'changeinternalpaths' ):
				changeinternalpaths = gen[ "changeinternalpaths" ]
				if changeinternalpaths == 'True':
					state = QtCore.Qt.Checked
				else:
					state = QtCore.Qt.Unchecked
				self.changeInternalPaths_chb.setCheckState( state )
			if gen.has_key( 'skin' ):
				skin = gen[ "skin" ]
				index = self.skin_cmb.findText( skin )
				if not index == -1:
					self.skin_cmb.setCurrentIndex(index)

	def setLocal(self):
		"""docstring for setLocal"""
		fil = str(QtGui.QFileDialog.getExistingDirectory(self, "Select Local Projects Path"))
		if fil:
			self.localPath_le.setText( fil.replace( '\\', '/' ) )

	def setServer(self):
		"""docstring for setServer"""
		fil = str(QtGui.QFileDialog.getExistingDirectory(self, "Select Local Projects Path"))
		if fil:
			self.serverPath_le.setText( fil.replace( '\\', '/' ) )

	def setDepartmentsPath(self):
		"""docstring for setServer"""
		fil = str(QtGui.QFileDialog.getExistingDirectory(self, "Select Departments Path"))
		if fil:
			self.departmentsPath_le.setText( fil.replace( '\\', '/' ) )

	def setRender(self):
		"""docstring for setRender"""
		fil = str(QtGui.QFileDialog.getExistingDirectory(self, "Select Local Projects Path"))
		if fil:
			self.renderPath_le.setText( fil.replace( '\\', '/' ) )

	def setMakeTx(self):
		"""docstring for fname"""
		fil = QtGui.QFileDialog.getOpenFileName(self, 'Select Make Tx Path', '', selectedFilter='*.exe')
		if fil:
			fil = fil[0]
			self.makeTxPath_le.setText( str( fil ).replace( '\\', '/' ) )

	def save(self):
		"""docstring for save"""
		self.settings.write( 'General', 'basepath', str( self.localPath_le.text().replace( '\\', '/' ) ))
		self.settings.write( 'General', 'serverpath', str( self.serverPath_le.text().replace( '\\', '/' ) ))
		self.settings.write( 'General', 'mailserver', str( self.mailServerIp_le.text() ))
		self.settings.write( 'General', 'mailport', str( self.mailPort_le.text() ))
		self.settings.write( 'General', 'sendmail', self.sendMail_chb.isChecked() )
		self.settings.write( 'General', 'departmentspath', str( self.departmentsPath_le.text().replace( '\\', '/' ) ))
		self.settings.write( 'General', 'renderpath', str( self.renderPath_le.text().replace( '\\', '/' ) ))
		self.settings.write( 'General', 'assetrenderpath', str( self.assetRenderPath_le.text().replace( '\\', '/' ) ))
		self.settings.write( 'General', 'shotrenderpath', str( self.shotRenderPath_le.text().replace( '\\', '/' ) ))
		self.settings.write( 'General', 'localnukepath', str( self.nukeLocalPath_le.text().replace( '\\', '/' ) ))
		self.settings.write( 'General', 'maketxpath', str( self.makeTxPath_le.text().replace( '\\', '/' ) ))
		self.settings.write( 'General', 'autoload', self.autoLoadManager_chb.isChecked() )
		self.settings.write( 'General', 'usemayasubfolder', self.useMayaSubFolder_chb.isChecked() )
		self.settings.write( 'General', 'useassetspershot', self.useAssetsPerShot_chb.isChecked() )
		self.settings.write( 'General', 'changeinternalpaths', self.changeInternalPaths_chb.isChecked() )
		self.settings.write( 'General', 'automaketx', self.makeTx_chb.isChecked() )
		self.settings.write( 'General', 'skin', str( self.skin_cmb.currentText() ))
		QtGui.QDialog.accept(self)

def main():
	global PyFormSettings
	PyFormSettings=Settings(parent=QtGui.QApplication.activeWindow())
	PyFormSettings.show()



