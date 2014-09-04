import os
import general.ui.pySideHelper as uiH
reload( uiH )
uiH.set_qt_bindings()
from Qt import QtGui,QtCore

import pipe.project.project   as prj
reload( prj )
import pipe.settings.settings as sti
reload( sti )

PYFILEDIR = os.path.dirname( os.path.abspath( __file__ ) )

uifile = PYFILEDIR + '/project.ui'
fom, base = uiH.loadUiType( uifile )

class ProjectCreator(base, fom):
	"""docstring for ProjectCreator"""
	def __init__(self):
		if uiH.USEPYQT:
			super(base, self).__init__()
		else:
			super(ProjectCreator, self).__init__()
		self.setupUi(self)
		self.connect(self.buttonBox, QtCore.SIGNAL("accepted()"), self.createProject)
		self.settings = sti.Settings()
		self.loadProjectsPath()
		uiH.loadSkin( self, 'QTDarkGreen' )

	def loadProjectsPath(self):
		"""docstring for loadProjectsPath"""
		gen = self.settings.General
		if gen:
			basePath = gen[ "basepath" ]
			if basePath:
				if basePath.endswith( '\\' ):
					basePath = basePath[:-1]
				prj.BASE_PATH = basePath.replace( '\\', '/' )
	
	def createProject(self):
		"""create New Project Based on new project name"""
		projName = self.project_le.text()
		newProject = prj.Project( str( projName ), prj.BASE_PATH )
		if not newProject.exists:
			newProject.create()
			print 'New Project Created : ', newProject.name
			QtGui.QDialog.accept(self)
		else:
			QtGui.QDialog.reject(self)


class Window(QtGui.QMainWindow):
	def __init__(self):
		QtGui.QMainWindow.__init__(self)
		dia = ProjectCreator()
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

