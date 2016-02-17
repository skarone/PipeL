import os
import general.ui.pySideHelper as uiH
reload( uiH )

from Qt import QtGui,QtCore
import maya.cmds as mc
import general.mayaNode.mayaNode as mn
import maya.mel as mm

import rigging.curveBased.curveBased as crvBased
reload( crvBased )

"""
import general.multiAttribute.multiAttributeUi as maUI
reload( maUI )
maUI.main()
"""

PYFILEDIR = os.path.dirname( os.path.abspath( __file__ ) )

uifile = PYFILEDIR + '/curveBased.ui'
fom, base = uiH.loadUiType( uifile )


class CurveBasedUI(base, fom):
	"""docstring for ProjectCreator"""
	def __init__(self, parent  = uiH.getMayaWindow(), *args ):
		if uiH.USEPYQT:
			super(base, self).__init__(parent)
		else:
			super(CurveBasedUI, self).__init__(parent)
		self.setupUi(self)
		self.connect(self.sysIn_btn, QtCore.SIGNAL("clicked()"), self.fillSystemLE)
		self.connect(self.curveIn_btn, QtCore.SIGNAL("clicked()"), self.fillCurveLE)
		self.connect(self.meshIn_btn, QtCore.SIGNAL("clicked()"), self.fillMeshLE)
		self.connect(self.skinIn_btn, QtCore.SIGNAL("clicked()"), self.fillSkinLE)
		self.connect(self.createSofts_btn, QtCore.SIGNAL("clicked()"), self.createSofts)
		self.connect(self.softToJoint_btn, QtCore.SIGNAL("clicked()"), self.createJointsOnSofts)
		self.connect(self.deleteSoft_btn, QtCore.SIGNAL("clicked()"), self.deleteSofts)
		self.connect(self.transWOnSel_btn, QtCore.SIGNAL("clicked()"), self.transferWeightToSel)
		self.setObjectName( 'cuveBasedRig_WIN' )
		uiH.loadSkin( self, 'QTDarkGreen' )

	def fillSystemLE(self):
		"""fill the system line edit"""
		sel = mn.ls( sl = True )
		if sel:
			self.systemName_le.setText( sel[0].namespace.name[1:] )

	def fillCurveLE(self):
		"""fill line edit with curve name"""
		sel = mn.ls( sl = True, dag = True, ni = True, typ = 'nurbsCurve' )
		self.curve_le.setText( sel[0].name )
	
	def fillMeshLE(self):
		"""fill line edit with mesh name"""
		sel = mn.ls( sl = True, dag = True, ni = True, typ = 'mesh' )
		self.mesh_le.setText( sel[0].name )

	def fillSkinLE(self):
		"""fill line edit with skincluster name"""
		sel = mn.ls( sl = True )
		skin = mm.eval( 'findRelatedSkinCluster ' + sel[0].name )
		self.skin_le.setText( skin )

	def createSofts(self):
		"""docstring for fname"""
		sysName = str( self.systemName_le.text() )
		if sysName == "":
			print "PLEASE SPECIFY A SYSTEM NAME"
			return
		curv = str( self.curve_le.text() )
		mesh = str( self.mesh_le.text() )
		softsCount = self.controlCount_sbx.value()
		useTip = self.useTips_chb.isChecked()
		crvBased.createSofts( sysName, curv, mesh, softsCount, useTip )

	def createJointsOnSofts(self):
		"""create joints from the softMods of the system"""
		sysName = str( self.systemName_le.text() )
		if sysName == "":
			print "PLEASE SPECIFY A SYSTEM NAME"
			return
		mesh = str( self.mesh_le.text() )
		skin = str( self.skin_le.text() )
		if skin == '': #THERE IS NO SKIN... CREATE ONE WITH A BASE JOINT
			mc.select(d=True)
			mc.joint(p=(0,0,0), n = sysName + ':softModBase_jnt')
			skin = mc.skinCluster( sysName + ':softModBase_jnt', mesh, dr=4.5,normalizeWeights = 2)[0]
		crvBased.createJointsOnSofts( sysName, mesh, skin )


	def deleteSofts(self):
		"""docstring for fname"""
		pass

	def transferWeightToSel(self):
		"""transfer weight of selected softmod to their skin joint"""
		skin = str( self.skin_le.text() )
		mesh = str( self.mesh_le.text() )
		crvBased.transferWeightToSel( skin, mesh )


class Window(QtGui.QMainWindow):
	def __init__(self):
		QtGui.QMainWindow.__init__(self)
		dia = CurveBasedUI()
		dia.exec_()
	
def main():
	"""use this to create project in maya"""
	if mc.window( 'cuveBasedRig_WIN', q = 1, ex = 1 ):
		mc.deleteUI( 'cuveBasedRig_WIN' )
	PyForm=CurveBasedUI()
	PyForm.show()


if __name__=="__main__":
	import sys
	a = QtGui.QApplication(sys.argv)
	global PyForm
	a.setStyle('plastique')
	PyForm=Window()
	PyForm.show()
	sys.exit(a.exec_())

