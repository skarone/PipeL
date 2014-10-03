from glob import glob
import re
import os
import pipe.settings.settings as sti
reload( sti )
import pipe.project.project as prj
import pipe.sequence.sequence as sq
import pipe.shot.shot as sh
import pipe.sequenceFile.sequenceFile as sqFil
import nuke

#print getFileSeq( 'R:/Pony_Halloween_Fantasmas/Terror/s004_T04/v0011/Fondo_Beauty' )


def createVersionKnobs():
	'''
	Add as callback to add user knobs in Read nodes.
	In menu.py or init.py:
	   nuke.addOnUserCreate( nuk.general.read.createVersionKnobs, nodeClass='Read' )        
	'''
	# CREATE USER KNOBS
	node        = nuke.thisNode()
	addKnobs( node )
	# UPDATE THE VERSION KNOB SO IT SHOWS WHAT'S ON DISK / IN THE DATABASE
	fillProjects(node)

def addKnobs( node ):
	tabKnob     = nuke.Tab_Knob( 'PipeL', 'PipeL' )
	projKnob    = nuke.Enumeration_Knob( 'projectSel', 'Project', [] )
	seqKnob     = nuke.Enumeration_Knob( 'seqSel', 'Sequence', [] )
	shotKnob    = nuke.Enumeration_Knob( 'shotSel', 'Shot', [] )
	layerKnob   = nuke.Enumeration_Knob( 'layerSel', 'Layer', [] )
	updateKnob  = nuke.PyScript_Knob( 'update', 'update' )
	versionKnob = nuke.Enumeration_Knob( '_version', 'version', [] ) # DO NOT USE "VERSION" AS THE KNOB NAME AS THE READ NODE ALREADY HAS A "VERSION" KNOB
	loadKnob    = nuke.PyScript_Knob( 'load', 'load' )
	copyKnob    = nuke.Boolean_Knob( 'copy', 'Copy To Local', 0 )
	updateKnob.setValue( 'import nuk.general.read as rd; rd.fillVersions()' )
	loadKnob.setValue( 'import nuk.general.read as rd; rd.loadFile()' )
	# ADD NEW KNOBS TO NODE
	for k in ( tabKnob, projKnob, seqKnob, shotKnob, layerKnob, updateKnob, versionKnob, loadKnob, copyKnob ):
		node.addKnob( k )

def fillProjects( node ):
	"""docstring for fillProjects"""
	settings = sti.Settings()
	gen = settings.General
	if gen:
		basePath = gen[ "basepath" ]
		if basePath:
			if basePath.endswith( '\\' ):
				basePath = basePath[:-1]
			prj.BASE_PATH = basePath.replace( '\\', '/' )
		renderPath = gen[ "renderpath" ]
		node[ 'projectSel' ].setValues( prj.projects( prj.BASE_PATH ) )
	root = nuke.root()
	if root.knob('pipPorject'):
		pipPorj = root[ 'pipPorject' ].value()
		pipSeq  = root[ 'pipSequence' ].value()
		pipShot = root[ 'pipShot' ].value()
		node[ 'projectSel' ].setValue( pipPorj )
		node[ 'seqSel' ].setValues( [s.name for s in prj.Project( pipPorj ).sequences] )
		node[ 'seqSel' ].setValue( pipSeq )
		node[ 'shotSel' ].setValues( [ s.name for s in sq.Sequence( pipSeq, prj.Project( pipPorj )).shots ]  )
		node[ 'shotSel' ].setValue( pipShot )
		node[ 'layerSel' ].setValues( sh.Shot( pipShot, sq.Sequence( pipSeq, prj.Project( pipPorj ))).renderedLayers( renderPath ) )
		node[ '_version' ].setValues( sh.Shot( pipShot, sq.Sequence( pipSeq, prj.Project( pipPorj ))).renderedLayerVersions( renderPath, node[ 'layerSel' ].value() ) )
		vers = sorted( node[ '_version' ].values() )
		node[ '_version' ].setValue( vers[-1] )
	else:
		f = nuke.getClipname("Select clip")
		node['file'].fromUserText(f)

def loadFile():
	node    = nuke.thisNode()
	#HERE WE NEED TO CREATE PATH SO WE CAN READ FILE
	settings = sti.Settings()
	gen = settings.General
	if gen:
		renderPath = gen[ "renderpath" ]
		localNuke  = gen[ "localnukepath" ]
	pathDir = getPathDir( renderPath, node )
	seqNode = sqFil.sequenceFile( pathDir + node[ 'layerSel' ].value() + '.*' )
	if node[ 'copy' ].value():
		newPath = pathFromStructure( localNuke, node[ 'projectSel' ].value(), node[ 'seqSel' ].value(), node[ 'shotSel' ].value(), node[ 'layerSel' ].value() )
		seqNode = seqNode.copy( newPath + node[ '_version' ].value() + '/' )
	node['file'].setValue( seqNode.seqPath )
	node['first'].setValue( seqNode.start )
	node['last'].setValue( seqNode.end )
	checkVersion( node, renderPath )

def updateVersionKnob():
	'''
	Add as callback to list versions per type in Read node's user knob
	In menu.py or init.py:
	   nuke.addKnobChanged( nuk.general.read.updateVersionKnob, nodeClass='Read' )  
	'''
	"""update list of version of the render in the node"""
	node = nuke.thisNode()
	knob = nuke.thisKnob()

	# RUN ONLY IF THE TYPE KNOB CHANGES OR IF THE NODE PANEL IS OPENED.
	settings = sti.Settings()
	gen = settings.General
	if gen:
		basePath = gen[ "basepath" ]
		if basePath:
			if basePath.endswith( '\\' ):
				basePath = basePath[:-1]
			prj.BASE_PATH = basePath.replace( '\\', '/' )
		renderPath = gen[ "renderpath" ]
	#UPDATE SEQUENCES BECAUSE PROJECTSEL HAS CHANGE
	if not knob or knob.name() in [ 'projectSel', 'showPanel' ]:
		node[ 'seqSel' ].setValues( [s.name for s in prj.Project( node[ 'projectSel' ].value() ).sequences] )

	#UPDATE SHOTS BECAUSE SEQSEL HAS CHANGE
	if not knob or knob.name() in [ 'seqSel', 'showPanel' ]:
		node[ 'shotSel' ].setValues( [ s.name for s in sq.Sequence( node[ 'seqSel' ].value(), prj.Project( node[ 'projectSel' ].value() )).shots ]  )
	
	#UPDATE SHOTS BECAUSE SEQSEL HAS CHANGE
	if not knob or knob.name() in [ 'shotSel', 'showPanel' ]:
		node[ 'layerSel' ].setValues( sh.Shot( node[ 'shotSel' ].value(),sq.Sequence( node[ 'seqSel' ].value(), prj.Project( node[ 'projectSel' ].value() ))).renderedLayers( renderPath ) )

	#UPDATE SHOTS BECAUSE SEQSEL HAS CHANGE
	if not knob or knob.name() in [ 'layerSel', 'showPanel' ]:
		node[ '_version' ].setValues( sh.Shot( node[ 'shotSel' ].value(),sq.Sequence( node[ 'seqSel' ].value(), prj.Project( node[ 'projectSel' ].value() ))).renderedLayerVersions( renderPath, node[ 'layerSel' ].value() ) )
		#vers = sorted( node[ '_version' ].values() )
		#node[ '_version' ].setValue( vers[-1] )

def fillVersions():
	"""docstring for fillVersions"""
	settings = sti.Settings()
	gen = settings.General
	node = nuke.thisNode()
	knob = nuke.thisKnob()
	if gen:
		basePath = gen[ "basepath" ]
		if basePath:
			if basePath.endswith( '\\' ):
				basePath = basePath[:-1]
			prj.BASE_PATH = basePath.replace( '\\', '/' )
		renderPath = gen[ "renderpath" ]
	node[ '_version' ].setValues( sh.Shot( node[ 'shotSel' ].value(),sq.Sequence( node[ 'seqSel' ].value(), prj.Project( node[ 'projectSel' ].value() ))).renderedLayerVersions( renderPath, node[ 'layerSel' ].value() ) )

def checkVersions( ):
	"""docstring for fname"""
	settings = sti.Settings()
	gen = settings.General
	if gen:
		basePath = gen[ "basepath" ]
		if basePath:
			if basePath.endswith( '\\' ):
				basePath = basePath[:-1]
			prj.BASE_PATH = basePath.replace( '\\', '/' )
		renderPath = gen[ "renderpath" ]
	for node in nuke.allNodes():
		if node.Class()=='Read':
			checkVersion( node, renderPath )

def checkVersion( node, renderPath ):
	"""docstring for checkVersion"""
	if node.knob('_version'):
		if not node[ '_version' ].value() == '0':
			currentVersion = node[ '_version' ].value()
			node[ '_version' ].setValues( sh.Shot( node[ 'shotSel' ].value(),sq.Sequence( node[ 'seqSel' ].value(), prj.Project( node[ 'projectSel' ].value() ))).renderedLayerVersions( renderPath, node[ 'layerSel' ].value() ) )
			node[ '_version' ].setValue( currentVersion )
			vers = sorted( node[ '_version' ].values() )
			if not vers[-1] ==  currentVersion:
				hexColour = int('%02x%02x%02x%02x' % (255,255,0,1),16)
				node['tile_color'].setValue( hexColour )
			else:
				node['tile_color'].setValue( 0 )

def getPathDir( renderPath, node ):
	"""docstring for getPathDir"""
	curShot = sh.Shot( node[ 'shotSel' ].value(),sq.Sequence( node[ 'seqSel' ].value(), prj.Project( node[ 'projectSel' ].value() )))
	path    = curShot.renderedLayerVersionPath( renderPath, node[ 'layerSel' ].value(), node[ '_version' ].value() )
	return path

def pathFromStructure( basePath, project, sequence, shot, layer ):
	"""
	basePath should be something like this...
	"D:/Projects/<project>/Sequences/<sequence>/Shots/<shot>/Renders/<layer>"
	X:/<project>/-Materiales-/3D/<sequence>/<shot>/<layer>
	"""
	basePath = basePath.replace( '<project>', project )
	basePath = basePath.replace( '<sequence>', sequence )
	basePath = basePath.replace( '<shot>', shot )
	return basePath.replace( '<layer>', layer ) + '/'

	
