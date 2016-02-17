import os
import general.ui.pySideHelper as uiH
reload( uiH )

from Qt import QtGui,QtCore


import pipe.project.project   as prj
import pipe.sequence.sequence as seq
reload( prj )
import pipe.settings.settings as sti
reload( sti )


PYFILEDIR = os.path.dirname( os.path.abspath( __file__ ) )

uifile = PYFILEDIR + '/sequence.ui'
fom, base = uiH.loadUiType( uifile )

class SequenceCreator(base, fom):
	"""docstring for ProjectCreator"""
	def __init__(self, parent = None):
		if uiH.USEPYQT:
			super(base, self).__init__(parent)
		else:
			super(SequenceCreator, self).__init__(parent)
		self.setupUi(self)
		self.connect(self.buttonBox, QtCore.SIGNAL("accepted()"), self.createSequence)
		self.settings = sti.Settings()
		self.loadProjectsPath()
		self.fillProjectsCMB()
		self.sequence_le.setFocus()

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
	
	def createSequence(self):
		"""create New Asset Based on new project name"""
		projName =  str( self.projects_cmb.currentText() )
		assetName = self.sequence_le.text()
		newAsset = seq.Sequence( str( assetName ), prj.Project( projName, prj.BASE_PATH ) )
		if not newAsset.exists:
			newAsset.create()
			print 'New Asset Created : ', newAsset.name, ' for ',  projName
			QtGui.QDialog.accept(self)
		else:
			QtGui.QDialog.reject(self)

class Window(QtGui.QMainWindow):
	def __init__(self):
		QtGui.QMainWindow.__init__(self)
		dia = SequenceCreator()
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

