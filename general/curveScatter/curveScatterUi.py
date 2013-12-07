import os
from PyQt4 import QtGui,QtCore, uic
import maya.cmds as mc
import general.mayaNode.mayaNode as mn
import maya.OpenMayaUI as mui
import sip
import maya.mel as mm

import general.curveScatter.curveScatter as crvScat
import modeling.curve.curve as crv

"""
import general.curveScatter.curveScatterUi as crvScatterUi
reload( crvScatterUi )
crvScatterUi.main()
"""

PYFILEDIR = os.path.dirname( os.path.abspath( __file__ ) )

uifile = PYFILEDIR + '/curveScatter.ui'
fom, base = uic.loadUiType( uifile )

def get_maya_main_window( ):
	ptr = mui.MQtUtil.mainWindow( )
	main_win = sip.wrapinstance( long( ptr ), QtCore.QObject )
	return main_win

class CurveScatterUI(base, fom):
	"""docstring for ProjectCreator"""
	def __init__(self, parent  = get_maya_main_window(), *args ):
		super(base, self).__init__(parent)
		self.setupUi(self)
		self.connect(self.curveIn_btn, QtCore.SIGNAL("clicked()"), self.fillCurveLE)
		self.connect(self.addObject_btn, QtCore.SIGNAL("clicked()"), self.addObject)
		self.connect(self.removeObject_btn, QtCore.SIGNAL("clicked()"), self.removeObject)
		self.connect(self.cleanList_btn, QtCore.SIGNAL("clicked()"), self.cleanList)
		self.setObjectName( 'curveScatter_WIN' )

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
		for SelectedItem in self.objects_lw.ContentList.selectedItems():
			self.objects_lw.ContentList.takeItem(self.objects_lw.ContentList.row(SelectedItem)

	def cleanList(self):
		"""docstring for fname"""
		pass
		

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

