import os

import general.ui.pySideHelper as uiH
reload( uiH )
uiH.set_qt_bindings()
from Qt import QtGui,QtCore

import render.renderlayer.renderlayer as rlayer
reload( rlayer )
import render.deadline.deadline as dl
reload( dl )
import pipe.mayaFile.mayaFile as mfl
reload(mfl)
import pipe.project.project as prj
import general.mayaNode.mayaNode as mn
import pipe.settings.settings as sti
reload( sti )

import socket

#load UI FILE
PYFILEDIR = os.path.dirname( os.path.abspath( __file__ ) )
uifile = PYFILEDIR + '/renderManager.ui'
fom, base = uiH.loadUiType( uifile )

uiLayfile = PYFILEDIR + '/renderLayer.ui'
fomLay, baseLay = uiH.loadUiType( uiLayfile )

import pipe.mayaFile.mayaFile as mfl
reload(mfl)

import maya.cmds as mc
frameUnits = {
    'game': 15,
    'film': 24,
    'pal': 25 ,
    'ntsc': 30,
    'show': 48,
    'palf': 50,
    'ntscf': 60
 }
TIMEUNIT = frameUnits[ mc.currentUnit( q=True, t = True)]

class RenderManagerUI(base,fom):
	def __init__(self, parent  = uiH.getMayaWindow(), *args ):
		if uiH.USEPYQT:
			super(base, self).__init__(parent)
		else:
			super(RenderManagerUI, self).__init__(parent)
		self.setupUi(self)
		self._makeConnections()
		self.setObjectName( 'RenderManagerUI' )
		self._fillUi()
		uiH.loadSkin( self, 'QTDarkGreen' )

	def _makeConnections(self):
		"""create connection for ui"""
		self.connect( self.render_btn, QtCore.SIGNAL("clicked()") , self.render )
		self.connect( self.allLayersOn_btn, QtCore.SIGNAL("clicked()") , self.allLayersOn )
		self.connect( self.allLayersOff_btn, QtCore.SIGNAL("clicked()") , self.allLayersOff )
		self.connect( self.allOverridesOff_btn, QtCore.SIGNAL("clicked()") , self.allOverridesOff )

	def _fillUi(self):
		"""fill ui"""
		dead = dl.Deadline()
		self.groups_cmb.addItems( dead.groups )
		settings = sti.Settings()
		gen = settings.General
		renderPath = 'R:/'
		if gen:
			renderPath = gen[ "renderpath" ]
			if not renderPath.endswith( '/' ):
				renderPath += '/'
		self.pools_cmb.addItems( dead.pools )
		renderGlobals = mn.Node( 'defaultRenderGlobals' )
		self.filePath_le.setText( str( renderGlobals.a.imageFilePrefix.v ))
		self.assOrShot = prj.shotOrAssetFromFile( mfl.currentFile() )
		self.projectPath_le.setText( mc.workspace( q = True, fullName = True ) )
		self._project = ''
		if self.assOrShot:
			if self.assOrShot.type == 'asset':
				if gen.has_key( 'assetrenderpath' ):
					pat = renderPath + gen[ "assetrenderpath" ]
				else:
					pat = renderPath + '<project>' + '/Assets/' + '<asset>' + '/Render/<RenderLayer>/' + '<RenderLayerVersion>' + '/<RenderLayer>'
			elif self.assOrShot.type == 'shot':
				if gen.has_key( 'shotrenderpath' ):
					pat = renderPath + gen[ "shotrenderpath" ]
				else:
					pat = renderPath + '<project>' + '/' + '<sequence>' + '/' + '<shot>' + '/<RenderLayer>/' + '<RenderLayerVersion>' + '/<RenderLayer>'
			self._project = self.assOrShot.project.name
			self.filePath_le.setText( str( pat ))
		self.frameRange_le.setText( str( int( renderGlobals.a.startFrame.v ) ) + "-" + str( int(  renderGlobals.a.endFrame.v ) ) )
		self._fillLayers()

	def _fillLayers(self):
		"""fill ui with render layers"""
		for r in rlayer.renderlayers():
			if ':defaultRenderLayer' in r.name:
				continue
			self.renderLayers_lay.addWidget( RenderLayerUI( r ) )

	def allOverridesOff(self):
		"""docstring for fname"""
		for w in self._getLayersWidgets():
			w.overFrameRange_chb.setCheckState( QtCore.Qt.Unchecked )

	def allLayersOn(self):
		"""docstring for fname"""
		for w in self._getLayersWidgets():
			w.renderMe_chb.setCheckState( QtCore.Qt.Checked )

	def allLayersOff(self):
		"""docstring for allLayersOff"""
		for w in self._getLayersWidgets():
			w.renderMe_chb.setCheckState( QtCore.Qt.Unchecked )

	def render(self):
		"""docstring for render"""
		curFile = mfl.currentFile()
		if self.autoSave_chb.isChecked():
			curFile.newVersion()
			curFile.save()
		dead       = dl.Deadline()
		group      = str(self.groups_cmb.currentText())
		pool       = str(self.pools_cmb.currentText())
		comments   = str( self.comments_te.text())
		priority   = str( self.priority_spb.value() )
		taskSize   = str( self.taskSize_spb.value() )
		projPath   = str( self.projectPath_le.text() )
		if self.useServerPaths_chb.isChecked(): #IF USE PATH FROM SERVER... WE NEED TO CHANGE INTERNAL PATHS SO MATCH SERVER
			curFile = mfl.mayaFile( curFile.copy( dead.userHomeDirectory + '/' + curFile.fullName ).path )
			settings = sti.Settings()
			gen = settings.General
			if gen:
				basePath = gen[ "basepath" ]
				if basePath:
					if basePath.endswith( '\\' ):
						basePath = basePath[:-1]
					basePath = basePath.replace( '\\', '/' )
				serverPath = gen[ "serverpath" ]
				curFile.changePathsBrutForce( srchAndRep =  [ basePath, serverPath ] )

		#fix for xgen =)
		curFile.changeXgens( newDir = curFile.dirPath )
		InitialStatus = "Active"
		if self.submitSuspended_chb.isChecked():
			InitialStatus = "Suspended"
		whiteList = ''
		deRenGlob = mn.Node( 'defaultRenderGlobals' )
		pad = deRenGlob.a.extensionPadding.v
		#deRenGlob.a.imageFilePrefix.v = str(self.filePath_le.text())
		if self.renderLocal_chb.isChecked():
			whiteList = socket.gethostname()
			print 'rendering in local', whiteList
		plugin = 'MayaBatch'
		if mc.getAttr( "defaultRenderGlobals.ren" ) == 'mentalRay':
			plugin = 'MayaCmd'
		for w in self._getLayersWidgets():
			filePrefix = self.getFilePrefixFromTags( str(self.filePath_le.text()), self.assOrShot )
			frames   = str(self.frameRange_le.text())
			if not w.renderMe_chb.isChecked():
				continue
			if w.overFrameRange_chb.isChecked():
				frames =  str( w.frameRange_le.text() )
			filename = mc.renderSettings( lyr = w.layer.name, gin = ('?'*pad) )[0]
			print filename
			if not mc.getAttr( "defaultRenderGlobals.ren" ) == 'mentalRay':
				filePrefix = filePrefix.replace( '<RenderLayer>', w.layer.name.replace( ':', '_' ) )
				#get version number
				if '<RenderLayerVersion>' in filePrefix:
					versionNumber = self._getVersionNumber( filePrefix.split( '<RenderLayerVersion>' )[0] )
					filePrefix = filePrefix.replace( '<RenderLayerVersion>', 'v' + str(versionNumber).zfill( 4 ) )
				filename = filePrefix + '.' + ('?'*pad) + os.path.splitext( filename )[1]
			print 'RENDERING', filename, w.layer.name
			#filename = filename.replace( ':', '_' )
			name = ''
			if self._project:
				name = self._project + ' - '
			Job = dl.Job( w.layer.name.replace( ':', '_' ),
					{		'Plugin'          : plugin,
							'Group'           : group,
							'Pool'            : pool,
							'Frames'          : frames,
							'Comment'         : comments,
							'InitialStatus'   : InitialStatus,
							'UserName'        : os.getenv('username'),
							'Whitelist'       : whiteList,
							'Name'            : name + curFile.name + ' - ' + w.layer.name,
							'OutputFilename0' : filename,
							'Priority'        : priority,
							'ChunkSize'       : taskSize,
							'OutputDirectory0': filename
							},{'CommandLineOptions' : '-rl ' + w.layer.name + ' -mr:art ',
								'UsingRenderLayers' : 1,
								#'ProjectPath'       : projPath,
								'RenderLayer'       : w.layer.name,
								'OutputFilePrefix'  : filePrefix,
								'OutputPath'        : filename
							}, curFile )
			Job.write()
			dead.runMayaJob( Job )
		#save asset or shot paths
		self.saveShotsPaths()

	def saveShotsPaths(self):
		"""save settings for render paths"""
		settings = sti.Settings()
		gen = settings.General
		gen = settings.General
		renderPath = 'R:/'
		if gen:
			renderPath = gen[ "renderpath" ]
		if self.assOrShot:
			if self.assOrShot.type == 'asset':
				settings.write( 'General', 'assetrenderpath', str(self.filePath_le.text()).replace( renderPath, '' ) )
			elif self.assOrShot.type == 'shot':
				settings.write( 'General', 'shotrenderpath', str(self.filePath_le.text()).replace( renderPath, '' ) )

	def _getVersionNumber(self, path):
		"""return version number for render folder"""
		if not os.path.exists( path ):
			return 1
		folders = [a for a in os.listdir( path ) if os.path.isdir( path + '/' + a ) ]
		lastFolderVersion = 1
		for f in folders:
			if not len( f ) == 5:
				continue
			numVer = int( f[f.rindex( 'v' )+1:] )
			if lastFolderVersion < numVer:
				lastFolderVersion = numVer
		return lastFolderVersion + 1

	def _getLayersWidgets(self):
		"""return the layerswidgets items"""
		return [self.renderLayers_lay.itemAt(i).widget() for i in range(self.renderLayers_lay.count())]

	def getFilePrefixFromTags(self, filePrefix, shot ):
		"""return filePrefix Path replacing tags"""
		if shot.type == 'asset':
			filePrefix = filePrefix.replace( '<project>', shot.project.name )
			filePrefix = filePrefix.replace( '<asset>', shot.name )
		else:
			filePrefix = filePrefix.replace( '<project>', shot.project.name )
			filePrefix = filePrefix.replace( '<sequence>', shot.sequence.name )
			filePrefix = filePrefix.replace( '<shot>', shot.name )
		return filePrefix


class RenderLayerUI(baseLay,fomLay):
	def __init__(self, renderLayerNode ):
		if uiH.USEPYQT:
			super(baseLay, self).__init__()
		else:
			super(RenderLayerUI, self).__init__()
		self.setupUi(self)
		self._layer = renderLayerNode
		self._makeConnections()
		self._updateUi()
		uiH.loadSkin( self, 'QTDarkGreen' )

	def _makeConnections(self):
		"""docstring for _makeConnections"""
		self.connect( self.renderMe_chb, QtCore.SIGNAL("stateChanged (int)") , self.setEnabled )
		self.connect( self.overFrameRange_chb, QtCore.SIGNAL("stateChanged (int)") , self.setFrameRangeOverride )

	@property
	def layer(self):
		"""docstring for layer"""
		return self._layer

	def _updateUi(self):
		"""update ui based on layer info"""
		if self._layer.a.renderable.v:
			self.renderMe_chb.setCheckState( QtCore.Qt.Checked )
		else:
			self.renderMe_chb.setCheckState( QtCore.Qt.Unchecked )
		tw = self._layer.overridesWithValues
		startFrame = ''
		endFrame   = ''
		for o in tw.keys():
			if 'defaultRenderGlobals.startFrame' == o.fullname:
				startFrame = tw[o]*TIMEUNIT
			elif 'defaultRenderGlobals.endFrame' == o.fullname:
				endFrame = tw[o]*TIMEUNIT
		renderGlobals = mn.Node( 'defaultRenderGlobals' )
		if startFrame or endFrame:
			self.overFrameRange_chb.setCheckState( QtCore.Qt.Checked )
			if not startFrame:
				startFrame = renderGlobals.a.startFrame.v
			if not endFrame:
				endFrame = renderGlobals.a.endFrame.v
			self.frameRange_le.setText( str( int( startFrame ) ) + '-' + str( int ( endFrame ) ) )
		self.renderLayer_lbl.setText( self._layer.name )

	def setEnabled(self, val):
		"""docstring for setEnabled"""
		color = [QtGui.QColor( "grey" ),
				QtGui.QColor( "red" ),
				QtGui.QColor( "green" )]
		self.baselayer_fm.setStyleSheet("QFrame { background-color: %s }" %color[val].name())

	def setFrameRangeOverride(self, val):
		""""""
		color = [QtGui.QColor( "grey" ),
				QtGui.QColor( "red" ),
				QtGui.QColor( "yellow" )]
		if uiH.USEPYQT:
			self.overFrameRange_chb.setStyleSheet("QCheckBox { background-color: %s }" %color[val].name())
		else:
			self.overFrameRange_chb.setStyleSheet("QCheckBox { background-color: %s }" %color[val].name())

def main():
	"""call this from maya"""
	if mc.window( 'RenderManagerUI', q = 1, ex = 1 ):
		mc.deleteUI( 'RenderManagerUI' )
	PyForm=RenderManagerUI()
	PyForm.show()
