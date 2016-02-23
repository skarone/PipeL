from rv import rvtypes, extra_commands, commands
import sys, pprint
from Qt import QtGui, QtCore

class SampleDialog(QtGui.QDockWidget):

	def __init__(self):
		QtGui.QDockWidget.__init__(self, None)

		widget = QtGui.QWidget()
		mainLayout = QtGui.QVBoxLayout()

		button = QtGui.QPushButton("Button")
		mainLayout.addWidget(button)

		combo = QtGui.QComboBox()
		combo.addItem("Combo")
		mainLayout.addWidget(combo)

		tree = QtGui.QTreeWidget()
		item = QtGui.QTreeWidgetItem(tree)
		item.setText(0,"Tree Item")
		tree.addTopLevelItem(item)
		mainLayout.addWidget(tree)

		line = QtGui.QLineEdit("Line Edit")
		mainLayout.addWidget(line)

		widget.setLayout(mainLayout)
		self.setWidget(widget)
		self.connect( button, QtCore.SIGNAL("clicked()") , self.loadFile )

	def loadFile(self):
		sources = commands.nodesOfType("RVFileSource")
		stacks = commands.nodesOfType("RVStackGroup")
		print stacks
		commands.setViewNode( stacks[0] )
		if sources:
			commands.setSourceMedia( sources[0], ['Q:/Spontex/Sequences/Hedgehog/Shots/s002_Hedgehog_T01/3D_Render/Beauty/Erizo_Beauty/v0001/Erizo_Beauty.1-66#.exr'], None )
		else:
			asd = commands.addSourceVerbose( ['Q:/Spontex/Sequences/Hedgehog/Shots/s002_Hedgehog_T01/3D_Render/Beauty/Erizo_Beauty/v0001/Erizo_Beauty.1-66#.exr'], 'mierda' )
			assGroup = commands.nodeGroup(asd)
			commands.setStringProperty(assGroup + '.ui.name', ['coco'])
			print commands.addSourceVerbose(['Q:/Spontex/Sequences/Hedgehog/Shots/s002_Hedgehog_T01/3D_Render/Beauty/Esponja_Beauty/v0001/Esponja_Beauty.1-66#.exr'], None )
		print commands.nodes()

class PyQtExample(rvtypes.MinorMode):

	def __init__(self):
		rvtypes.MinorMode.__init__(self)
		self.dialog = SampleDialog()
		widgets = QtGui.QApplication.topLevelWidgets()
		for w in widgets:
			if "QMainWindow" in str(w):
				w.addDockWidget(QtCore.Qt.RightDockWidgetArea,self.dialog)

		self.init("PyQtExample", None, [("key-down--X", self.toggleDialog, ""),
			("before-session-deletion", self.shutdown, "")],
			[("PyQtExample", [("Example 1", self.toggleDialog, "", None)])])
		self.dialog.hide()

	def shutdown(self, event):
		self.deactivate()

	def toggleDialog(self, event):
		if self.dialog.isVisible():
			self.dialog.hide()
		else:
			self.dialog.show()

def createMode():
	return PyQtExample()

