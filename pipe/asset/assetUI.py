import os
import general.ui.pySideHelper as uiH
reload( uiH )
uiH.set_qt_bindings()
from Qt import QtGui,QtCore
import pipe.project.project   as prj
import pipe.asset.asset as ass
reload( prj )
import pipe.settings.settings as sti
reload( sti )


PYFILEDIR = os.path.dirname( os.path.abspath( __file__ ) )

uifile = PYFILEDIR + '/asset.ui'
fom, base = uiH.loadUiType( uifile )

class AssetCreator(base, fom):
	"""docstring for ProjectCreator"""
	def __init__(self, parent = None):
		if uiH.USEPYQT:
			super(base, self).__init__(parent)
		else:
			super(AssetCreator, self).__init__(parent)
		self.setupUi(self)
		self.connect(self.buttonBox, QtCore.SIGNAL("accepted()"), self.createAsset)
		self.settings = sti.Settings()
		self.loadProjectsPath()
		self.fillProjectsCMB()
		self.asset_le.setFocus()

	def loadProjectsPath(self):
		"""docstring for loadProjectsPath"""
		gen = self.settings.General
		if gen:
			basePath = gen[ "basepath" ]
			if basePath:
				if basePath.endswith( '\\' ):
					basePath = basePath[:-1]
				prj.BASE_PATH = basePath.replace( '\\', '/' )

	def fillProjectsCMB(self):
		"""fill combo box with projects"""
		self.projects_cmb.clear()
		self.projects_cmb.addItems( prj.projects( prj.BASE_PATH ) )
	
	def createAsset(self):
		"""create New Asset Based on new project name"""
		projName =  str( self.projects_cmb.currentText() )
		print projName
		assetName = self.asset_le.text()
		newAsset = ass.Asset( str( assetName ), prj.Project( projName, prj.BASE_PATH ) )
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

