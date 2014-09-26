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
	tabKnob     = nuke.Tab_Knob( 'PipeL', 'PipeL' )
	projKnob    = nuke.Enumeration_Knob( 'projectSel', 'Project', [] )
	seqKnob     = nuke.Enumeration_Knob( 'seqSel', 'Sequence', [] )
	shotKnob    = nuke.Enumeration_Knob( 'shotSel', 'Shot', [] )
	layerKnob   = nuke.Enumeration_Knob( 'layerSel', 'Layer', [] )
	updateKnob  = nuke.PyScript_Knob( 'update', 'update' )
	versionKnob = nuke.Enumeration_Knob( '_version', 'version', [] ) # DO NOT USE "VERSION" AS THE KNOB NAME AS THE READ NODE ALREADY HAS A "VERSION" KNOB
	loadKnob    = nuke.PyScript_Knob( 'load', 'load' )
	updateKnob.setValue( 'import nuk.general.read as rd; rd.updateVersionKnob()' )
	loadKnob.setValue( 'import nuk.general.read as rd; rd.loadFile()' )
	# ADD NEW KNOBS TO NODE
	for k in ( tabKnob, projKnob, seqKnob, shotKnob, layerKnob, updateKnob, versionKnob, loadKnob ):
		node.addKnob( k )
	# UPDATE THE VERSION KNOB SO IT SHOWS WHAT'S ON DISK / IN THE DATABASE
	fillProjects()

def fillProjects():
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
	node = nuke.thisNode()
	root = nuke.root()
	node[ 'projectSel' ].setValues( prj.projects( prj.BASE_PATH ) )
	node[ 'seqSel' ].setValues( [s.name for s in prj.Project( root[ 'pipPorject' ].value() ).sequences] )
	node[ 'shotSel' ].setValues( [ s.name for s in sq.Sequence( root[ 'pipSequence' ].value(), prj.Project( root[ 'pipPorject' ].value() )).shots ]  )
	node[ 'layerSel' ].setValues( sh.Shot( root[ 'pipShot' ].value(),sq.Sequence( root[ 'pipSequence' ].value(), prj.Project( root[ 'pipPorject' ].value() ))).renderedLayers( renderPath ) )
	node[ '_version' ].setValues( sh.Shot( root[ 'pipShot' ].value(),sq.Sequence( root[ 'pipSequence' ].value(), prj.Project( root[ 'pipPorject' ].value() ))).renderedLayerVersions( renderPath, node[ 'layerSel' ].value() ) )
	
	node[ 'projectSel' ].setValue( root[ 'pipPorject' ].value() )
	node[ 'seqSel' ].setValue( root[ 'pipSequence' ].value() )
	node[ 'shotSel' ].setValue( root[ 'pipShot' ].value() )

def loadFile():
	node    = nuke.thisNode()
	#HERE WE NEED TO CREATE PATH SO WE CAN READ FILE
	settings = sti.Settings()
	gen = settings.General
	if gen:
		renderPath = gen[ "renderpath" ]
	pathDir = getPathDir( renderPath, node )
	print pathDir
	seqNode = sqFil.sequenceFile( pathDir + node[ 'layerSel' ].value() + '.*' )
	print pathDir + node[ 'layerSel' ].value() + '.*'
	print seqNode.files
	node['file'].setValue( seqNode.seqPath )
	node['first'].setValue( seqNode.start )
	node['last'].setValue( seqNode.end )

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
	
	root = nuke.root()
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

	#NOW IT WOULD BE GREAT TO SET ALL THIS KNOBS BASED ON ENVIROMENT VARIABLES

def getPathDir( renderPath, node ):
	"""docstring for getPathDir"""
	curShot = sh.Shot( node[ 'shotSel' ].value(),sq.Sequence( node[ 'seqSel' ].value(), prj.Project( node[ 'projectSel' ].value() )))
	path    = curShot.renderedLayerVersionPath( renderPath, node[ 'layerSel' ].value(), node[ '_version' ].value() )
	return path
	
