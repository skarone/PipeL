import os
import general.ui.pySideHelper as uiH
reload( uiH )
uiH.set_qt_bindings()
from Qt import QtGui,QtCore

INMAYA = False
try:
	import general.mayaNode.mayaNode as mn
	import maya.cmds as mc
	import rigging.utils.utils as utls
	reload( utls )
	INMAYA = True
except:
	pass

#load UI FILE
PYFILEDIR = os.path.dirname( os.path.abspath( __file__ ) )
uifile = PYFILEDIR + '/transferSkinWeights.ui'
fom, base = uiH.loadUiType( uifile )

class TransferSkinWeightsUi(base,fom):
	"""manager ui class"""
	def __init__(self):
		if INMAYA:
			if uiH.USEPYQT:
				super(base, self).__init__(uiH.getMayaWindow())
			else:
				super(TransferSkinWeightsUi, self).__init__(uiH.getMayaWindow())
		else:
			super(base, self).__init__()
		self.setupUi(self)
		self._makeConnections()
		self.setObjectName( 'TransferSkinWeightsUi' )

	def _makeConnections(self):
		"""docstring for _makeConnections"""
		self.connect( self.insterFromVertex_btn , QtCore.SIGNAL("clicked()") , self.insterFromVertex )
		self.connect( self.insertFromSkin_btn , QtCore.SIGNAL("clicked()") , self.insertFromSkin )
		self.connect( self.toVertex_btn , QtCore.SIGNAL("clicked()") , self.toVertex )
		self.connect( self.insertToSkin_btn , QtCore.SIGNAL("clicked()") , self.insertToSkin )
		self.connect( self.transferWeights_btn , QtCore.SIGNAL("clicked()") , self.transferWeights )
		self.connect( self.quickTransferWeights_btn , QtCore.SIGNAL("clicked()") , self.quickTransferWeights )

	def insterFromVertex(self):
		"""docstring for insterFromVertex"""
		self.fromVertex_le.setText( mc.ls( sl = True, hd = 1 )[0] )

	def insertFromSkin(self):
		"""docstring for insertFromSkin"""
		self.fromSkin_le.setText( utls.getSkinFromGeo( mc.ls( sl = True, hd = 1 )[0] )[0])

	def toVertex(self):
		"""docstring for toVertex"""
		self.toVertex_lw.clear()
		for v in mc.ls( sl = True, fl = True ):
			item = QtGui.QListWidgetItem( v )
			self.toVertex_lw.addItem( item )

	def insertToSkin(self):
		"""docstring for insertToSk"""
		self.toSkin_le.setText( utls.getSkinFromGeo( mc.ls( sl = True, hd = 1 )[0] )[0] )

	def transferWeights(self):
		"""docstring for transferWri"""
		fromVer = str( self.fromVertex_le.text() )
		verts = []
		for v in xrange(self.toVertex_lw.count()):
			verts.append( str( self.toVertex_lw.item(v).text() ))
		fromSkn = str( self.fromSkin_le.text()  )
		toSkn   = str( self.toSkin_le.text() )
		utls.copyVertexWeights( fromVer, fromSkn, verts, toSkn )

	def quickTransferWeights(self):
		"""docstring for quickTran"""
		sel = mc.ls( sl = 1 , fl = 1 )
		skn = utls.getSkinFromGeo( sel[0] )[0]
		skn2 = utls.getSkinFromGeo( sel[1] )[0]
		utls.copyVertexWeights( sel[0], skn, sel[1:], skn2 )

def main():
	if mc.window( 'TransferSkinWeightsUi', q = 1, ex = 1 ):
		mc.deleteUI( 'TransferSkinWeightsUi' )
	PyForm=TransferSkinWeightsUi()
	PyForm.show()


if __name__=="__main__":
	import sys
	a = QtGui.QApplication(sys.argv)
	global PyForm
	a.setStyle('plastique')
	PyForm=TransferSkinWeightsUi()
	PyForm.show()
	sys.exit(a.exec_())

