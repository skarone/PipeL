import hou
import pipe.project.project as prj
import pipe.sequenceFile.sequenceFile as sqFil
import pipe.houdiniFile.houdiniFile as hfl
import tempfile
import shutil
import pipe.file.file as fl
import os


def loadCamera( projName, seqName, shotName, globalScale = False ):
	"""load alembic camera for shot"""
	proj = prj.Project( projName )
	seq  = proj.sequence( seqName )
	sht  = seq.shot( shotName )
	al = hou.node( '/obj' ).createNode( 'alembicarchive' )
	al.setName( 'CameraPool' )
	al.parm( 'fileName').set( sht.poolCamPath.replace( '.ma', '.abc' ))
	al.parm('buildHierarchy').pressButton()
	if globalScale:
		gScale = hou.node( '/obj/globalScale' )
		if not gScale:
			gScale = hou.node( '/obj' ).createNode( 'null', 'globalScale' )
		al.setInput(0, gScale)

def copyTimeSettings( projName, seqName, shotName ):
	"""copy time settings from animation file"""
	proj = prj.Project( projName )
	seq  = proj.sequence( seqName )
	sht  = seq.shot( shotName )
	tim = sht.animPath.time
	fpsVals = {'pal':25,'film':24}
	hou.setFps( fpsVals[tim['tim']] )
	cmd = 'tset `('+ str( tim[ 'ast' ] ) +'-1)/$FPS` `'+ str( tim[ 'aet' ] )+'/$FPS`'
	hou.hscript(cmd)
	hou.playbar.setPlaybackRange( tim[ 'ast' ], tim[ 'aet' ])

def loadAllCaches( projName, seqName, shotName ):
	"""load all caches from shot"""
	proj = prj.Project( projName )
	seq  = proj.sequence( seqName )
	sht  = seq.shot( shotName )
	caches = sht.caches
	for a in caches.keys():
		for c in caches[a]:
			loadAlembic( c )

def loadAlembic( cache, globalScale = False ):
	"""load alembic from cacheFile, connect to transform to manage global scale"""
	geo = hou.node( '/obj' ).createNode( 'geo' )
	geo.setName( cache.name + '_geo' )
	geo.children()[0].destroy()
	al = geo.createNode( 'alembic' )
	al.setName( cache.name + '_abc' )
	al.parm( 'fileName' ).set( cache.path )
	if globalScale:
		gScale = hou.node( '/obj/globalScale' )
		if not gScale:
			gScale = hou.node( '/obj' ).createNode( 'null', 'globalScale' )
		geo.setInput(0, gScale)
			


def playblast( fi ):
	"""fi = <path>/file.png
	import general.houdini.utils as hut
	hut.playblast( 'D:/testPlay/test.png' )
	"""
	gl = hou.node( '/out' ).createNode( 'opengl' )
	gl.setName( 'playblast' )
	tmpFile = tempfile.gettempdir() + '/playblastTmp/' + fi.name
	gl.parm( 'picture' ).set( tmpFile + '.$F4.png' )
	gl.parm( 'picture' ).pressButton()
	gl.parm( 'imgformat' ).set( 'PNG' )
	cam = getRenderCamera()
	gl.parm( 'camera' ).set( cam.path() )
	#set frame range
	gl.parm( 'trange' ).set(1)
	gl.parm( 'aamode' ).set( 3 )
	gl.parm( 'gamma' ).set( 2.2 )
	frameRange = getFrameRangeFromTimeline()
	gl.parm( 'f1' ).set(frameRange[0])
	gl.parm( 'f2' ).set(frameRange[1])
	gl.parm( 'execute').pressButton()
	sqFile = sqFil.sequenceFile( tmpFile + '.png' )

	sqFile.createMov( fi.dirPath, '', int(hou.fps()), sqFile.name )
	os.system("start "+ str( fi.path ) )	
	shutil.rmtree( tempfile.gettempdir() + '/playblastTmp/' )
	gl.destroy()
	
def playblastCurrentFile():
	"""docstring for playblastCurrentFile"""
	fil = hfl.currentFile()
	if not fil:
		print 'Please Save File To create Playblast'
		return
	movFil = fl.File( fil.versionPath + fil.name + '_v' + str( fil.version ).zfill( 3 ) + '.mov' )
	fil.newVersion();fil.save()
	playblast( movFil )
	if movFil.exists:
		movFil.copy( fil.dirPath + fil.name + '.mov' )


def getRenderCamera():
	"""return render camera from scene"""
	return hou.ui.paneTabOfType(hou.paneTabType.SceneViewer).curViewport().camera()

def getFrameRangeFromTimeline():
	"""return start and end frame setted in timeline"""
	return hou.playbar.playbackRange()
