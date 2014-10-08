import maya.mel as mm
import maya.cmds as mc
import general.mayaNode.mayaNode as mn
import pipe.file.file as fl
import pipe.mayaFile.mayaFile as mfl

def playblastCurrentFile():
	"""playblast current File"""
	fil = mfl.currentFile()
	movfil = fil.path.replace( fil.extension, '.mov' )
	playblast( movfil )

def playblast( path ):
	"""main playblast function
	param path: string for the path for the playblast"""
	mm.eval( 'setAllMainWindowComponentsVisible 0;' )
	try:
		resNode = mn.Node( 'defaultResolution' )
		fil = fl.File( path )
		if fil.exists:
			fil.newVersion()
		resolution = [ resNode.a.width.v, resNode.a.height.v ]
		print path
		#playblast  -format qt -filename "P:/Wrigleys_Test/Maya/Sequences/Test/Shots/s001_T01/Anim/s001_T01_ANIM.mov" -sequenceTime 0 -clearCache 1 -viewer 1 -showOrnaments 1 -fp 4 -percent 50 -compression "PNG" -quality 70;
		asd = mc.playblast( format = "qt", filename = path, forceOverwrite = True, sequenceTime = 0, clearCache = 1, viewer = 1, showOrnaments = 0, fp = 4, percent = 75, compression = "PNG", quality = 70, widthHeight = resolution )
		print asd
	finally:
		mm.eval( 'setAllMainWindowComponentsVisible 1;' )
<<<<<<< .merge_file_a04576

=======
>>>>>>> .merge_file_a06424
