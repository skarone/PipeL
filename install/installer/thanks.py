import os
from PyQt4 import QtGui,QtCore, uic
import pyregistry as rg

PYFILEDIR = os.path.dirname( os.path.abspath( __file__ ) )

uifile = PYFILEDIR + '/thanks.ui'
fom, base = uic.loadUiType( uifile )

class ThanksUI(base, fom):
	"""docstring for ProjectCreator"""
	procStart = QtCore.pyqtSignal(str)
	def __init__(self, parent  = None, *args ):
		super(base, self).__init__(parent)
		self.setWindowFlags(QtCore.Qt.FramelessWindowHint)
		self.setupUi(self)
		self.connect( self.close_btn, QtCore.SIGNAL("clicked()") , self.close )

	@QtCore.pyqtSlot()
	def close(self):
		"""docstring for close"""
		self.procStart.emit( 'Close' )

if __name__=="__main__":
	import sys
	a = QtGui.QApplication(sys.argv)
	global PyForm
	PyForm=ThanksUI()
	PyForm.show()
	sys.exit(a.exec_())