from rv import rvtypes, extra_commands, commands
import sys, pprint
from Qt import QtGui, QtCore
import os
import general.ui.pySideHelper as uiH
import pipe.project.project   as prj
reload( prj )
import pipe.sequence.sequence as sq
reload( sq )
import pipe.shot.shot as sh
reload( sh )
import pipe.settings.settings as sti
reload( sti )
from sys import platform as _platform
import subprocess
import pipe.sequenceFile.sequenceFile as sqf
import pipe.mail.mail as ml
reload( ml)

PYFILEDIR = os.path.dirname( os.path.abspath( __file__ ) )

uifile = PYFILEDIR + '/rvRenderManager.ui'
# uifile = 'D:/PipeL/pipe/rv' + '/rvRenderManager.ui'
fom, base = uiH.loadUiType( uifile )

class RenderManager(base,fom):
	"""manager ui class"""
	def __init__(self, parent = None):
		super(RenderManager, self).__init__(parent)
		self.setupUi(self)
		self.settings = sti.Settings()
		self.gen = self.settings.General
		self.serverPath = self.gen[ "serverpath" ]
		useMayaSubFolder = self.gen[ "usemayasubfolder" ]
		if useMayaSubFolder == 'True':
			prj.USE_MAYA_SUBFOLDER = True
		else:
			prj.USE_MAYA_SUBFOLDER = False
		self._makeConnections()
		self._fillUi()
		self._loadConfig()

	def _makeConnections(self):
		"""create connection in the UI"""
		self.connect( self.exploreFolder_btn, QtCore.SIGNAL("clicked()") , self.exploreRenderFolder )
		self.connect( self.addLayer_btn, QtCore.SIGNAL("clicked()") , self.addLayer)
		self.connect( self.removeLayer_btn, QtCore.SIGNAL("clicked()") , self.removeLayer)
		self.connect( self.publish_btn, QtCore.SIGNAL("clicked()") , self.publish)
		QtCore.QObject.connect( self.projects_cmb, QtCore.SIGNAL( "currentIndexChanged( const QString& )" ), self._fillSequences )
		QtCore.QObject.connect( self.sequences_cmb, QtCore.SIGNAL( "currentIndexChanged( const QString& )" ), self._fillShots )
		QtCore.QObject.connect( self.shots_cmb, QtCore.SIGNAL( "currentIndexChanged( const QString& )" ), self._fillRendersList )
		QtCore.QObject.connect( self.layers_lw, QtCore.SIGNAL( "itemClicked( QListWidgetItem* )" ), self.fillVersionsList )
		QtCore.QObject.connect( self.layers_lw, QtCore.SIGNAL( "itemActivated( QListWidgetItem* )" ), self.fillVersionsList )
		QtCore.QObject.connect( self.layers_lw, QtCore.SIGNAL( "itemPressed( QListWidgetItem* )" ), self.fillVersionsList )
		QtCore.QObject.connect( self.viewLayers_lw, QtCore.SIGNAL( "itemChanged( QListWidgetItem* )" ), self.changeLayerVis )

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

	@property
	def _selectedLayer(self):
		"""docstring for _selectedLayer"""
		return self.layers_lw.selectedItems()[0].text()

	@property
	def _selectedRender(self):
		"""docstring for _selectedRender"""
		renderPath =  self.getRenderPathForShot( self._selectedShot )
		return renderPath + '/' + self._selectedLayer

	@property
	def _selectedVersion(self):
		"""docstring for _selectedVersion"""
		return self.versions_lw.selectedItems()[0].text()

	def exploreRenderFolder(self):
		"""explore pool folder for current shot"""
		poolPath = self.getRenderPathForShot( self._selectedShot )
		if _platform == 'win32':
			subprocess.Popen(r'explorer "'+ poolPath.replace( '/','\\' ) +'"')
		else:
			subprocess.Popen(['nautilus',poolPath])

	def _fillUi(self):
		"""fill ui based on current scene or selected shot"""
		self._fillProyects()

	def _loadConfig(self):
		"""docstring for _loadConfig"""
		his = self.settings.History
		if his:
			if 'lastproject' in his:
				lastProject = his[ "lastproject" ]
				if lastProject:
					index = self.projects_cmb.findText( lastProject )
					if not index == -1:
						self.projects_cmb.setCurrentIndex(index)
						self._fillSequences()
			if 'lastsequence' in his:
				lastSequence = his[ "lastsequence" ]
				if lastSequence:
					index = self.sequences_cmb.findText( lastSequence )
					if not index == -1:
						self.sequences_cmb.setCurrentIndex(index)

	def _fillProyects(self):
		"""docstring for _fillProyects"""
		self.projects_cmb.clear()
		self.projects_cmb.addItems( prj.projects( self.serverPath ) )
		self._fillSequences()

	def _fillSequences(self):
		"""docstring for _fillSequences"""
		self.sequences_cmb.clear()
		self.sequences_cmb.addItems( [ str( s.name ) for s in self._selectedProject.sequences ] )
		self._fillShots()

	def _fillShots(self):
		"""docstring for _fillShots"""
		self.shots_cmb.clear()
		self.shots_cmb.addItems( [ str( s.name ) for s in self._selectedSequence.shots ] )
		self._fillRendersList()

	def _fillRendersList(self):
		"""docstring for _fillRendersList"""
		self.layers_lw.clear()
		renderPath =  self.getRenderPathForShot( self._selectedShot )
		if not os.path.exists( renderPath ):
			return
		for f in sorted(os.listdir( self.getRenderPathForShot( self._selectedShot ) )):
			self.layers_lw.addItem( f )

	def fillVersionsList(self):
		"""docstring for fname"""
		layer = self._selectedRender
		self.versions_lw.clear()
		for a in sorted(os.listdir( layer )):
			self.versions_lw.addItem( a )

	def getRenderPathForShot(self, sho):
		"""docstring for getRenderPathForShot"""
		filePrefix = self.gen[ "renderpath" ] + self.gen[ "shotrenderpath" ]
		if sho.type == 'asset':
			filePrefix = filePrefix.replace( '<project>', sho.project.name )
			filePrefix = filePrefix.replace( '<asset>', sho.name )
		else:
			filePrefix = filePrefix.replace( '<project>', sho.project.name )
			filePrefix = filePrefix.replace( '<sequence>', sho.sequence.name )
			filePrefix = filePrefix.replace( '<shot>', sho.name )
		return filePrefix.split( '<RenderLayer>' )[0]

	def addLayer(self):
		"""docstring for fname"""
		stacks = commands.nodesOfType("RVStackGroup")
		commands.setViewNode( stacks[0] )
		layer = self._selectedRender
		version = self._selectedVersion
		sqfFil = sqf.sequenceFile( layer + '/' + version + '/' + self._selectedLayer + '.exr' )
		asd = commands.addSourceVerbose( [layer + '/' + version + '/' + self._selectedLayer + '.' + str(sqfFil.start) + '-' + str(sqfFil.end) + '#.exr'], None )
		assGroup = commands.nodeGroup(asd)
		commands.setStringProperty(assGroup + '.ui.name', [self._selectedShot.name + ' - ' + self._selectedLayer + ' - ' + version])
		item = QtGui.QListWidgetItem(self._selectedShot.name + ' - ' + self._selectedLayer + ' - ' + version )
		item.setCheckState( QtCore.Qt.Checked )
		item.setData(32, [asd, [sqfFil, self._selectedShot, self._selectedLayer, version ]] )
		self.viewLayers_lw.addItem( item )

	def removeLayer(self):
		"""docstring for fname"""
		lay = self.viewLayers_lw.selectedItems()[0]
		self.viewLayers_lw.takeItem( self.viewLayers_lw.row( lay ) )
		assGroup = commands.nodeGroup(lay.data(32)[0])
		commands.deleteNode( assGroup )

	def changeLayerVis(self, item):
		"""docstring for changeLayerVis(self, item"""
		sourNode = item.data(32)[0]
		sourceMedia = commands.getStringProperty( sourNode + '.media.movie' )
		trf = extra_commands.associatedNode( 'RVTransform2D', sourNode )
		if item.checkState() == QtCore.Qt.Checked: #TURN ON LAYER
			commands.setFloatProperty( trf + '.transform.scale', [1.0,1.0] )
		else: #TURN OFF LAYER
			commands.setFloatProperty( trf + '.transform.scale', [0.0,0.0] )

	def publish(self):
		"""docstring for publish"""
		mails = ''
		mailNoti = 'false'
		if self.gen[ "sendmail" ] == 'True':
			mails = ','.join( ml.getUsersInDepartments( ['compo', 'lighting', 'production'], self.gen[ "departmentspath" ] ) )
			mailNoti = 'true'
		for i in range( self.viewLayers_lw.count() ):
			item = self.viewLayers_lw.item( i )
			if item.checkState() == QtCore.Qt.Checked:
				sqFile, sho, layer, version = item.data(32)[1]
				sqFile.copy( sho.publish3DPath + '/' + layer + '/' + version + '/' )
				if self.gen[ "sendmail" ]:
					ml.mailFromTool( 'new_render',
						{ '<ProjectName>': sho.project.name,
						'<SequenceName>': sho.sequence.name,
						'<ShotName>': sho.name,
						'<RenderLayer>': layer + ' - ' + version,
						'<UserName>': os.getenv('username'),
						'<Path>' : sho.publish3DPath + '/' + layer + '/' + version + '/' },
						os.getenv('username') + '@bitt.com',
						self.gen[ "departmentspath" ] , self.gen[ "mailserver" ], self.gen[ "mailport" ]  )
		msgBox = QMessageBox()
		msgBox.setText("All renderlayers have been published.")
		msgBox.exec_()






