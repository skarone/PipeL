import os
from PyQt4 import QtGui,QtCore, uic
import maya.cmds as mc
import general.mayaNode.mayaNode as mn
import maya.OpenMayaUI as mui
import sip
import maya.mel as mm

import general.curveScatter.curveScatter as crvScat
reload( crvScat )
import modeling.curve.curve as crv
reload( crv )
import rigging.utils.SoftModCluster.SoftModCluster as sf
reload( sf )
import rigging.stickyControl.stickyControl as stk
reload( stk )

"""
import general.multiAttribute.multiAttributeUi as maUI
reload( maUI )
maUI.main()
"""

PYFILEDIR = os.path.dirname( os.path.abspath( __file__ ) )

uifile = PYFILEDIR + '/curveBased.ui'
fom, base = uic.loadUiType( uifile )

def get_maya_main_window( ):
	ptr = mui.MQtUtil.mainWindow( )
	main_win = sip.wrapinstance( long( ptr ), QtCore.QObject )
	return main_win


class CurveBasedUI(base, fom):
	"""docstring for ProjectCreator"""
	def __init__(self, parent  = get_maya_main_window(), *args ):
		super(base, self).__init__(parent)
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
		space = mn.Namespace( sysName )
		space.create()
		with space.set():
			grp = mn.Node( mc.group( n = sysName + '_grp', em = True ) )
			grp.a.crvSystem.add( at = "bool" )
			obj = crv.Curve( sysName + '_CRV' )
			obj = obj.create( "sphere" )
			scat = crvScat.CurveScatter( 
					curve = crv.Curve( curv ), 
					objects = [obj],
					pointsCount = softsCount, 
					useTips = useTip, 
					keepConnected = True,
					tangent = 1,
					rand = 0 )
			for i,n in enumerate( scat._nodes ):
				softMod = sf.SoftModCluster( sysName + '_%i'%i + '_SFM', mesh )
				handle = softMod.create( n.a.t.v[0] )
				handle.parent = grp
		scat.delete()
		obj.delete()

	def createJointsOnSofts(self):
		"""create joints from the softMods of the system"""
		sysName = str( self.systemName_le.text() )
		if sysName == "":
			print "PLEASE SPECIFY A SYSTEM NAME"
			return
		mesh = str( self.mesh_le.text() )
		space = mn.Namespace( sysName )
		skin = str( self.skin_le.text() )
		with space.set():
			for i,s in enumerate( mn.ls( sysName + ':*', typ = 'softModHandle' ) ):
				trans = s.parent
				control = stk.ControlOnMesh( name = sysName + '%i'%i, baseJoint = '', position = trans.worldPosition, mesh = mesh )
				control.create()
				mc.select( mesh, control.skinJoint.name )
				mc.skinCluster( skin, e = True, dr = 4, lw = True, wt=0, ai = control.skinJoint.name )
				control.skinJoint.a.lockInfluenceWeights.v = 0
				s.a.joint.add( at = "message" )
				control.skinJoint.a.soft.add( at = "message" )
				s.a.joint >> control.skinJoint.a.soft
				sf.copyWeightsToJoint( s.name, skin, control.skinJoint.name, mesh )


	def deleteSofts(self):
		"""docstring for fname"""
		pass

	def transferWeightToSel(self):
		"""transfer weight of selected softmod to their skin joint"""
		softMo = mn.ls( sl = True, dag = True, typ = 'softModHandle' )
		if softMo:
			skin = str( self.skin_le.text() )
			mesh = str( self.mesh_le.text() )
			for s in softMo:
				sf.copyWeightsToJoint( s.name, skin, s.a.joint.output[0].node.name, mesh )


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

