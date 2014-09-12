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
		assOrShot = prj.shotOrAssetFromFile( mfl.currentFile() )
		self.projectPath_le.setText( mc.workspace( q = True, fullName = True ) )
		self._project = ''
		if assOrShot:
			if assOrShot.type == 'asset':
				versionNumber = self._getVersionNumber( renderPath + assOrShot.project.name + '/Asset/' + assOrShot.name )
				pat = renderPath + assOrShot.project.name + '/Asset/' + assOrShot.name + '/v' + str(versionNumber).zfill( 4 ) + '/' + '<RenderLayer>' + '/<RenderLayer>'
			elif assOrShot.type == 'shot':
				versionNumber = self._getVersionNumber( renderPath + assOrShot.project.name + '/' + assOrShot.sequence.name + '/' + assOrShot.name )
				pat = renderPath + assOrShot.project.name + '/' + assOrShot.sequence.name + '/' + assOrShot.name + '/v' + str(versionNumber).zfill( 4 ) + '/' + '<RenderLayer>' + '/<RenderLayer>'
				renderGlobals.a.imageFilePrefix.v = str( pat )
			self._project = assOrShot.project.name
			self.filePath_le.setText( str( pat ))
		self.frameRange_le.setText( str( int( renderGlobals.a.startFrame.v ) ) + "-" + str( int(  renderGlobals.a.endFrame.v ) ) )
		self._fillLayers()

	def _fillLayers(self):
		"""fill ui with render layers"""
		for r in rlayer.renderlayers():
			if ':' in r.name:
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
		if self.autoSave_chb.isChecked():
			curFile = mfl.currentFile()
			curFile.newVersion()
			curFile.save()
		dead     = dl.Deadline()
		group    = str(self.groups_cmb.currentText())
		pool     = str(self.pools_cmb.currentText())
		comments = str( self.comments_te.toPlainText())
		filePrefix= str( self.filePath_le.text())
		priority = str( self.priority_spb.value() )
		taskSize = str( self.taskSize_spb.value() )
		projPath = str( self.projectPath_le.text() )
		InitialStatus = "Active"
		if self.submitSuspended_chb.isChecked():
			InitialStatus = "Suspended"
		whiteList = ''
		deRenGlob = mn.Node( 'defaultRenderGlobals' )
		pad = deRenGlob.a.extensionPadding.v
		deRenGlob.a.imageFilePrefix.v = str(self.filePath_le.text())
		if self.renderLocal_chb.isChecked():
			whiteList = socket.gethostname()
			print 'rendering in local', whiteList
		for w in self._getLayersWidgets():
			frames   = str(self.frameRange_le.text())
			if not w.renderMe_chb.isChecked():
				continue
			if w.overFrameRange_chb.isChecked():
				frames =  str( w.frameRange_le.text() )
			filename = mc.renderSettings( lyr = w.layer.name, gin = ('?'*pad) )[0]
			name = ''
			if self._project:
				name = self._project + ' - '
			Job = dl.Job( w.layer.name,
						{	'Group'           : group,
							'Pool'            : pool,
							'Frames'          : frames,
							'Comment'         : comments,
							'InitialStatus'   : InitialStatus,
							'Whitelist'       : whiteList,
							'Name'            : name + mfl.currentFile().name + ' - ' + w.layer.name,
							'OutputFilename0' : filename,
							'Priority'        : priority,
							'ChunkSize'       : taskSize
							},{'CommandLineOptions' : '-rl ' + w.layer.name,
								'UsingRenderLayers' : 1,
								'ProjectPath'       : projPath,
								'RenderLayer'       : w.layer.name,
								'OutputFilePrefix'  : filePrefix,
							}, mfl.currentFile() )
			Job.write()
			dead.runMayaJob( Job )

	def _getVersionNumber(self, path):
		"""return version number for render folder"""
		if not os.path.exists( path ):
			return 1
		return len( [a for a in os.listdir( path ) if os.path.isdir( path + '/' + a ) ] ) + 1

	def _getLayersWidgets(self):
		"""return the layerswidgets items"""
		return [self.renderLayers_lay.itemAt(i).widget() for i in range(self.renderLayers_lay.count())] 

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
		if self.layer.a.renderable.v:
			self.renderMe_chb.setCheckState( QtCore.Qt.Checked )
		else:
			self.renderMe_chb.setCheckState( QtCore.Qt.Unchecked )
		#print 'error'
		tw = self.layer.overridesWithValues
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
		self.renderLayer_lbl.setText( self.layer.name )

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
