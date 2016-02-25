from rv import rvtypes, extra_commands, commands
import sys, pprint
from Qt import QtGui, QtCore
import pipe.rvPipeL.rvRenderManager as rvMan

class PyQtExample(rvtypes.MinorMode):

	def __init__(self):
		rvtypes.MinorMode.__init__(self)
		self.dialog = rvMan.RenderManager()
		widgets = QtGui.QApplication.topLevelWidgets()
		for w in widgets:
			if "QMainWindow" in str(w):
				w.addDockWidget(QtCore.Qt.RightDockWidgetArea,self.dialog)

		self.init("rvPipeL", None, [("key-down--X", self.toggleDialog, ""),
			("before-session-deletion", self.shutdown, "")],
			[("PipeL", [("Render Selector", self.toggleDialog, "", None)])])
		self.dialog.hide()

	def shutdown(self, event):
		self.deactivate()

	def toggleDialog(self, event):
		if self.dialog.isVisible():
			self.dialog.hide()
		else:
			self.dialog.show()
