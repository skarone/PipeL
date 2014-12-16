import pipe.mayaFile.mayaFile as mfl
import os
import maya.cmds as mc
import general.mayaNode.mayaNode as mn

def loadUnloadLightRig():
	"""docstring for loadUnloadLightRig"""
	PYFILEDIR = os.path.dirname( os.path.abspath( __file__ ) )
	fil = mfl.mayaFile( PYFILEDIR + '/LightRig.ma'  )
	if mc.objExists( 'LightRig:LR' ):
		refNode = mc.referenceQuery( fil.path, rfn = True )
		mc.file( referenceNode  = refNode, removeReference = True  )
	else:
		mc.file( fil.path, r = True, type = "mayaAscii", gl = True, loadReferenceDepth = "all",rnn = True, namespace = fil.name, options = "v=0;" )
