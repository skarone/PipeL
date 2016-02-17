import pipe.mayaFile.mayaFile as mfl
import os
import maya.cmds as mc
import general.mayaNode.mayaNode as mn
import pipe.project.project as prj
import pipe.asset.asset as ass

import general.ui.pySideHelper as uiH
reload( uiH )

from Qt import QtGui,QtCore

PYFILEDIR = os.path.dirname( os.path.abspath( __file__ ) )

def loadUnloadLightRig( path = '' ):
	"""docstring for loadUnloadLightRig"""
	if path == '':
		fil = mfl.mayaFile( PYFILEDIR + '/LightRig.ma'  )
	else:
		fil = mfl.mayaFile( path )
	if mc.objExists( 'LightRig:LR' ):
		refNode = mc.referenceQuery( fil.path, rfn = True )
		mc.file( referenceNode  = refNode, removeReference = True  )
	else:
		mc.file( fil.path, r = True, type = "mayaAscii", gl = True, loadReferenceDepth = "all",rnn = True, namespace = 'LightRig', options = "v=0;" )

#load UI FILE
uifile = PYFILEDIR + '/LightRigUi.ui'
fom, base = uiH.loadUiType( uifile )

class LightRigUi(base,fom):
	def __init__(self, parent  = uiH.getMayaWindow(), *args ):
		if uiH.USEPYQT:
			super(base, self).__init__(parent)
		else:
			super(LightRigUi, self).__init__(parent)
		self.setupUi(self)
		self.connect( self.default_btn, QtCore.SIGNAL("clicked()") , self.default )
		self.connect( self.project_btn, QtCore.SIGNAL("clicked()") , self.project )
		self.setObjectName( 'LightRigUi' )
		

	def default(self):
		"""load default light rig"""
		loadUnloadLightRig()

	def project(self):
		"""load project light Rig"""
		asset = prj.shotOrAssetFromFile( mfl.currentFile() )
		litRig  = ass.Asset( 'LightRig', asset.project )
		if litRig.exists:
			loadUnloadLightRig( litRig.shadingPath.path )

def main():
	"""docstring for main"""
	if mc.window( 'LightRigUi', q = 1, ex = 1 ):
		mc.deleteUI( 'LightRigUi' )
	PyForm=LightRigUi()
	PyForm.show()
