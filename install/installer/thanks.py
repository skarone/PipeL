import os
from PySide import QtGui,QtCore
import pyregistry as rg
import xml.etree.ElementTree as xml
import general.ui.pysideuic as pysideuic
from cStringIO import StringIO
from xml.etree.ElementTree import parse, SubElement

PYFILEDIR = os.path.dirname( os.path.abspath( __file__ ) )

uifile = QtCore.QFile("ui/thanks.ui")

def loadUiType(uiFile):
	parsed = xml.parse(uiFile)
	widget_class = parsed.find('widget').get('class')
	form_class = parsed.find('class').text

	with open(uiFile, 'r') as f:
		o = StringIO()
		frame = {}

		pysideuic.compileUi(f, o, indent=0)
		pyc = compile(o.getvalue(), '<string>', 'exec')
		exec pyc in frame

		#Fetch the base_class and form class based on their type in the xml from designer
		form_class = frame['Ui_%s'%form_class]
		base_class = eval('QtGui.%s'%widget_class)
	return form_class, base_class

fom, base = loadUiType( uifile.fileName() )

class ThanksUI(base, fom):
	"""docstring for ProjectCreator"""
	procStart = QtCore.Signal(str)
	def __init__(self, parent  = None ):
		super(ThanksUI, self).__init__(parent)
		self.setWindowFlags(QtCore.Qt.FramelessWindowHint)
		self.setupUi(self)
		self.connect( self.close_btn, QtCore.SIGNAL("clicked()") , self.close )

	@QtCore.Slot()
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
