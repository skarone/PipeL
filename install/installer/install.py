import os
from PySide import QtGui,QtCore
import FaderWidget.FaderWidget as fd
import installer as ins
import thanks as insth

class _ToolsDock(QtGui.QWidget):
	"""Former Miscellaneous, contains all the widgets in the bottom area."""
	def __init__(self, parent=None):
		super(_ToolsDock, self).__init__(parent)
		vbox = QtGui.QVBoxLayout(self)
		vbox.setContentsMargins(0, 0, 0, 0)
		vbox.setSpacing(0)
		self.stack = fd.StackedWidget()
		vbox.addWidget( self.stack )
		self.installer = ins.InstallerUI()
		self.installerHelper = insth.ThanksUI()
		self.stack.addWidget( self.installer )
		self.stack.addWidget( self.installerHelper )
		self.installer.procStart.connect( self.inputconnection )
		self.installerHelper.procStart.connect( self.inputconnection )
		self.setWindowFlags(QtCore.Qt.FramelessWindowHint)

	def mousePressEvent(self, event):
		self.offset = event.pos()

	def mouseMoveEvent(self, event):
		x=event.globalX()
		y=event.globalY()
		x_w = self.offset.x()
		y_w = self.offset.y()
		self.move(x-x_w, y-y_w)

	def inputconnection(self, action):
		"""docstring for inputconnection"""
		if action == 'Installed':
			index_of = self.stack.indexOf(self.installerHelper)
			self.stack.setCurrentIndex( index_of )
		elif action == 'Close':
			self.close()

if __name__=="__main__":
	import sys
	a = QtGui.QApplication(sys.argv)
	global PyForm
	PyForm=_ToolsDock()
	PyForm.show()
	sys.exit(a.exec_())
		
