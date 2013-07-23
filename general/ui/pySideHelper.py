from cStringIO import StringIO
import maya.OpenMayaUI as apiUI
import xml.etree.ElementTree as xml
import shiboken
from PySide import QtGui, QtCore
import pysideuic

def getMayaWindow():
	"""
	Get the main Maya window as a QtGui.QMainWindow instance
	@return: QtGui.QMainWindow instance of the top level Maya windows
	"""
	ptr = apiUI.MQtUtil.mainWindow()
	print ptr
	if ptr is not None:
		return shiboken.wrapInstance(long(ptr), QtGui.QMainWindow)


def loadUiType(uiFile):
	"""
	Pyside lacks the "loadUiType" command, so we have to convert the ui file to py code in-memory first
	and then execute it in a special frame to retrieve the form_class.
	"""
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



