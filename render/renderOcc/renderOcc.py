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
	attrs = [ 'ignoreTextures', 'ignoreAtmosphere', 'ignoreLights', 'ignoreShadows', 'ignoreDisplacement', 'ignoreBump' ]
	for a in attrs:
		defArnoldRenderOptions.attr( a ).v = 1
	defArnoldRenderOptions.a.AASamples.v = 3
	attrs = [ 'GIDiffuseSamples', 'GIGlossySamples', 'GIRefractionSamples', 'sssBssrdfSamples', 'volumeIndirectSamples' ]
	for a in attrs:
		defArnoldRenderOptions.attr( a ).v = 0
	#TURN OFF ALL CAMERAS RENDERABLES
	for c in mn.ls( typ = 'camera' ):
		c.a.renderable.v = 0
	#TURN CAMERA TO RENDER ON
	currCam = getCurrentCamera()
	currCam.shape.a.renderable.v = 1

	#set attributes on for all the meshes
	attrs = [ 'castsShadows', 'receiveShadows', 'primaryVisibility', 'motionBlur' ]

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
	#Create OCC Shader
	occMat = mn.Node( 'Occ_MAT' )
	if not mn.Node( 'Occ_MAT' ).exists:
		occMat = mn.createNode( 'aiAmbientOcclusion' )
		occMat.name = 'Occ_MAT'
	#Connect Shader to AOV
	if not occMat.a.outColor.isConnected( aovNode.a.defaultValue ):
		occMat.a.outColor >> aovNode.a.defaultValue
	#write job for render
	settings = sti.Settings()
	gen = settings.General
	renderPath = 'R:/'
	if gen:
		renderPath = gen[ "renderpath" ]
		print renderPath
		if not renderPath.endswith( '/' ):
			renderPath += '/'
	assOrShot = prj.shotOrAssetFromFile( curFile )
	name = ''
	filename = ''
	if assOrShot:
		if assOrShot.type == 'asset':
			filePrefix = renderPath + assOrShot.project.name + '/Asset/' + assOrShot.name + '/defaultRenderLayer/' + '<RenderLayerVersion>' + '/defaultRenderLayer'
		elif assOrShot.type == 'shot':
			filePrefix = renderPath + assOrShot.project.name + '/' + assOrShot.sequence.name + '/' + assOrShot.name + '/defaultRenderLayer/' + '<RenderLayerVersion>' + '/defaultRenderLayer'
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
					'Name'            : name + curFile.name + ' - ' + 'defaultRenderLayer',
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

def _getVersionNumber( path):
	"""return version number for render folder"""
	if not os.path.exists( path ):
		return 1
	return len( [a for a in os.listdir( path ) if os.path.isdir( path + '/' + a ) ] ) + 1




