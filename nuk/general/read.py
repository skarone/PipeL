from glob import glob
import re
import os
import pipe.settings.settings as sti
reload( sti )
import pipe.project.project as prj

def getFileSeq( dirPath ):
	'''Return file sequence with same name as the parent directory. Very loose example!!'''
	dirName = os.path.basename( dirPath )
	# COLLECT ALL FILES IN THE DIRECTORY THAT HVE THE SAME NAME AS THE DIRECTORY
	files = sorted(glob( os.path.join( dirPath, '%s.*.*' % dirName ) ))
	# GRAB THE RIGHT MOST DIGIT IN THE FIRST FRAME'S FILE NAME
	firstString = re.findall( r'\d+', files[0] )[-1]
	# GET THE PADDING FROM THE AMOUNT OF DIGITS
	padding = len( firstString )
	# CREATE PADDING STRING FRO SEQUENCE NOTATION
	paddingString = '%04s' % padding
	# CONVERT TO INTEGER
	first = int( firstString )
	# GET LAST FRAME
	last = int( re.findall( r'\d+', files[-1] )[-1] )
	# GET EXTENSION
	ext = os.path.splitext( files[0] )[-1]
	# BUILD SEQUENCE NOTATION
	fileName = '%s.%%%sd%s' % ( dirName, str(padding).zfill(2), ext )
	# RETURN FULL PATH AS SEQUENCE NOTATION
	return os.path.join( dirPath, fileName ),[ first, last ]

#print getFileSeq( 'R:/Pony_Halloween_Fantasmas/Terror/s004_T04/v0011/Fondo_Beauty' )

def createVersionKnobs():
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
	updateKnob.setValue( 'assetManager.updateVersionKnob()' )
	loadKnob.setValue( 'assetManager.loadFile()' )
	# ADD NEW KNOBS TO NODE
	for k in ( tabKnob, projKnob, seqKnob, shotKnob, layerKnob, updateKnob, versionKnob, loadKnob ):
		node.addKnob( k )
	# UPDATE THE VERSION KNOB SO IT SHOWS WHAT'S ON DISK / IN THE DATABASE
	updateVersionKnob()

def loadFile():
	node    = nuke.thisNode()
	projSel = node[ 'projectSel' ].value()
	seqSel  = node[ 'seqSel' ].value()
	shotSel = node[ 'shotSel' ].value()
	laySel  = node[ 'layerSel' ].value()
	verSel  = node[ '_version' ].value()
	#HERE WE NEED TO CREATE PATH SO WE CAN READ FILE
	pathDir = getPathDir()
	getFileSeq( pathDir )
	first, last = range.split('-')
	node['file'].setValue( path )
	node['first'].setValue( int(first) )
	node['last'].setValue( int(last) )

def updateVersionKnob():
	"""update list of version of the render in the node"""
	node = nuke.thisNode()
	knob = nuke.thisKnob()

	# RUN ONLY IF THE TYPE KNOB CHANGES OR IF THE NODE PANEL IS OPENED.
	settings = sti.Settings()
	gen = self.settings.General
	if gen:
		basePath = gen[ "basepath" ]
		if basePath:
			if basePath.endswith( '\\' ):
				basePath = basePath[:-1]
			prj.BASE_PATH = basePath.replace( '\\', '/' )

	#UPDATE SEQUENCES BECAUSE PROJECTSEL HAS CHANGE
	if not knob or knob.name() in [ 'projectSel', 'showPanel' ]:
		node[ 'seqSel' ].setValues( prj.Project( node[ 'projectSel' ].value() ).sequences )

	#UPDATE SHOTS BECAUSE SEQSEL HAS CHANGE
	if not knob or knob.name() in [ 'seqSel', 'showPanel' ]:
		node[ 'shotSel' ].setValues( sq.Sequence( node[ 'seqSel' ].value(), prj.Project( node[ 'projectSel' ].value() )).shots  )
	
	#UPDATE SHOTS BECAUSE SEQSEL HAS CHANGE
	if not knob or knob.name() in [ 'seqSel', 'showPanel' ]:
		node[ 'layerSel' ].setValues( sh.Shot( node[ 'shotSel' ].value(),sq.Sequence( node[ 'seqSel' ].value(), prj.Project( node[ 'projectSel' ].value() ))).layers )
