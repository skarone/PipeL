import os
import general.ui.pySideHelper as uiH
reload( uiH )

from Qt import QtGui,QtCore
import pipe.project.project   as prj
import pipe.sets.sets as st
reload( prj )

PYFILEDIR = os.path.dirname( os.path.abspath( __file__ ) )

uifile = PYFILEDIR + '/sets.ui'
fom, base = uiH.loadUiType( uifile )

class SetCreator(base, fom):
	"""docstring for ProjectCreator"""
	def __init__(self,parent = None):
		if uiH.USEPYQT:
			super(base, self).__init__(parent)
		else:
			super(SetCreator, self).__init__(parent)

		self.setupUi(self)
		self.connect(self.buttonBox, QtCore.SIGNAL("accepted()"), self.createSet)
		self.fillProjectsCMB()
		self.set_le.setFocus()

	def fillProjectsCMB(self):
		"""fill combo box with projects"""
		self.projects_cmb.clear()
		self.projects_cmb.addItems( prj.projects() )
	
	def createSet(self):
		"""create New Asset Based on new project name"""
		projName = str( self.projects_cmb.currentText())
		setName = self.set_le.text()
		newSet = st.Set( str( setName ), prj.Project(  projName ) )

		if not newSet.exists:
			newSet.create()
			print 'New Asset Created : ', newSet.name, ' for ',  projName
			QtGui.QDialog.accept(self)
		else:
			QtGui.QDialog.reject(self)

class Window(QtGui.QMainWindow):
	def __init__(self):
		QtGui.QMainWindow.__init__(self)
		dia = SetCreator()
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

