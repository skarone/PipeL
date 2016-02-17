import os
import general.ui.pySideHelper as uiH
reload( uiH )

from Qt import QtGui,QtCore

import maya.cmds as mc
import general.mayaNode.mayaNode as mn
import maya.mel as mm

import general.curveScatter.curveScatter as crvScat
reload( crvScat )
import modeling.curve.curve as crv

"""
import general.curveScatter.curveScatterUi as crvScatterUi
reload( crvScatterUi )
crvScatterUi.main()
"""

PYFILEDIR = os.path.dirname( os.path.abspath( __file__ ) )

uifile = PYFILEDIR + '/curveScatter.ui'
fom, base = uiH.loadUiType( uifile )

class CurveScatterUI(base, fom):
	"""docstring for ProjectCreator"""
	def __init__(self, parent  = uiH.getMayaWindow(), *args ):
		if uiH.USEPYQT:
			super(base, self).__init__(parent)
		else:
			super(CurveScatterUI, self).__init__(parent)
		self.setupUi(self)
		self.connect(self.curveIn_btn, QtCore.SIGNAL("clicked()"), self.fillCurveLE)
		self.connect(self.addObject_btn, QtCore.SIGNAL("clicked()"), self.addObject)
		self.connect(self.removeObject_btn, QtCore.SIGNAL("clicked()"), self.removeObject)
		self.connect(self.cleanList_btn, QtCore.SIGNAL("clicked()"), self.cleanList)
		self.connect(self.createScatter_btn, QtCore.SIGNAL("clicked()"), self.createScatter)
		self.setObjectName( 'curveScatter_WIN' )
		uiH.loadSkin( self, 'QTDarkGreen' )

	def fillCurveLE(self):
		"""fill line edit with curve name"""
		sel = mn.ls( sl = True, dag = True, ni = True, typ = 'nurbsCurve' )
		self.curve_le.setText( sel[0].name )
	
	def addObject(self):
		"""add selected transforms to list"""
		sel = mc.ls( sl = True, typ = 'transform' )
		if sel:
			self.objects_lw.addItems( sel )

	def removeObject(self):
		"""remove selected object from list"""
		for SelectedItem in self.objects_lw.selectedItems():
			self.objects_lw.takeItem(self.objects_lw.row(SelectedItem) )

	def cleanList(self):
		"""docstring for fname"""
		self.objects_lw.clean()

	def createScatter(self):
		"""create scatter based on UI"""
		curv = str( self.curve_le.text() )
		objCount = self.controlCount_sbx.value()
		random = self.random_chb.isChecked()
		useTip = self.useTips_chb.isChecked()
		keepConn = self.keepConnected_chb.isChecked()
		tangent = self.tangent_chb.isChecked()
		groupIt = self.groupIt_chb.isChecked()
		animated = self.animated_chb.isChecked()
		objs = []
		for index in xrange(self.objects_lw.count()):
			objs.append( mn.Node( str ( self.objects_lw.item(index).text() ) ) )
		crvScat.CurveScatter( 
				curve = crv.Curve( curv ), 
				objects = objs,
				pointsCount = objCount, 
				useTips = useTip, 
				keepConnected = keepConn,
				tangent = tangent,
				rand = random,
				groupit = groupIt,
				animated = animated)
		

class Window(QtGui.QMainWindow):
	def __init__(self):
		QtGui.QMainWindow.__init__(self)
		dia = CurveScatterUI()
		dia.exec_()
	
def main():
	"""use this to create project in maya"""
	if mc.window( 'curveScatter_WIN', q = 1, ex = 1 ):
		mc.deleteUI( 'curveScatter_WIN' )
	PyForm=CurveScatterUI()
	PyForm.show()


if __name__=="__main__":
	import sys
	a = QtGui.QApplication(sys.argv)
	global PyForm
	a.setStyle('plastique')
	PyForm=Window()
	PyForm.show()
	sys.exit(a.exec_())



