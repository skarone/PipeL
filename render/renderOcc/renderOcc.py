import general.mayaNode.mayaNode as mn
reload( mn )
import maya.cmds as mc
import render.aov.aov as aov
reload( aov )
import pipe.mayaFile.mayaFile as mfl
reload(mfl)
import pipe.settings.settings as sti
reload( sti )
import os
import render.deadline.deadline as dl
reload( dl )
import pipe.project.project as prj

def getCurrentCamera():
    '''
    gets the current maya viewport camera
    '''
    pan = mc.getPanel(wf=True)
    cam = mc.modelPanel(pan, q=True, camera=True)
    return mn.Node( cam )

def renderOcc( motionBlur, group ):
	#setup render settings
	curFile = mfl.currentFile()
	dead = dl.Deadline()
	defRenderGlobals = mn.Node( 'defaultRenderGlobals' )
	defRenderGlobals.a.currentRenderer.v = 'arnold'
	defRenderGlobals.a.animation.v = True
	defRenderGlobals.a.extensionPadding.v = 4
	defRenderGlobals.a.putFrameBeforeExt.v = 1
	defArnoldRenderOptions = mn.Node( 'defaultArnoldRenderOptions' )
	defArnoldRenderOptions.a.motion_blur_enable.v = motionBlur
	defArnoldRenderOptions.a.motion_steps.v = 3
	mn.Node( 'defaultArnoldDriver' ).a.aiTranslator.v = 'exr'
	attrs = [ 'ignoreAtmosphere', 'ignoreLights',
			'ignoreShadows', 'ignoreDisplacement', 'ignoreBump' ]
	for a in attrs:
		defArnoldRenderOptions.attr( a ).v = 1
	defArnoldRenderOptions.a.AASamples.v = 3
	attrs = [ 'GIDiffuseSamples', 'GIGlossySamples',
			'GIRefractionSamples', 'sssBssrdfSamples', 'volumeIndirectSamples' ]
	for a in attrs:
		defArnoldRenderOptions.attr( a ).v = 0
	#TURN OFF ALL CAMERAS RENDERABLES
	for c in mn.ls( typ = 'camera' ):
		c.a.renderable.v = 0
	#TURN CAMERA TO RENDER ON
	currCam = getCurrentCamera()
	currCam.shape.a.renderable.v = 1
	#TURN OFF ALL IMAGE PLANES
	imagePlanes = mn.ls( exactType = 'imagePlane' )
	for i in imagePlanes:
		i.a.alphaGain.v = 0
	#set attributes on for all the meshes
	attrs = [ 'castsShadows', 'receiveShadows',
			'primaryVisibility', 'motionBlur' ]
	for n in mn.ls( typ = 'mesh' ):
		for a in attrs:
			n.attr( a ).v = 1
	#Turn OFF ALL AOVS
	for ao in aov.aovsInScene():
		ao.a.enabled.v = 0
	#Create OCC AOV
	aovNode = mn.Node( 'aiAOV_Aov_OCC' )
	if not aovNode.exists:
		aovNode = aov.create( aovName = 'Aov_OCC' , aovType = 6 )
	#Turn On OCC AOV
	aovNode.a.enabled.v = 1
	createShader(aovNode)
	#write job for render
	settings = sti.Settings()
	gen = settings.General
	renderPath = 'R:/'
	if gen:
		renderPath = gen[ "renderpath" ]
		if not renderPath.endswith( '/' ):
			renderPath += '/'
	assOrShot = prj.shotOrAssetFromFile( curFile )
	name = ''
	filename = ''
	if assOrShot:
		if assOrShot.type == 'shot':
			if gen.has_key( 'greypath' ):
				filePrefix = renderPath + gen[ "greypath" ]
			else:
				filePrefix = renderPath + '/<project>' + '/' + '<sequence>' + '/' + '<shot>' + '/Grey/' + '<RenderLayerVersion>' + '/Grey'
			#replace <tags> to final names
			filePrefix = getFilePrefixFromTags( filePrefix, assOrShot )
		else:
			print 'Cant Detect current shot :(, please save scene if its is a shot'
			return
		if '<RenderLayerVersion>' in filePrefix:
			versionNumber = _getVersionNumber( filePrefix.split( '<RenderLayerVersion>' )[0] )
			filePrefix = filePrefix.replace( '<RenderLayerVersion>', 'v' + str(versionNumber).zfill( 4 ) )
		filename = filePrefix + '.' + ('?'*4) + os.path.splitext( filename )[1]
		name = assOrShot.project.name + ' - '
	else:
		print 'please save scene in project'
		return
	curFile.newVersion()
	curFile.save()
	Job = dl.Job( 'defaultRenderLayer',
			{		'Plugin'          : 'MayaBatch',
					'Group'           : group,
					'Pool'            : '',
					'Frames'          : str( int( mc.playbackOptions( q = True, min = True ) ) ) + "-" + str( int( mc.playbackOptions( q = True, max = True ) ) ),
					'Comment'         : '',
					'InitialStatus'   : 'Active',
					'Whitelist'       : '',
					'Name'            : name + curFile.name + ' - ' + 'Grey',
					'OutputFilename0' : filename,
					'Priority'        : 50,
					'ChunkSize'       : 5,
					'OutputDirectory0': filename
					},{'CommandLineOptions' : '-rl ' + 'defaultRenderLayer' + ' -mr:art ',
						'UsingRenderLayers' : 1,
						#'ProjectPath'       : projPath,
						'RenderLayer'       : 'defaultRenderLayer',
						'OutputFilePrefix'  : filePrefix,
						'OutputPath'        : filename
					}, curFile )
	Job.write()
	dead.runMayaJob( Job )
	#TURN ON IMAGE PLANES
	for i in imagePlanes:
		i.a.alphaGain.v = 1

def getFilePrefixFromTags( filePrefix, shot ):
	"""return filePrefix Path replacing tags"""
	filePrefix = filePrefix.replace( '<project>', shot.project.name )
	filePrefix = filePrefix.replace( '<sequence>', shot.sequence.name )
	filePrefix = filePrefix.replace( '<shot>', shot.name )
	return filePrefix

def createShader(aovNode):
	"""docstring for createShader"""
	#Create Utility base Shader
	utilMat = mn.Node( 'OccUtil_MAT')
	if not utilMat.exists:
		utilMat = mn.createNode( 'aiUtility' )
		utilMat.a.shadeMode.v = 2
		utilMat.name = 'OccUtil_MAT'
	#Create TripleSwitch
	tripleSwitch = mn.Node( 'OccTripleSwith_TS')
	if not tripleSwitch.exists:
		tripleSwitch = mn.createNode( 'tripleShadingSwitch' )
		tripleSwitch.name = 'OccTripleSwith_TS'
	if not tripleSwitch.a.output.isConnected( utilMat.a.color ):
		tripleSwitch.a.output >> utilMat.a.color
	#Create OCC Shader
	occMat = mn.Node( 'Occ_MAT' )
	if not occMat.exists:
		occMat = mn.createNode( 'aiAmbientOcclusion' )
		occMat.name = 'Occ_MAT'
	if not occMat.a.outColor.isConnected( tripleSwitch.a.default ):
		occMat.a.outColor >> tripleSwitch.a.default
	count = 0
	#get shapes with customs attributes
	for sha in mn.ls( typ = 'mesh', ni = True ):
		if sha.a.iris_Occ.exists:
			#create Iris for this shape
			irisMat = mn.Node( 'irisOcc_MAT' )
			if not irisMat.exists:
				irisMat = mn.createNode( 'surfaceShader' )
				irisMat.name = 'irisOcc_MAT'
			#connect shape with tripleswitch and irisMat
			if not sha.attr('instObjGroups[0]').isConnected( tripleSwitch.attr( 'input[' + str(count) +'].inShape')):
				sha.attr('instObjGroups[0]') >> tripleSwitch.attr( 'input[' + str(count) +'].inShape')
			if not irisMat.a.outColor.isConnected( tripleSwitch.attr( 'input[' + str(count) +'].inTriple') ):
				irisMat.a.outColor >> tripleSwitch.attr( 'input[' + str(count) +'].inTriple')
			count += 1
			continue
		if sha.a.texture_Occ.exists:
			#create Occ with texture for this shape
			occMat = mn.Node( sha.name + 'Occ_MAT' )
			if not occMat.exists:
				occMat = mn.createNode( 'aiAmbientOcclusion' )
				occMat.name = sha.name + 'Occ_MAT'
			fileMat = mn.Node( sha.name + 'file_Occ_MAT' )
			if not fileMat.exists:
				fileMat = mn.createNode( 'file' )
				fileMat.name = sha.name + 'file_Occ_MAT'
			fileMat.a.ftn.v = sha.a.texture_Occ.v
			if not fileMat.a.outColor.isConnected( occMat.a.white ):
				fileMat.a.outColor >> occMat.a.white
			if not sha.attr('instObjGroups[0]').isConnected( tripleSwitch.attr( 'input[' + str(count) +'].inShape') ):
				sha.attr('instObjGroups[0]') >> tripleSwitch.attr( 'input[' + str(count) +'].inShape')
			if not occMat.a.outColor.isConnected( tripleSwitch.attr( 'input[' + str(count) +'].inTriple') ):
				occMat.a.outColor >> tripleSwitch.attr( 'input[' + str(count) +'].inTriple')
			count += 1
		if sha.a.hideForOcc.exists:
			sha.a.castsShadows.v = False
			sha.a.primaryVisibility.v = False
	#Connect Shader to AOV
	if not utilMat.a.outColor.isConnected( aovNode.a.defaultValue ):
		utilMat.a.outColor >> aovNode.a.defaultValue

def _getVersionNumber( path):
	"""return version number for render folder"""
	if not os.path.exists( path ):
		return 1
	return len( [a for a in os.listdir( path ) if os.path.isdir( path + '/' + a ) ] ) + 1




