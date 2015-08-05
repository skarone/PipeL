
"""
import shading.shaderLibrary.shaderLibraryUi as shdUi
reload( shdUi )
shdUi.main()
"""

import general.ui.pySideHelper as uiH
reload( uiH )
uiH.set_qt_bindings()
from Qt import QtGui,QtCore

import shading.shaderLibrary.shaderLibrary as sh
reload (sh )
import pyqt.accordionwidget.accordionwidget as cgroup
import pyqt.flowlayout.flowlayout as flowlayout
try:
	import maya.cmds as mc
	import maya.mel as mm
	import general.mayaNode.mayaNode as mn
except:
	pass
import os
import json
import subprocess


PYFILEDIR = os.path.dirname( os.path.abspath( __file__ ) )
LIBSETTINGSPATH =  str( os.getenv('USERPROFILE') ) + '/shaderLibrary_settings.ini'
LIBHISTORYPATH = str( os.getenv('USERPROFILE') ) + '/shaderLibrary_his.ini'
NOPREVIEWPATH   = PYFILEDIR + '/tex/shaderLibrary_preview.png'

uifile = PYFILEDIR + '/shaderLibrary.ui'
fom, base = uiH.loadUiType( uifile )

uifile = PYFILEDIR + '/shader.ui'
fom2, base2 = uiH.loadUiType( uifile )

SELECTEDSHADERS = []

class LibraryUI(base, fom):
	def __init__(self, parent = uiH.getMayaWindow()  ):
		super(LibraryUI, self).__init__(parent)
		self.setupUi(self)
		self._fillHistory()
		self._makeConnections()
		self._setupBanner()
		self._createAccordion()
		self._createLibUI()
		self.setObjectName( 'LibraryUI' )

	def _fillHistory(self):
		"""add lastest libraries in history"""
		for h in reversed( self.history ):
			print h
			self._insertLibraryPathInUI( h )

	def _createAccordion(self):
		"""docstring for _createAccordion"""
		self.catLayout = cgroup.AccordionWidget(None)
		self.catLayout.itemMenuRequested.connect( self.showCategoryMenu )
		self.asd.addWidget( self.catLayout )

	def showCategoryMenu(self, item):
		"""docstring for showCategoryMenu"""
		menu=QtGui.QMenu(self)
		actionExportShaders = QtGui.QAction("Export Selected Shaders to Category", menu)
		menu.addAction( actionExportShaders )
		self.connect( actionExportShaders, QtCore.SIGNAL( "triggered()" ), lambda val = item.title() : self.exportSelShaders(val) )
		#delete Category
		actionDeleteCategory = QtGui.QAction("deleteCategory", menu)
		menu.addAction( actionDeleteCategory )
		self.connect( actionDeleteCategory, QtCore.SIGNAL( "triggered()" ), lambda val = item.title() : self.deleteCategory(val) )
		menu.popup(QtGui.QCursor.pos())

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
		QtCore.QObject.connect( self.closeCats_btn, QtCore.SIGNAL( "clicked()" ), self.closeCats )
		QtCore.QObject.connect( self.openCats_btn, QtCore.SIGNAL( "clicked()" ), self.openCats )
		QtCore.QObject.connect( self.browse_lib_btn, QtCore.SIGNAL( "clicked()" ), self._selectLibraryFromBrowser )
		QtCore.QObject.connect( self.newCategory_btn, QtCore.SIGNAL( "clicked()" ), self._newCategory )
		QtCore.QObject.connect( self.actionClear_History, QtCore.SIGNAL( "triggered()" ), self.clearHistory )
		QtCore.QObject.connect( self.actionSetMain_Library, QtCore.SIGNAL( "triggered()" ), self._assignMainLibrary )
		QtCore.QObject.connect( self.actionExplore_Library, QtCore.SIGNAL( "triggered()" ), self.exploreLibrary )
		QtCore.QObject.connect( self.actionImport_Selected, QtCore.SIGNAL( "triggered()" ), self.importSelected )
		QtCore.QObject.connect( self.actionCreate_Preview, QtCore.SIGNAL( "triggered()" ), self.createPreview )
		QtCore.QObject.connect( self.deleteSelectedShaders, QtCore.SIGNAL( "triggered()" ), self.deleteSelected )
		QtCore.QObject.connect( self.main_lib_rbtn, QtCore.SIGNAL( "clicked()" ), self._useMainLibrary )
		QtCore.QObject.connect( self.refresh_btn, QtCore.SIGNAL( "clicked()" ), self._createLibUI )
		self.previewScale_sld.valueChanged.connect(self.changePreviewRes)
		QtCore.QObject.connect( self.search_le, QtCore.SIGNAL( "textEdited (const QString&)" ), self.searchShader )

	def searchShader(self, fil):
		"""docstring for fname"""
		for i in range( self.catLayout.widget().layout().count() - 1 ):
			grid = self.catLayout.itemAt( i ).widget().layout()
			hideCat = True
			for p in range( grid.count() ):
				item = grid.itemAt( p )
				if fil.lower() in str(item.widget().selectShader_chb.text()).lower():
					item.widget().setVisible( True )
					hideCat = False
				else:
					item.widget().setVisible( False )
			if hideCat:
				self.catLayout.itemAt( i ).setVisible( False )
			else:
				self.catLayout.itemAt( i ).setVisible( True )

	def closeCats(self):
		"""collapse all category frames"""
		for i in range( self.catLayout.widget().layout().count() - 1 ):
			grid = self.catLayout.itemAt( i )
			grid.setCollapsed( True )

	def openCats(self):
		"""expand all category frames"""
		for i in range( self.catLayout.widget().layout().count() - 1 ):
			grid = self.catLayout.itemAt( i )
			grid.setCollapsed( False )

	def changePreviewRes(self, value):
		"""change resolution in previews"""
		for i in range( self.catLayout.widget().layout().count() - 1 ):
			grid = self.catLayout.itemAt( i ).widget().layout()
			for p in range( grid.count() ):
				item = grid.itemAt( p )
				item.widget().sdf.setMaximumSize( 200 + value, 250 + value )
				geom = item.widget().sdf.geometry()
				item.widget().sdf.setGeometry(geom.x(), geom.y(), 200 + value, 250 + value )
				item.widget().imageShader_img.setMaximumSize( 150 + value, 150 + value )
				geom = item.widget().imageShader_img.geometry()
				item.widget().imageShader_img.setGeometry(geom.x(), geom.y(), 150 + value, 150 + value )

	def _newCategory(self):
		"""create a new category and refresh"""
		text, result = QtGui.QInputDialog.getText(self, "Create New Category","Write the name for the new category")
		if result:
			lib = self._getSelectedLibrary()
			lib.createCategory( text )
			self._createLibUI()

	def exportSelShaders(self, catName):
		"""export shaders from selected objects"""
		lib = self._getSelectedLibrary()
		makePreview = self.makePreview_chb.isChecked()
		for a in mn.ls(sl = True):
			sha = a.shader
			shaName = sha.a.surfaceShader.input.node
			shader = sh.Shader( shaName.name, catName, lib )
			shader.publish(makePreview)
		self._createLibUI()

	def deleteCategory(self, cat):
		"""delete category"""
		lib = self._getSelectedLibrary()
		lib.deleteCategory( cat )
		self._createLibUI()

	def importSelected(self):
		"""docstring for importSelected"""
		for s in SELECTEDSHADERS:
			s.shader.importShader()

	def createPreview(self):
		"""create preview for selected shader"""
		for s in SELECTEDSHADERS:
			s.shader.preview()

	def deleteSelected(self):
		"""docstring for deleteSelected"""
		for s in SELECTEDSHADERS:
			s.delete()

	def exploreLibrary(self):
		"""open explorer with the library path"""
		path = self.getSelectedLibrary()
		if path:
			subprocess.Popen(r'explorer /select,"'+ path.replace( '/','\\' ) +'"')

	def _createLibUI(self):
		#clear ui
		self._clearAccordion()
		lib = self._getSelectedLibrary()
		if lib:
			for cat in lib.categories:
				self._createCategory( cat, lib )

	def _getSelectedLibrary(self):
		"""docstring for _getSelectedLibrary"""
		libPath = self.lib_path_cmb.currentText()
		if not libPath:
			return 
		return sh.ShaderLibrary( str( libPath ) )

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

	def _useMainLibrary(self):
		"""use main library"""
		lib = self.mainlibrary
		self._insertLibraryPathInUI( lib )
		self._createLibUI()
		self.history = lib

	@property
	def history(self):
		"""return the history of libraries used"""
		if os.path.exists( LIBHISTORYPATH ):
			with open( LIBHISTORYPATH, 'r' ) as dataFile:
				history = json.load( dataFile )
			return history[ 'History' ]
		return []

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
		if not settin:
			self._assignMainLibrary()
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
		if os.path.exists( LIBSETTINGSPATH ):
			with open( LIBSETTINGSPATH, 'r' ) as dataFile:
				_settings = json.load( dataFile )
			return _settings
		return []

	@settings.setter
	def settings(self, sett):
		"""save new settings"""
		with open( LIBSETTINGSPATH, 'w' ) as dataFile:
			json.dump( sett, dataFile, sort_keys=True, indent=4, separators=(',', ': ') )

	def _changeSettings(self, newSettings):
		"""update settings"""
		self.settings = newSettings


class shaderUI(base2, fom2):
	def __init__(self, name, category, library ):
		super(shaderUI,self).__init__()
		self.shader = sh.Shader( name, category, library )
		self.setupUi(self)
		self.selectShader_chb.setText( name )
		imagePath = self.shader.previewpath
		if not os.path.exists( imagePath ):
			imagePath = PYFILEDIR + '/tex/no_Preview.jpg'
		myPixmap = QtGui.QPixmap( imagePath )
		#myScaledPixmap = myPixmap.scaled(self.imageShader_img.size(), QtCore.Qt.KeepAspectRatio )
		self.imageShader_img.setPixmap(myPixmap)
		self.imageShader_img.setScaledContents(True)
		self.imageShader_img.setMaximumSize( 150,150 )
		self._makeConnections()

	def _makeConnections(self):
		"""make the connection to the actions"""
		QtCore.QObject.connect( self.deleteShader_btn, QtCore.SIGNAL("clicked()"),self.delete )
		QtCore.QObject.connect( self.assignShader_btn, QtCore.SIGNAL("clicked()"),self.assign )
		QtCore.QObject.connect( self.editShader_btn, QtCore.SIGNAL("clicked()"),self.edit )
		QtCore.QObject.connect(self.selectShader_chb, QtCore.SIGNAL("clicked()"), self._shaderSelected )

	def delete(self):
		"""delete shader from UI and from library"""
		print 'Deleting', self.shader.name
		self.selectShader_chb.setCheckState( QtCore.Qt.Checked )
		self._shaderSelected()
		self.shader.delete()
		self.setParent(None)
		self.close()

	def edit(self):
		"""open preview file for editing shader"""
		if not self.shader.previewMayaFile.exists:
			self.shader.createPreviewMayaFile()
		self.shader.previewMayaFile.open()
	
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
	if mc.window( 'LibraryUI', q = 1, ex = 1 ):
		mc.deleteUI( 'LibraryUI' )
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

