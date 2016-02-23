import os
import ConfigParser
import general.ui.pySideHelper as uiH
reload( uiH )

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
import pipe.cacheManager.sceneCreator as sc
reload( sc )
from sys import platform as _platform
import subprocess
import pipe.mail.mail as ml
reload( ml )

try:
	import general.mayaNode.mayaNode as mn
	import maya.cmds as mc
	mc.loadPlugin( 'AbcImport' )
	import pipe.cacheManager.swapShot as ssh
	reload( ssh )
	INMAYA = True
	try:
		mc.loadPlugin( 'MayaExocortexAlembic' )
	except:
		pass
except:
	pass

INHOU = False
try:
	import general.houdini.utils as hu
	reload(hu)
	INHOU = True
except:
	pass

#load UI FILE
PYFILEDIR = os.path.dirname( os.path.abspath( __file__ ) )

uifile = PYFILEDIR + '/cacheFileManager.ui'
fom, base = uiH.loadUiType( uifile )

settingsFile =  str( os.getenv('USERPROFILE') ) + '/settings.ini'


class CacheManagerUI(base,fom):
	"""manager ui class"""
	def __init__(self, parent = None):
		if INMAYA:
			if uiH.USEPYQT:
				super(base, self).__init__(uiH.getMayaWindow())
			else:
				super(CacheManagerUI, self).__init__(uiH.getMayaWindow())
		else:
			if uiH.USEPYQT:
				super(base, self).__init__(parent)
			else:
				super(CacheManagerUI, self).__init__(parent)
		self.setupUi(self)
		if not INHOU:
			self.connectToGlobalScale_chb.setVisible( False )
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
			self.sendMail = gen[ "sendmail" ]
			self.mailServer = gen[ "mailserver" ]
			self.mailPort = gen[ "mailport" ]
			self.mailsPath = gen[ "departmentspath" ]
		self._fillUi()
		self._loadConfig()
		self.setObjectName( 'cacheManager_WIN' )
		cfl.USE_EXOCORTEX = self.useExocortex_chb.isChecked()
		if gen:
			skin = gen[ "skin" ]
			if skin:
				uiH.loadSkin( self, skin )

	def _loadConfig(self):
		"""load config settings"""
		if INMAYA:
			sht = prj.shotOrAssetFromFile(mfl.currentFile())
		else:
			sht = None
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
		self.connect( self.exploreFolder_btn       , QtCore.SIGNAL("clicked()") , self.explorePoolFolder )
		self.connect( self.exportSelectedGeo_btn   , QtCore.SIGNAL("clicked()") , self.exportSelectedGeo )
		self.connect( self.exportAssetCache_btn    , QtCore.SIGNAL("clicked()") , self.exportAssetCache )
		self.connect( self.loadExternalCache_btn   , QtCore.SIGNAL("clicked()") , self.loadExternalCache )
		self.connect( self.loadSelectedCache_btn   , QtCore.SIGNAL("clicked()") , self.loadSelectedCache )
		self.connect( self.referenceCamera_btn     , QtCore.SIGNAL("clicked()") , self.referenceCamera )
		self.connect( self.exportCamera_btn        , QtCore.SIGNAL("clicked()") , self.exportCamera )
		self.connect( self.exportSelectedToSet_btn , QtCore.SIGNAL("clicked()") , self.exportSet )
		self.connect( self.replaceAlembic_btn      , QtCore.SIGNAL("clicked()") , self.replaceAlembic )
		self.connect( self.createLitScene_btn      , QtCore.SIGNAL("clicked()") , self.createLitScene )
		self.connect( self.exportAnimationScene_btn      , QtCore.SIGNAL("clicked()") , self.exportAnimationScene )
		self.connect( self.swapShot_btn      , QtCore.SIGNAL("clicked()") , self.swapShot )

		QtCore.QObject.connect( self.projects_cmb, QtCore.SIGNAL( "currentIndexChanged( const QString& )" ), self._fillSequences )
		QtCore.QObject.connect( self.sequences_cmb, QtCore.SIGNAL( "currentIndexChanged( const QString& )" ), self._fillShots )
		QtCore.QObject.connect( self.shots_cmb, QtCore.SIGNAL( "currentIndexChanged( const QString& )" ), self._fillCacheList )
		QtCore.QObject.connect( self.shots_cmb, QtCore.SIGNAL( "currentIndexChanged( const QString& )" ), self._fillFileList )
		QtCore.QObject.connect( self.useExocortex_chb, QtCore.SIGNAL( "stateChanged  (int)" ), self.setUseExocortex )
		QtCore.QObject.connect( self.shots_cmb, QtCore.SIGNAL( "currentIndexChanged( const QString& )" ), self._checkCameraInPool )

	def _checkCameraInPool(self):
		"""docstring for fname"""
		sht = self._selectedShot
		if INMAYA:
			if sht.poolCam.exists:
				if not sht.poolCam.isZero:
					self.referenceCamera_btn.setEnabled( True )
				else:
					self.referenceCamera_btn.setEnabled( False )
			else:
				self.referenceCamera_btn.setEnabled( False )


	def explorePoolFolder(self):
		"""explore pool folder for current shot"""
		poolPath = self._selectedShot.path + '/Pool/'
		print poolPath
		if _platform == 'win32':
			subprocess.Popen(r'explorer "'+ poolPath.replace( '/','\\' ) +'"')
		else:
			subprocess.Popen(['nautilus',poolPath])


	def setUseExocortex(self, val):
		"""docstring for setUseExocortex"""
		cfl.USE_EXOCORTEX = self.useExocortex_chb.isChecked()

	def referenceCamera(self):
		"""docstring for reference"""
		sht = self._selectedShot
		if INMAYA:
			sht.poolCam.reference()
			tim = self._selectedShot.animPath.time
			mc.currentUnit( time=tim['tim'], linear = tim['lin'], angle = tim[ 'angle' ] )
			mc.playbackOptions( min = tim[ 'min' ],
								ast = tim[ 'ast' ],
								max = tim[ 'max' ],
								aet = tim[ 'aet' ] )
		elif INHOU:
			hu.loadCamera(sht.project.name, sht.sequence.name, sht.name, self.connectToGlobalScale_chb.isChecked() )
			hu.copyTimeSettings( sht.project.name, sht.sequence.name, sht.name )

	def exportCamera(self):
		"""docstring for exportCamera"""
		mc.file( self._selectedShot.poolCam.path, force = True, options = "v=0;", typ = "mayaAscii", pr = True, es = True )
		sel = mc.ls( sl = True )
		cacheFile = cfl.CacheFile( self._selectedShot.poolCam.path.replace( '.ma', '.abc' ), sel )
		cacheFile.export()
		selShot = self._selectedShot
		cacheFile.copy( selShot.compElementsPath )
		if self.sendMail:
			ml.mailFromTool( 'new_cache',
							{ '<ProjectName>': selShot.project.name,
							'<SequenceName>': selShot.sequence.name,
							'<ShotName>': selShot.name,
							'<AssetName>': 'CAMERA',
							'<UserName>': os.getenv('username')},
							os.getenv('username') + '@bitt.com',
							self.mailsPath , self.mailServer, self.mailPort  )

	def refresh(self):
		"""docstring for refresh"""
		self._fillCacheList()
		self._fillFileList()

	def exportSelectedGeo(self):
		"""docstring for exp"""
		sel = mc.ls( sl = True )
		fileName = self.fileNameForCache()
		cacheFile = cfl.CacheFile( fileName, sel )
		cacheFile.export()
		if self.copyToServer_chb.isChecked():
			cacheFile.copy( cacheFile.path.replace( prj.BASE_PATH, self.serverPath ) )
		selShot = self._selectedShot
		if self.sendMail:
			ml.mailFromTool( 'new_cache',
							{ '<ProjectName>': selShot.project.name,
							'<SequenceName>': selShot.sequence.name,
							'<ShotName>': selShot.name,
							'<AssetName>': fileName,
							'<UserName>': os.getenv('username')},
							os.getenv('username') + '@bitt.com',
							self.mailsPath , self.mailServer, self.mailPort  )
		self._fillCacheList()

	def exportAssetCache(self):
		"""docstring for fname"""
		baseDir =  self.fileNameForCache( True )
		#TODO add filename and see best way to detect asset
		exportedAsset = []
		steps = self.steps_spb.value()
		for n in mn.ls( sl = True ):
			baseName = n.name.split( ':' )[0]
			if baseName in exportedAsset:
				continue
			a = ass.getAssetFromNode(n, self._selectedProject)
			cacFile = cfl.CacheFile( baseDir + '/' + baseName + '.abc', [n] )
			cacFile.exportAsset( a, False, False, steps )
			exportedAsset.append( baseName )
			if self.copyToServer_chb.isChecked():
				serverFile = cfl.CacheFile( cacFile.path.replace( prj.BASE_PATH, self.serverPath ) )
				serverFile.newVersion()
				cacFile.copy( serverFile.path )
		selShot = self._selectedShot
		if self.sendMail:
			ml.mailFromTool( 'new_cache',
							{ '<ProjectName>': selShot.project.name,
							'<SequenceName>': selShot.sequence.name,
							'<ShotName>': selShot.name,
							'<AssetName>': ','.join( exportedAsset ),
							'<UserName>': os.getenv('username')},
							os.getenv('username') + '@bitt.com',
							self.mailsPath , self.mailServer, self.mailPort  )
		self._fillCacheList()

	def exportSet(self):
		"""export selection"""
		pat = QtGui.QFileDialog.getSaveFileName(self, 'Save Set', self._selectedShot.setsPath, selectedFilter='*.ma')
		if pat:
			print 'patSSS',pat
			maFile = mfl.mayaFile( str( pat[0] ) )
			maFile.newVersion()
			mc.file( str( maFile.path ), preserveReferences=True, type='mayaAscii', exportSelected =True, prompt=True, force=True )
			if self.copyToServer_chb.isChecked():
				serverFile = mfl.mayaFile( maFile.path.replace( prj.BASE_PATH, self.serverPath ) )
				serverFile.newVersion()
				maFile.copy( serverFile.path )

	def exportAnimationScene(self):
		"""docstring for exportAnimationScene"""
		sc.exportAllFromAnim( str ( self.projects_cmb.currentText() ), str( self.sequences_cmb.currentText() ), str( self.shots_cmb.currentText() ), self.serverPath, self.useExocortex_chb.isChecked() )
		selShot = self._selectedShot
		if self.sendMail:
			ml.mailFromTool( 'new_cache',
							{ '<ProjectName>': selShot.project.name,
							'<SequenceName>': selShot.sequence.name,
							'<ShotName>': selShot.name,
							'<AssetName>': 'ALL',
							'<UserName>': os.getenv('username')},
							os.getenv('username') + '@bitt.com',
							self.mailsPath , self.mailServer, self.mailPort  )

	def createLitScene(self):
		"""docstring for createLitScene"""
		sc.createLitScene( str ( self.projects_cmb.currentText() ), str( self.sequences_cmb.currentText() ), str( self.shots_cmb.currentText() ), self.serverPath, self.useExocortex_chb.isChecked() )

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
		elif currentTab == 3:
			tabwid = self.vfxCaches_lw
		return tabwid, currentTab

	def loadExternalCache(self):
		"""docstring for fname"""
		pass

	def loadSelectedCache(self):
		"""docstring for fname"""
		tabNum = self._getCurrentTab()
		importAsset = self.importShading_chb.isChecked()
		if tabNum == 0:
			gen = self.settings.General
			assetPerShot = gen[ "useassetspershot" ]
			if assetPerShot == 'True': assetPerShot = True
			else: assetPerShot = False
			shotSel = self._selectedShot
			cacheTab, cacheTabNum = self._getCurrentCacheTab()
			for v in xrange( cacheTab.count()):
				i = cacheTab.item(v)
				if i.checkState() == 2:
					if uiH.USEPYQT:
						n = i.data(32).toPyObject()
					else:
						n = i.data( 32 )
					if INMAYA:
						if '_' in n.name:
							n.importForAsset( ass.Asset( n.name[:n.name.rindex( '_' )], self._selectedProject ), self.area_lw.currentRow() , n.name, not importAsset, assetPerShot, shotSel )
						else:
							n.imp()
					elif INHOU:
						hu.loadAlembic( n, self.connectToGlobalScale_chb.isChecked() )
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
		tabNum = self._getCurrentTab()
		if tabNum == 0:
			cacheTab, cacheTabNum = self._getCurrentCacheTab()
			for v in xrange( cacheTab.count()):
				i = cacheTab.item(v)
				if i.checkState() == 2:
					if uiH.USEPYQT:
						n = i.data(32).toPyObject()
					else:
						n = i.data( 32 )
					n.replace()

	def swapShot(self):
		"""swap current shot with selected one"""
		sho = self._selectedShot
		ssh.swapShot( sho.project.name, sho.sequence.name, sho.name )

	def _fillUi(self):
		"""fill ui based on current scene or selected shot"""
		self._fillProyects()

	@property
	def _selectedProject(self):
		"""docstring for _selectedProyect"""
		return prj.Project( str ( self.projects_cmb.currentText() ), self.serverPath )

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
		self.projects_cmb.addItems( prj.projects( self.serverPath ) )
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
		self.vfxCaches_lw.clear()
		for s in caches.keys():
			for f in sorted( caches[s], key=lambda x: x.name, reverse=False):
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
				elif s == 'vfx':
					self.vfxCaches_lw.addItem( item )

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
	try:
		if mc.window( 'cacheManager_WIN', q = 1, ex = 1 ):
			mc.deleteUI( 'cacheManager_WIN' )
	except:
		pass
	global PyForm
	PyForm=CacheManagerUI(parent=QtGui.QApplication.activeWindow())
	PyForm.show()


if __name__=="__main__":
	import sys
	a = QtGui.QApplication(sys.argv)
	global PyForm
	a.setStyle('plastique')
	PyForm=CacheManagerUI()
	PyForm.show()
	sys.exit(a.exec_())

