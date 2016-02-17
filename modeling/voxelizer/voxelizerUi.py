import os
import general.ui.pySideHelper as uiH

from Qt import QtGui,QtCore
PYFILEDIR = os.path.dirname( os.path.abspath(__file__) )
uifile = PYFILEDIR + '/voxelizer.ui'
fom, base = uiH.loadUiType( uifile )
try:
	import maya.cmds as mc
	INMAYA = True
except:
	pass
	INMAYA = False

import modeling.voxelizer.voxelizer as vxe
reload( vxe )

class VoxelizerUI(base,fom):
	"""docstring for VoxelizerUI"""
	def __init__(self, parent = None ):
		if INMAYA:
			super(VoxelizerUI, self).__init__(uiH.getMayaWindow())
		else:
			super(VoxelizerUI, self).__init__(parent)
		self.setupUi(self)
		self.setObjectName( 'VoxelizerUI' )
		self.makeConnections()

	def makeConnections(self):
		"""docstring for fname"""
		QtCore.QObject.connect( self.create_btn, QtCore.SIGNAL( "clicked()" ),
								self.create )

	def create(self):
		"""docstring for fname"""
		startFrame = self.startFrame_spb.value()
		endFrame = self.endFrame_spb.value()
		voxelSize = self.voxelSize_spb.value()
		voxelStep = self.boxSize_spb.value()
		vxe.createVoxelForSelection( startFrame, endFrame, voxelSize, voxelStep )

def main():
	"""call this from inside maya"""
	if mc.window( 'VoxelizerUI', q = 1, ex = 1 ):
		mc.deleteUI( 'VoxelizerUI' )
	expor = VoxelizerUI()
	expor.show()

