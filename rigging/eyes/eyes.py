import os

import general.ui.pySideHelper as uiH
reload( uiH )

from Qt import QtGui,QtCore

#load UI FILE
PYFILEDIR = os.path.dirname( os.path.abspath( __file__ ) )

uifile = PYFILEDIR + '/eyes.ui'
fom, base = uiH.loadUiType( uifile )

import maya.cmds as mc
import general.mayaNode.mayaNode as mn
reload( mn )
import modeling.curve.curve as crv

class EyesUI(base,fom):
	"""manager ui class"""
	def __init__(self, parent  = uiH.getMayaWindow(), *args):
		if uiH.USEPYQT:
			super(base, self).__init__(parent)
		else:
			super(EyesUI, self).__init__(parent)
			self.setupUi(self)
			self.setObjectName( 'EyesUI' )
		self.makeConnections()

	def makeConnections(self):
		"""docstring for makeConnections"""
		self.connect(self.create_btn, QtCore.SIGNAL("clicked()"), self.create)
		self.connect(self.leftEyesGeo_btn, QtCore.SIGNAL("clicked()"), self.leftEyesGeo)
		self.connect(self.rightEyesGeo_btn, QtCore.SIGNAL("clicked()"), self.rightEyesGeo)

	def leftEyesGeo(self):
		"""docstring for leftEyesGeo"""
		geo = ",".join([a.name for a in mn.ls( sl = True )])
		self.leftEyesGeo_le.setText( geo )

	def rightEyesGeo(self):
		"""docstring for rightEyesGeo"""
		geo = ",".join([a.name for a in mn.ls( sl = True )])
		self.rightEyesGeo_le.setText( geo )

	def eyesBasePosControl(self):
		"""docstring for eyesBasePosControl"""
		geo = mn.ls( sl = True )[0].name
		self.eyesBasePosControl_le.setText( geo )

	def _textToNodes(self, le):
		"""docstring for _textToNodes"""
		nods = mn.Nodes(le.text().split(','))
		return nods

	def create(self):
		"""docstring for create"""
		leftEyes = self._textToNodes( self.leftEyesGeo_le )
		leftTrf, leftCtl = self._createPerEye( 'l', leftEyes )
		rightEyes = self._textToNodes( self.rightEyesGeo_le )
		rightTrf, rightCtl = self._createPerEye( 'r', rightEyes )
		trf = mn.createNode( 'transform' )
		trf.name = 'Eyes_Def_grp'
		leftTrf.parent = trf
		rightTrf.parent  = trf
		ctl = crv.Curve( 'eyes_ctl' )
		ctl.create( 'square' )
		par = mn.Node( mc.parentConstraint( leftCtl, rightCtl,ctl, mo = False )[0])
		par.delete()
		ctl.a.rx.v = 90
		mc.makeIdentity( ctl, a = True, t = 1, r = 1, s = 1 )
		leftCtl.parent = ctl
		rightCtl.parent = ctl

	def _createPerEye(self, side, geos ):
		mc.select( geos )
		clu = mn.Node( mc.cluster( n = side + '_Eye_CLU' )[1] )
		print clu.name
		mc.select( geos )
		lat = mn.Nodes( mc.lattice( n = side + '_Eye_LAT', objectCentered = True ) )
		ctl = crv.Curve( side + '_Eye_ctl' )
		ctl.create( 'circleZ' )
		print ctl.name
		par = mn.Node( mc.parentConstraint( clu, ctl, mo = False )[0])
		par.delete()
		ctl.a.tz.v = self.distance_control_sb.value() + ctl.a.tz.v
		mc.makeIdentity( ctl, a = True, t = 1, r = 1, s = 1 )
		loc = mn.createNode( 'locator' ).parent
		loc.name = side + '_Eye_Top_Loc'
		par = mn.Node( mc.aimConstraint( ctl, clu, mo = True, aimVector=[1,0,0],
										upVector=[0,1,0], worldUpType='object',
										worldUpObject=loc )[0])
		trf = mn.createNode( 'transform' )
		trf.name = side + '_Eye_Def_grp'
		lat[1].parent = trf
		lat[2].parent = trf
		clu.parent = trf
		loc.parent = trf
		return trf, ctl



def main():
	"""use this to create project in maya"""
	if mc.window( 'EyesUI', q = 1, ex = 1 ):
		mc.deleteUI( 'EyesUI' )
	PyForm=EyesUI()
	PyForm.show()







