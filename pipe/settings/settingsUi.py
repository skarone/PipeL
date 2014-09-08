import os
import general.ui.pySideHelper as uiH
reload( uiH )
uiH.set_qt_bindings()
from Qt import QtGui,QtCore
import pipe.settings.settings as sti
reload( sti )

PYFILEDIR = os.path.dirname( os.path.abspath( __file__ ) )

uifile = PYFILEDIR + '/settings.ui'
fom, base = uiH.loadUiType( uifile )


class Settings(base, fom):
	"""docstring for ProjectCreator"""
	def __init__(self):
		if uiH.USEPYQT:
			super(base, self).__init__()
		else:
			super(Settings, self).__init__()
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
		self.connect(self.save_btn, QtCore.SIGNAL("clicked()"), self.save)

	def _loadConfig(self):
		"""docstring for _loadConfig"""
		gen = self.settings.General
		if gen:
			basePath = gen[ "basepath" ]
			self.localPath_le.setText( basePath )
			serverPath = gen[ "serverpath" ]
			self.serverPath_le.setText( serverPath )
			renderPath = gen[ "renderpath" ]
			self.serverPath_le.setText( serverPath )
			autoLoad = gen[ "autoLoad" ]
			if autoLoad: 
				state = QtCore.Qt.Checked 
			else: 
				state = QtCore.Qt.Unchecked
			self.autoLoadManager_chb.setCheckState( state )
			usemayasubfolder = gen[ "usemayasubfolder" ]
			if usemayasubfolder: 
				state = QtCore.Qt.Checked 
			else: 
				state = QtCore.Qt.Unchecked
			self.useMayaSubFolder_chb.setCheckState( state )
			skin = gen[ "skin" ]
			index = self.skin_cmb.findText( skin )
			if not index == -1:
				self.skin_cmb.setCurrentIndex(index)

	def setLocal(self):
		"""docstring for setLocal"""
		pass

	def setServer(self):
		"""docstring for setServer"""
		pass

	def setRender(self):
		"""docstring for setRender"""
		pass

	def save(self):
		"""docstring for save"""
		pass



