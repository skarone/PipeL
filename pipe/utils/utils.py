'''
File: utils.py
Author: Ignacio Urruty
Description: General Utitlities for pipeline
'''
import shading.textureManager.textureManager as tm
reload(tm)
import pipe.settings.settings as sti
reload( sti )

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


