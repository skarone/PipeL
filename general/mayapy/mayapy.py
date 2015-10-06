import sys
import os
import maya.standalone as std
std.initialize(name='python')
import maya.cmds as mc

def runScripts(mayaFile, scripts, save = False):
	"""docstring for runScripts"""
	maya.standalone.initialize(name='python')
	mc.file(mayaFile, force=True, open=True )
	scripts = scripts.split( ',' )
	for s in scripts:
		sys.path.append( os.path.dirname( s ) )
		cmd = "import "+os.path.filename( s )
		eval( cmd )
	if save:
		mc.file(save=True, force=True)

mayaFile = sys.argv[1]
scripts  = sys.argv[2]
save     = sys.argv[3]
runScripts(mayaFile, scripts, save )
