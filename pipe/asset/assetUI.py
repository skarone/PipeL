import os
from PyQt4 import QtGui,QtCore, uic
import pipe.project.project   as prj
import pipe.asset.asset as ass
reload( prj )

PYFILEDIR = os.path.dirname( os.path.abspath( __file__ ) )

uifile = PYFILEDIR + '/asset.ui'
fom, base = uic.loadUiType( uifile )

class AssetCreator(base, fom):
	"""docstring for ProjectCreator"""
	def __init__(self):
		super(base, self).__init__()
		self.setupUi(self)
		self.connect(self.buttonBox, QtCore.SIGNAL("accepted()"), self.createAsset)
		self.fillProjectsCMB()
		self.asset_le.setFocus()

	def fillProjectsCMB(self):
		"""fill combo box with projects"""
		self.projects_cmb.clear()
		self.projects_cmb.addItems( prj.projects() )
	
	def createAsset(self):
		"""create New Asset Based on new project name"""
		projName =  str( self.projects_cmb.currentText() )
		print projName
		assetName = self.asset_le.text()
		newAsset = ass.Asset( str( assetName ), prj.Project( projName ) )
		print newAsset.name
		if not newAsset.exists:
			newAsset.create()
			print 'New Asset Created : ', newAsset.name, ' for ',  projName
			QtGui.QDialog.accept(self)
		else:
			QtGui.QDialog.reject(self)

class Window(QtGui.QMainWindow):
	def __init__(self):
		QtGui.QMainWindow.__init__(self)
		dia = AssetCreator()
		dia.exec_()
	
def main():
	"""use this to create project in maya"""
	pass


if __name__=="__main__":
	import sys
	a = QtGui.QApplication(sys.argv)
	global PyForm
	a.setStyle('plastique')
	PyForm=Window()
	PyForm.show()
	sys.exit(a.exec_())

