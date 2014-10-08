import os
from PyQt4 import QtGui,QtCore, uic
import pyregistry as rg
from xml.etree.ElementTree import parse, SubElement

PYFILEDIR = os.path.dirname( os.path.abspath( __file__ ) )

uifile = QtCore.QFile("ui/thanks.ui")
print 'asd',uifile.fileName(), uifile.exists()
fom, base = uic.loadUiType( uifile.fileName() )

class ThanksUI(base, fom):
	"""docstring for ProjectCreator"""
	procStart = QtCore.pyqtSignal(str)
	def __init__(self, parent  = None ):
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
