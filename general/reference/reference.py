import maya.cmds as mc
import general.mayaNode.mayaNode as mn

"""
import general.reference.reference as rf

rf.reloadSelected()
"""

def reloadSelected():
	"""reload selected object"""
	#reload reference
	obj = mn.ls( sl = True )[0]
	referenceNode = mc.referenceQuery( obj.name, rfn = True )
	path = mc.referenceQuery( obj.name, f = True )
	mc.file( path, loadReference = referenceNode )

def unloadSelected():
	"""unload selected reference"""
	obj = mn.ls( sl = True )[0]
	referenceNode = mc.referenceQuery( obj.name, rfn = True )
	path = mc.referenceQuery( obj.name, f = True )
	mc.file( path, ur = referenceNode )

def loaded():
	"""return al the references that are loaded to the scene"""
	loaded = []
	numLoaded = 0
	refs = mc.file( q = True, r = True )
	for r in refs:
		if not mc.file( r, q = True, dr = True ):
			loaded.append( r )
	return loaded

def unload():
	"""unload reference node"""
	pass
