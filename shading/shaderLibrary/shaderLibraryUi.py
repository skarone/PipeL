from PyQt4 import QtGui,QtCore, uic
import shading.shaderLibrary.shaderLibrary as sh
reload (sh )
import pyqt.accordionwidget.accordionwidget as cgroup
import pyqt.flowlayout.flowlayout as flowlayout
try:
	import maya.cmds as cmds
	import maya.mel as mm
except:
	print 'running from outside maya'
import os
import json


PYFILEDIR = os.path.dirname( os.path.abspath( __file__ ) )
LIBHISTORYPATH  = PYFILEDIR + '/shaderLibrary.his'
LIBSETTINGSPATH = PYFILEDIR + '/shaderLibrary.settings'
NOPREVIEWPATH   = PYFILEDIR + '/tex/shaderLibrary_preview.png'

uifile = PYFILEDIR + '/shaderLibrary.ui'
fom, base = uic.loadUiType( uifile )

uifile = PYFILEDIR + r'/shader.ui'
fom2, base2 = uic.loadUiType( uifile )

SELECTEDSHADERS = []

class LibraryUI(base, fom):
	def __init__(self):
		super(base,self).__init__()
		self.setupUi(self)
		self._fillHistory()
		self._makeConnections()
		self._setupBanner()
		self._createAccordion()
		self._createLibUI()

	def _fillHistory(self):
		"""add lastest libraries in history"""
		for h in self.history:
			self._insertLibraryPathInUI( h )

	def _createAccordion(self):
		"""docstring for _createAccordion"""
		self.catLayout = cgroup.AccordionWidget(None)
		self.asd.addWidget( self.catLayout )

	def _clearAccordion(self):
		"""docstring for _deleteAccordion"""
		self.catLayout.clear()

	def _setupBanner(self):
		"""set texture for banner"""
		imagePath = PYFILEDIR + '/tex/shaderLibrary_flag.png'
		myPixmap = QtGui.QPixmap(imagePath)
		self.image_ui.setPixmap(myPixmap)

	def _makeConnections(self):
		"""make the connection to the actions"""
		QtCore.QObject.connect( self.lib_path_cmb, QtCore.SIGNAL( "currentIndexChanged( const QString& )" ), self._createLibUI )
		QtCore.QObject.connect( self.hyperShade_btn, QtCore.SIGNAL( "clicked()" ), self.HyperShade )
		QtCore.QObject.connect( self.browse_lib_btn, QtCore.SIGNAL( "clicked()" ), self._selectLibraryFromBrowser )
		#QtCore.QObject.connect( self.pushButton_2, QtCore.SIGNAL( "clicked()" ), self._createLibUI )
		QtCore.QObject.connect( self.actionClear_History, QtCore.SIGNAL( "triggered()" ), self.clearHistory )
		QtCore.QObject.connect( self.actionSetMain_Library, QtCore.SIGNAL( "triggered()" ), self._assignMainLibrary )
		QtCore.QObject.connect( self.actionExplore_Library, QtCore.SIGNAL( "triggered()" ), self.exploreLibrary )
		QtCore.QObject.connect( self.actionImport_Selected, QtCore.SIGNAL( "triggered()" ), self.importSelected )
		QtCore.QObject.connect( self.deleteSelectedShaders, QtCore.SIGNAL( "triggered()" ), self.deleteSelected )
		QtCore.QObject.connect( self.main_lib_rbtn, QtCore.SIGNAL( "clicked()" ), self._useMainLibrary )
		QtCore.QObject.connect( self.exportAsset_btn, QtCore.SIGNAL( "clicked()" ), self.exportAssetShaders )
		QtCore.QObject.connect( self.exportSel_btn, QtCore.SIGNAL( "clicked()" ), self.exportSelShaders )
		QtCore.QObject.connect( self.exportAll_btn, QtCore.SIGNAL( "clicked()" ), self.exportAllShaders )

	def exportAssetShaders(self):
		"""export all the shaders from the selected asset"""
		pass

	def exportSelShaders(self):
		"""export shaders from selected objects"""
		pass

	def exportAllShaders(self):
		"""export all the shaders in the scene"""
		pass


	def importSelected(self):
		"""docstring for importSelected"""
		for s in SELECTEDSHADERS:
			s.shader.importShader()

	def deleteSelected(self):
		"""docstring for deleteSelected"""
		for s in SELECTEDSHADERS:
			s.delete()

	def _useMainLibrary(self):
		"""use main library"""
		lib = self.mainlibrary
		self._insertLibraryPathInUI( lib )
		self._createLibUI()
		self.history = lib

	def exploreLibrary(self):
		"""open explorer with the library path"""
		path = self.getSelectedLibrary()
		if path:
			cmd = str( 'start explorer "'+path.replace('/','\\')+'"')
			os.system(cmd)
		

	def _createLibUI(self):
		#clear ui
		self._clearAccordion()
		libPath = self.lib_path_cmb.currentText()
		if not libPath:
			return 
		lib = sh.ShaderLibrary( str( libPath ) )
		for cat in lib.categories:
			self._createCategory( cat, lib )

	def getSelectedLibrary(self):
		"""get the selected library from the comboBox"""
		libPath = self.lib_path_cmb.currentText()
		if libPath == '':
			return None
		return libPath

	def _createCategory( self, cat, lib ):
		"""create shader form in UI"""
		#catLay = QtGui.
		grid = flowlayout.FlowLayout()
		shds = lib.shadersincategory( cat )
		shaderCount = len( shds )
		for s in shds:
			button = shaderUI( s.name, cat, lib )
			grid.addWidget(button)

		wid = QtGui.QWidget()
		wid.setLayout( grid )
		item = self.catLayout.addItem( cat, wid, True )

	def HyperShade(self):
		"""open HyperShade"""
		mm.eval( 'HypershadeWindow;' )

	def _selectLibraryFromBrowser(self):
		"""Set library Path from browser"""
		lib = self._selectDirectory()
		self._insertLibraryPathInUI( lib )
		self._createLibUI()
		self.history = lib
	
	def _insertLibraryPathInUI(self, lib):
		"""add path to ComboBox"""
		self._removeItemFromComboBox( lib )
		self.lib_path_cmb.insertItems(0,[lib])
		self.lib_path_cmb.setCurrentIndex( 0 )

	def _removeItemFromComboBox(self, lib):
		"""remove item from comboBox"""
		[self.lib_path_cmb.removeItem(i) for i in range(self.lib_path_cmb.count()) if self.lib_path_cmb.itemText(i) == lib]

	def _selectDirectory(self):
		"""create FileDialog to select directory"""
		fi = str(QtGui.QFileDialog.getExistingDirectory(self, "Select Directory"))
		return fi

	def _assignMainLibrary(self):
		"""set main library for settings"""
		fi = self._selectDirectory()
		self.mainlibrary = fi

	@property
	def history(self):
		"""return the history of libraries used"""
		with open( LIBHISTORYPATH, 'r' ) as dataFile:
			history = json.load( dataFile )
		return history[ 'History' ]

	@history.setter
	def history( self, newLib ):
		"""add a newLib to history"""
		his = self.history
		if newLib in his:
			his.remove( newLib )
		his.insert( 0, newLib )
		history = {}
		history[ "History" ] = his
		self._writeHistory( history )

	def _writeHistory(self, his ):
		"""write history to file"""
		with open( LIBHISTORYPATH, 'w' ) as dataFile:
			json.dump( his, dataFile, sort_keys=True, indent=4, separators=(',', ': ') )

	def _libsInComboBox(self):
		"""return the list of items in the combobox"""
		AllItems = [self.lib_path_cmb.itemText(i) for i in range(self.lib_path_cmb.count())]
		print AllItems

	def clearHistory(self):
		"""this will remove all history from file"""
		his = {}
		his[ "History" ] = []
		print 'History Cleaned'
		self._writeHistory( his )

	@property
	def mainlibrary(self):
		"""get main library path"""
		settin = self.settings
		return settin[ 'Main' ]

	@mainlibrary.setter
	def mainlibrary(self, libPath ):
		"""set main library"""
		setting = {}
		setting[ 'Main' ] = libPath
		self._changeSettings( setting )
		
	@property
	def settings(self):
		"""return the settings of the UI"""
		with open( LIBSETTINGSPATH, 'r' ) as dataFile:
			_settings = json.load( dataFile )
		return _settings

	@settings.setter
	def settings(self, sett):
		"""save new settings"""
		with open( LIBSETTINGSPATH, 'w' ) as dataFile:
			json.dump( sett, dataFile, sort_keys=True, indent=4, separators=(',', ': ') )

	def _changeSettings(self, newSettings):
		"""update settings"""
		sets = self.settings
		sets.update( newSettings )
		self.settings = sets


class shaderUI(base2, fom2):
	def __init__(self, name, category, library ):
		super(base2,self).__init__()
		self.shader = sh.Shader( name, category, library )
		self.setupUi(self)
		self.selectShader_chb.setText( name )
		imagePath = self.shader.previewpath
		if not os.path.exists( imagePath ):
			imagePath = PYFILEDIR + '/tex/no_Preview.jpg'
		myPixmap = QtGui.QPixmap( imagePath )
		myScaledPixmap = myPixmap.scaled(self.imageShader_img.size(), QtCore.Qt.KeepAspectRatio )
		self.imageShader_img.setPixmap(myScaledPixmap)
		self._makeConnections()

	def _makeConnections(self):
		"""make the connection to the actions"""
		QtCore.QObject.connect( self.deleteShader_btn, QtCore.SIGNAL("clicked()"),self.delete )
		QtCore.QObject.connect( self.assignShader_btn, QtCore.SIGNAL("clicked()"),self.assign )
		QtCore.QObject.connect(self.selectShader_chb, QtCore.SIGNAL("clicked()"), self._shaderSelected )

	def delete(self):
		"""delete shader from UI and from library"""
		print 'Deleting', self.shader.name
		self.selectShader_chb.setCheckState( 0 )
		self._shaderSelected()
		self.setParent(None)
		self.close()
		self.shader.delete()
	
	def _shaderSelected(self):
		"""manage checbox event for ui"""
		#if self.isCheked():
		if self.selectShader_chb.isChecked():
			SELECTEDSHADERS.append( self )
		else:
			SELECTEDSHADERS.remove( self )

	def assign(self):
		"""assign shader to selection or import"""
		self.shader.assign()


def main():
	global PyForm
	PyForm=LibraryUI()
	PyForm.show()
	
if __name__=="__main__":
	import sys
	a = QtGui.QApplication(sys.argv)
	global PyForm
	a.setStyle('plastique')
	PyForm=LibraryUI()
	PyForm.show()
	sys.exit(a.exec_())

