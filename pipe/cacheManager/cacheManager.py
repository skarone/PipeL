import os
import ConfigParser
import general.ui.pySideHelper as uiH
reload( uiH )
uiH.set_qt_bindings()
from Qt import QtGui,QtCore
import pipe.project.project   as prj
reload( prj )
import pipe.sequence.sequence as sq
reload( sq )
import pipe.asset.asset as ass
import pipe.shot.shot as sh
reload( sh )
INMAYA = False
import pipe.mayaFile.mayaFile as mfl
import pipe.cacheFile.cacheFile as cfl
reload( cfl )
import pipe.settings.settings as sti
reload( sti )

try:
	import maya.cmds as mc
	mc.loadPlugin( 'AbcImport' )
except:
	pass

try:
	import general.mayaNode.mayaNode as mn
	import maya.cmds as mc
	INMAYA = True
except:
	pass

#load UI FILE
PYFILEDIR = os.path.dirname( os.path.abspath( __file__ ) )
MAYAPATH = 'C:/"Program Files"/Autodesk/Maya2013/bin/maya.exe'

uifile = PYFILEDIR + '/cacheFileManager.ui'
fom, base = uiH.loadUiType( uifile )

settingsFile =  str( os.getenv('USERPROFILE') ) + '/settings.ini'


class CacheManagerUI(base,fom):
	"""manager ui class"""
	def __init__(self):
		if INMAYA:
			if uiH.USEPYQT:
				super(base, self).__init__(uiH.getMayaWindow())
			else:
				super(CacheManagerUI, self).__init__(uiH.getMayaWindow())
		else:
			super(base, self).__init__()
		self.setupUi(self)
		self._makeConnections()
		self.settings = sti.Settings()
		gen = self.settings.General
		self.serverPath = ''
		if gen:
			basePath = gen[ "basepath" ]
			if basePath:
				prj.BASE_PATH = basePath.replace( '\\', '/' )
			useMayaSubFolder = gen[ "usemayasubfolder" ]
			if useMayaSubFolder == 'True':
				prj.USE_MAYA_SUBFOLDER = True
			else:
				prj.USE_MAYA_SUBFOLDER = False
			self.serverPath = gen[ "serverpath" ]
		self._fillUi()
		self._loadConfig()
		self.setObjectName( 'cacheManager_WIN' )
		if gen:
			skin = gen[ "skin" ]
			if skin:
				uiH.loadSkin( self, skin )

	def _loadConfig(self):
		"""load config settings"""
		sht = prj.shotOrAssetFromFile(mfl.currentFile())
		if sht:
			if str( type(sht) ) == "<class 'pipe.shot.shot.Shot'>":
				index = self.projects_cmb.findText( sht.project.name )
				if not index == -1:
					self.projects_cmb.setCurrentIndex(index)
				index = self.sequences_cmb.findText( sht.sequence.name )
				if not index == -1:
					self.sequences_cmb.setCurrentIndex(index)
				index = self.shots_cmb.findText( sht.name )
				if not index == -1:
					self.shots_cmb.setCurrentIndex(index)
				return
		if not os.path.exists( settingsFile ):
			return
		his = self.settings.History
		if his:
			if 'lastproject' in his:
				lastProject = his[ "lastproject" ]
				if lastProject:
					index = self.projects_cmb.findText( lastProject )
					if not index == -1:
						self.projects_cmb.setCurrentIndex(index)

	def _makeConnections(self):
		"""create connection in the UI"""
		self.connect( self.refresh_btn             , QtCore.SIGNAL("clicked()") , self.refresh )
		self.connect( self.exportSelectedGeo_btn   , QtCore.SIGNAL("clicked()") , self.exportSelectedGeo )
		self.connect( self.exportAssetCache_btn    , QtCore.SIGNAL("clicked()") , self.exportAssetCache )
		self.connect( self.loadExternalCache_btn   , QtCore.SIGNAL("clicked()") , self.loadExternalCache )
		self.connect( self.loadSelectedCache_btn   , QtCore.SIGNAL("clicked()") , self.loadSelectedCache )
		self.connect( self.referenceCamera_btn     , QtCore.SIGNAL("clicked()") , self.referenceCamera )
		self.connect( self.exportCamera_btn        , QtCore.SIGNAL("clicked()") , self.exportCamera )
		self.connect( self.exportSelectedToSet_btn , QtCore.SIGNAL("clicked()") , self.exportSet )
		self.connect( self.replaceAlembic_btn      , QtCore.SIGNAL("clicked()") , self.replaceAlembic )

		QtCore.QObject.connect( self.projects_cmb, QtCore.SIGNAL( "currentIndexChanged( const QString& )" ), self._fillSequences )
		QtCore.QObject.connect( self.sequences_cmb, QtCore.SIGNAL( "currentIndexChanged( const QString& )" ), self._fillShots )
		QtCore.QObject.connect( self.shots_cmb, QtCore.SIGNAL( "currentIndexChanged( const QString& )" ), self._fillCacheList )
		QtCore.QObject.connect( self.shots_cmb, QtCore.SIGNAL( "currentIndexChanged( const QString& )" ), self._fillFileList )

	def referenceCamera(self):
		"""docstring for reference"""
		sht = self._selectedShot.poolCam
		sht.reference()
		tim = sht.time
		mc.currentUnit( time=tim['tim'], linear = tim['lin'], angle = tim[ 'angle' ] )
		"""
		mc.playbackOptions( min = tim[ 'min' ],
							ast = tim[ 'ast' ], 
							max = tim[ 'max' ], 
							aet = tim[ 'aet' ] )
		"""

	def exportCamera(self):
		"""docstring for exportCamera"""
		mc.file( self._selectedShot.poolCam.path, force = True, options = "v=0;", typ = "mayaAscii", pr = True, es = True )

	def refresh(self):
		"""docstring for refresh"""
		self._fillCacheList()
		self._fillFileList()

	def exportSelectedGeo(self):
		"""docstring for exp"""
		sel = mn.ls( sl = True )
		cacheFile = cfl.CacheFile( self.fileNameForCache(), sel )
		cacheFile.export()
		if self.copyToServer_chb.isChecked():
			cacheFile.copy( cacheFile.path.replace( prj.BASE_PATH, self.serverPath ) )
		self._fillCacheList()

	def exportAssetCache(self):
		"""docstring for fname"""
		baseDir =  self.fileNameForCache( True )
		#TODO add filename and see best way to detect asset
		exportedAsset = []
		for n in mn.ls( sl = True ):
			baseName = n.name.split( ':' )[0]
			if baseName in exportedAsset:
				continue
			a = ass.getAssetFromNode(n, self._selectedProject)
			cacFile = cfl.CacheFile( baseDir + '/' + baseName + '.abc', n )
			cacFile.exportAsset( a, self.useFinalToExport_chb.isChecked() )
			exportedAsset.append( baseName )
			if self.copyToServer_chb.isChecked():
				serverFile = cfl.CacheFile( cacFile.path.replace( prj.BASE_PATH, self.serverPath ) )
				serverFile.newVersion()
				cacFile.copy( serverFile.path )
		self._fillCacheList()

	def exportSet(self):
		"""export selection"""
		pat = QtGui.QFileDialog.getSaveFileName(self, 'Save Set', self._selectedShot.setsPath, selectedFilter='*.ma')
		if pat:
			maFile = mfl.mayaFile( str( pat ) )
			maFile.newVersion()
			mc.file( str( pat ), preserveReferences=True, type='mayaAscii', exportSelected =True, prompt=True, force=True )
			if self.copyToServer_chb.isChecked():
				serverFile = mfl.mayaFile( maFile.path.replace( prj.BASE_PATH, self.serverPath ) )
				serverFile.newVersion()
				maFile.copy( serverFile.path )


	def _getCurrentTab(self):
		"""return the visible table in the ui"""
		currentTab = self.tabWidget.currentIndex()
		return currentTab

	def _getCurrentCacheTab(self):
		"""return the visible table in the ui"""
		currentTab = self.caches_tw.currentIndex()
		if currentTab == 0:
			tabwid = self.animCaches_lw
		elif currentTab == 1:
			tabwid = self.skinFixCaches_lw
		elif currentTab == 2:
			tabwid = self.simCaches_lw
		return tabwid, currentTab

	def loadExternalCache(self):
		"""docstring for fname"""
		pass

	def loadSelectedCache(self):
		"""docstring for fname"""
		tabNum = self._getCurrentTab()
		importAsset = self.importShading_chb.isChecked()
		if tabNum == 0:
			cacheTab, cacheTabNum = self._getCurrentCacheTab()
			for v in xrange( cacheTab.count()):
				i = cacheTab.item(v)
				if i.checkState() == 2:
					if uiH.USEPYQT:
						n = i.data(32).toPyObject()
					else:
						n = i.data( 32 )
					if '_' in n.name:
						n.importForAsset( ass.Asset( n.name[:n.name.rindex( '_' )], self._selectedProject ), n.name, not importAsset )
					else:
						n.imp()
		elif tabNum == 1:
			for v in xrange(self.files_lw.count()):
				i = self.files_lw.item(v)
				if i.checkState() == 2:
					if uiH.USEPYQT:
						n = i.data(32).toPyObject()
					else:
						n = i.data( 32 )
					n.reference()

	def replaceAlembic(self):
		"""replace Alembic File"""
		SelAl = mn.ls( sl = True )
		if not SelAl:
			QtGui.QMessageBox.critical(self, 'Bad Input' , "PLEASE SELECT AN ALEMBIC NODE THAT YOU WANT TO REPLACE", QtGui.QMessageBox.Close)
			return
		if not SelAl[0].type == 'AlembicNode':
			QtGui.QMessageBox.critical(self, 'Bad Input' , "PLEASE SELECT AN ALEMBIC NODE THAT YOU WANT TO REPLACE", QtGui.QMessageBox.Close)
			return
		tabNum = self._getCurrentTab()
		importAsset = self.importShading_chb.isChecked()
		if tabNum == 0:
			cacheTab, cacheTabNum = self._getCurrentCacheTab()
			for v in xrange( cacheTab.count()):
				i = cacheTab.item(v)
				if i.checkState() == 2:
					if uiH.USEPYQT:
						n = i.data(32).toPyObject()
					else:
						n = i.data( 32 )
					n.replace( SelAl[0].name )

	def _fillUi(self):
		"""fill ui based on current scene or selected shot"""
		self._fillProyects()

	@property
	def _selectedProject(self):
		"""docstring for _selectedProyect"""
		return prj.Project( str ( self.projects_cmb.currentText() ) )

	@property
	def _selectedSequence(self):
		"""docstring for _selectedSequence"""
		return  sq.Sequence( str( self.sequences_cmb.currentText() ), self._selectedProject )

	@property
	def _selectedShot(self):
		"""docstring for _selectedShot"""
		return sh.Shot( str( self.shots_cmb.currentText() ), self._selectedSequence )

	def _fillProyects(self):
		"""docstring for _fillProyects"""
		self.projects_cmb.clear()
		self.projects_cmb.addItems( prj.projects() )
		self._fillSequences()

	def _fillSequences(self):
		"""docstring for _fillSequences"""
		self.sequences_cmb.clear()
		self.sequences_cmb.addItems( [ s.name for s in self._selectedProject.sequences ] )
		self._fillShots()

	def _fillShots(self):
		"""docstring for _fillShots"""
		self.shots_cmb.clear()
		self.shots_cmb.addItems( [ s.name for s in self._selectedSequence.shots ] )
		self._fillCacheList()
		self._fillFileList()

	def _fillCacheList(self):
		"""fill list from caches in shot"""
		caches = self._selectedShot.caches
		self.animCaches_lw.clear()
		self.skinFixCaches_lw.clear()
		self.simCaches_lw.clear()
		for s in caches.keys():
			for f in caches[s]:
				item = QtGui.QListWidgetItem( f.name + ' - ' + s )
				#item.setFlags(QtCore.Qt.ItemIsEnabled)
				item.setCheckState(QtCore.Qt.Unchecked )
				item.setData(32, f )
				if s == 'anim':
					self.animCaches_lw.addItem( item )
				elif s == 'skin':
					self.skinFixCaches_lw.addItem( item )
				elif s == 'sim':
					self.simCaches_lw.addItem( item )

	def _fillFileList(self):
		"""docstring for _fillFileList"""
		files = self._selectedShot.sets
		self.files_lw.clear()
		for f in files:
			item = QtGui.QListWidgetItem( f.name )
			item.setCheckState(QtCore.Qt.Unchecked )
			item.setData(32, f )
			self.files_lw.addItem( item )

	def fileNameForCache(self, exportAsset = False):
		"""set the filename for the cache"""
		if self.useShotFolder_chb.isChecked() and exportAsset:
			cacheTab, cacheTabNum = self._getCurrentCacheTab()
			if cacheTabNum == 0:
				pathDir = self._selectedShot.animCachesPath 
			elif cacheTabNum == 1:
				pathDir = self._selectedShot.skinFixCachesPath
			elif cacheTabNum == 2:
				pathDir = self._selectedShot.simCachesPath 
		else:
			pathDir = QtGui.QFileDialog.getSaveFileName(self, 'Save Cache', self._selectedShot.animCachesPath, selectedFilter='*.abc')
			pathDir = pathDir[0]
		return str( pathDir )

def main():
	if mc.window( 'cacheManager_WIN', q = 1, ex = 1 ):
		mc.deleteUI( 'cacheManager_WIN' )
	PyForm=CacheManagerUI()
	PyForm.show()


if __name__=="__main__":
	import sys
	a = QtGui.QApplication(sys.argv)
	global PyForm
	a.setStyle('plastique')
	PyForm=CacheManagerUI()
	PyForm.show()
	sys.exit(a.exec_())

