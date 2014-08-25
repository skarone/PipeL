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
INMAYA = False
import pipe.mayaFile.mayaFile as mfl
import pipe.cacheFile.cacheFile as cfl
reload( cfl )
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
		self._loadConfig()
		self._fillUi()
		self.setObjectName( 'cacheManager_WIN' )

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
		Config = ConfigParser.ConfigParser()
		Config.read( settingsFile )
		if Config.has_section( "GeneralSettings" ):
			basePath = Config.get("GeneralSettings", "basepath")
			if basePath:
				prj.BASE_PATH = basePath
		lastProject = Config.get("BaseSettings", "lastproject")
		if lastProject:
			index = self.projects_cmb.findText( lastProject )
			if not index == -1:
				self.projects_cmb.setCurrentIndex(index)

	def _makeConnections(self):
		"""create connection in the UI"""
		self.connect( self.refresh_btn            , QtCore.SIGNAL("clicked()") , self.refresh )
		self.connect( self.exportSelectedGeo_btn            , QtCore.SIGNAL("clicked()") , self.exportSelectedGeo )
		self.connect( self.exportAssetCache_btn            , QtCore.SIGNAL("clicked()") , self.exportAssetCache )
		self.connect( self.loadExternalCache_btn            , QtCore.SIGNAL("clicked()") , self.loadExternalCache )
		self.connect( self.loadSelectedCache_btn            , QtCore.SIGNAL("clicked()") , self.loadSelectedCache )
		self.connect( self.referenceCamera_btn            , QtCore.SIGNAL("clicked()") , self.referenceCamera )
		self.connect( self.exportCamera_btn            , QtCore.SIGNAL("clicked()") , self.exportCamera )
		self.connect( self.exportSelectedToSet_btn , QtCore.SIGNAL("clicked()") , self.exportSet )

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
		sel = mc.ls( sl = True )
		cacheFile = cfl.CacheFile( self.fileNameForCache(), sel )
		cacheFile.export()
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

	def exportSet(self):
		"""export selection"""
		pat = QtGui.QFileDialog.getSaveFileName(self, 'Save Set', self._selectedShot.setsPath, selectedFilter='*.ma')
		if pat:
			maFile = mfl.mayaFile( str( pat ) )
			maFile.newVersion()
			mc.file( str( pat ), preserveReferences=True, type='mayaAscii', exportSelected =True, prompt=True, force=True )

	def _getCurrentTab(self):
		"""return the visible table in the ui"""
		currentTab = self.tabWidget.currentIndex()
		if currentTab == 0:
			tabwid = self.caches_lw
		elif currentTab == 1:
			tabwid = self.files_lw
		return tabwid, currentTab

	def loadExternalCache(self):
		"""docstring for fname"""
		pass

	def loadSelectedCache(self):
		"""docstring for fname"""
		tab, tabNum = self._getCurrentTab()
		importAsset = self.importShading_chb.isChecked()
		if tabNum == 0:
			for v in xrange(self.caches_lw.count()):
				i = self.caches_lw.item(v)
				if i.checkState() == 2:
					n = i.data(32).toPyObject()
					n.importForAsset( ass.Asset( n.name[:n.name.rindex( '_' )], self._selectedProject ), n.name, not importAsset )
		elif tabNum == 1:
			for v in xrange(self.files_lw.count()):
				i = self.files_lw.item(v)
				if i.checkState() == 2:
					n = i.data(32).toPyObject()
					n.reference()


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
		self.caches_lw.clear()
		for s in caches.keys():
			for f in caches[s]:
				item = QtGui.QListWidgetItem( f.name + ' - ' + s )
				#item.setFlags(QtCore.Qt.ItemIsEnabled)
				item.setCheckState(QtCore.Qt.Unchecked )
				item.setData(32, f )
				self.caches_lw.addItem( item )
		#self.caches_lw.addItems( [  ( f.name + ' - ' + s ) for s in caches.keys() for f in caches[s] ])

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
			pathDir = self._selectedShot.animCachesPath 
		else:
			pathDir = QtGui.QFileDialog.getSaveFileName(self, 'Save Cache', self._selectedShot.animCachesPath, selectedFilter='*.abc')
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

