'''
File: utils.py
Author: Ignacio Urruty
Description: General Utitlities for pipeline
'''
import shading.textureManager.textureManager as tm
reload(tm)
import pipe.settings.settings as sti
reload( sti )
import maya.cmds as mc
import general.mayaNode.mayaNode as mn
import pipe.project.project as prj
import pipe.mayaFile.mayaFile as mfl

def isAllInLocal():
	"""check if all paths in file are in local"""
	settings = sti.Settings()
	gen = settings.General
	if gen:
		basePath = gen[ "basepath" ]
		if basePath:
			if basePath.endswith( '\\' ):
				basePath = basePath[:-1]
			basePath = basePath.replace( '\\', '/' )
	texts = tm.Manager.textures

def isAllInServer():
	"""check if all paths in file are in server"""
	settings = sti.Settings()
	gen = settings.General
	if gen:
		serverPath = gen[ "serverpath" ]

def setAllToServer():
	"""set all paths in scene to server"""
	pass

def setAllToLocal():
	"""set all paths in scene to local"""
	pass


def makeAssetForShot():
	"""make selected asset for this shot, move to assets shot folder and change path to new location"""
	curFile = prj.shotOrAssetFromFile(mfl.currentFile())
	if curFile.type == 'shot':
		allreadyDup = []
		for obj in mn.ls( sl = True ):
			referenceNode = mc.referenceQuery( obj.name, rfn = True )
			refFile = mfl.mayaFile( mc.referenceQuery( obj.name, f = True ) )
			print refFile
			asst = prj.shotOrAssetFromFile( refFile )
			if asst.type == 'asset':
				newFile = mfl.mayaFile( curFile.assetsPath + refFile.path.split( 'Assets' )[-1] )
				newFile.newVersion()
				newFile = refFile.copy( curFile.assetsPath + refFile.path.split( 'Assets' )[-1] )
				mc.file( newFile.path, loadReference = referenceNode )
