import maya.mel as mm
import maya.cmds as mc
import general.mayaNode.mayaNode as mn
import pipe.file.file as fl
import pipe.mayaFile.mayaFile as mfl
import tempfile
import pipe.sequenceFile.sequenceFile as sqFil
reload( sqFil )
import os
import shutil


def playblastCurrentFile():
	"""playblast current File"""
	fil = mfl.currentFile()
	if not fil:
		print 'Please Save File To create Playblast'
		return
	movFil = fl.File( fil.versionPath + fil.name + '_v' + str( fil.version ).zfill( 3 ) + '.mov' )
	playblast( movFil )

def playblast( movFil ):
	"""main playblast function
	param path: string for the path for the playblast"""
	mm.eval( 'setAllMainWindowComponentsVisible 0;' )
	try:
		resNode = mn.Node( 'defaultResolution' )
		#resolution = [ resNode.a.width.v, resNode.a.height.v ]
		resolution = [ 1280, 720 ]
		#CREATE PLAYBLAST
		#write files in tmp dir
		mc.setAttr ('defaultRenderGlobals.imageFormat',32)
		tmpFile = tempfile.gettempdir() + '/playblastTmp/' + movFil.name
		asd = mc.playblast( format = "image", filename = tmpFile, forceOverwrite = True, viewer = 0, showOrnaments = 0, percent = 100, widthHeight = resolution )
		print asd
	finally:
		mm.eval( 'setAllMainWindowComponentsVisible 1;' )
	#ADD FRAME NUMBERS
	print tmpFile + '.png'
	#sqFil.sequenceFile( tmpFile + '.png' ).insertFrameNumber( tempfile.gettempdir() + '/playblastTmp/', 1, movFil.name )
	#EXPORT MOV FILE
	audioPath = ''
	audio =[a for a in  mn.ls( typ = 'audio' ) if a.a.mute.v == 0]
	if audio:
		audioPath = audio[0].a.filename.v
	fps = { 'film':24, 'pal':25 }
	curFps = mc.currentUnit( q = True, time=True)
	sqFile = sqFil.sequenceFile( tmpFile + '.png' )
	sqFile.createMov( movFil.dirPath.replace( '\\', '/').replace('//','/'), audioPath, fps[curFps], movFil.name )
	os.system("start "+ str( movFil.path ) )
	shutil.rmtree( tempfile.gettempdir() + '/playblastTmp/' )


