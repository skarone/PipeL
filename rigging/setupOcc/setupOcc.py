import os

import general.ui.pySideHelper as uiH
reload( uiH )
uiH.set_qt_bindings()
from Qt import QtGui,QtCore

#load UI FILE
PYFILEDIR = os.path.dirname( os.path.abspath( __file__ ) )

uifile = PYFILEDIR + '/setupOcc.ui'
fom, base = uiH.loadUiType( uifile )

import general.mayaNode.mayaNode as mn
import maya.cmds as mc


class SetupOccUI(base,fom):
	"""manager ui class"""
	def __init__(self, parent  = uiH.getMayaWindow(), *args):
		if uiH.USEPYQT:
			super(base, self).__init__(parent)
		else:
			super(SetupOccUI, self).__init__(parent)
		self.setupUi(self)
		self.setObjectName( 'SetupOccUI' )
		self.makeConnections()

	def makeConnections(self):
		"""create connections for ui controls"""
		self.connect(self.addTextureToOcc_btn, QtCore.SIGNAL("clicked()"), self.addTextureToOcc)
		self.connect(self.removeTextureToOcc_btn, QtCore.SIGNAL("clicked()"), self.removeTextureToOcc)
		self.connect(self.addIrisToOcc_btn, QtCore.SIGNAL("clicked()"), self.addIrisToOcc)
		self.connect(self.removeIrisToOcc_btn, QtCore.SIGNAL("clicked()"), self.removeIrisToOcc)

	def _getShapes(self):
		"""docstring for _getShapes"""
		shas = []
		for n in mn.ls( sl = True ):
			if not n.shape and not n.type == 'mesh':
				print n.name
				continue
			if n.type == 'mesh': #selecting a mesh
				shas.append( n )
			else:
				shas.append( n.shape )
		return shas

	def addTextureToOcc(self):
		"""add texture attribute for occ render"""
		shas = self._getShapes()
		fname, _ = QtGui.QFileDialog.getOpenFileName(self, 'Open file ',
													'/home')
		if fname:
			for sha in shas:
				#get texture Path
				if not sha.a.texture_Occ.exists:
					occText = sha.a.texture_Occ.add( dt='string' )
				sha.a.texture_Occ.v = fname

	def removeTextureToOcc(self):
		"""remove attribute for occ render"""
		shas = self._getShapes()
		for sha in shas:
			if sha.a.texture_Occ.exists:
				sha.a.texture_Occ.delete()

	def addIrisToOcc(self):
		"""add Iris to occ"""
		shas = self._getShapes()
		for sha in shas:
			if not sha.a.iris_Occ.exists:
				occText = sha.a.iris_Occ.add( at='bool' )
			sha.a.iris_Occ.v = True

	def removeIrisToOcc(self):
		"""remove Iris to occ"""
		shas = self._getShapes()
		for sha in shas:
			if sha.a.iris_Occ.exists:
				sha.a.iris_Occ.delete()

def main():
	"""use this to create project in maya"""
	if mc.window( 'SetupOccUI', q = 1, ex = 1 ):
		mc.deleteUI( 'SetupOccUI' )
	PyForm=SetupOccUI()
	PyForm.show()
