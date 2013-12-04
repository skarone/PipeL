import os
from PyQt4 import QtGui,QtCore, uic
import pipe.project.project   as prj
reload( prj )

PYFILEDIR = os.path.dirname( os.path.abspath( __file__ ) )

uifile = PYFILEDIR + '/project.ui'
fom, base = uic.loadUiType( uifile )

class ProjectCreator(base, fom):
	"""docstring for ProjectCreator"""
	def __init__(self):
		super(base, self).__init__()
		self.setupUi(self)
		self.connect(self.buttonBox, QtCore.SIGNAL("accepted()"), self.createProject)
	
	def createProject(self):
		"""create New Project Based on new project name"""
		projName = self.project_le.text()
		newProject = prj.Project( str( projName ) )
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

