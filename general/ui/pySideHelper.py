from cStringIO import StringIO
import xml.etree.ElementTree as xml
try:
	import maya.OpenMayaUI as mui
except:
	pass

USEPYQT = True
try:
	import shiboken
except:
	pass
try:
	from PySide import QtGui, QtCore
	import general.ui.pysideuic as pysideuic
	USEPYQT = False
except:
	from PyQt4 import QtGui,QtCore, uic
	import sip
import os

PYFILEDIR = os.path.dirname( os.path.abspath( __file__ ) )

def set_qt_bindings():
	if USEPYQT:
		package = 'PyQt4'
	else:
		package = 'PySide'
	if package not in ('PyQt4', 'PySide'):
		raise ValueError('Unknown Qt Bindings: %s' % package)
	import __builtin__
	__import__ = __builtin__.__import__
	def hook(name, globals=None, locals=None, fromlist=None, level=-1):
		root, sep, other = name.partition('.')
		if root == 'Qt':
			name = package + sep + other
		return __import__(name, globals, locals, fromlist, level)
	__builtin__.__import__ = hook

"""
def set_qt_bindings():
	if USEPYQT:
		package = 'PyQt4'
	else:
		package = 'PySide'
	if package not in ('PyQt4', 'PySide'):
		raise ValueError('Unknown Qt Bindings: %s' % package)
	import __builtin__
	__import__ = __builtin__.__import__
	def hook(name, globals=None, locals=None, fromlist=None, level=-1):
		root, sep, other = name.partition('.')
		if root == 'Qt':
			name = package + sep + other
		return __import__(name, globals, locals, fromlist, level)
	__builtin__.__import__ = hook
"""

def getMayaWindow():
	"""
	Get the main Maya window as a QtGui.QMainWindow instance
	@return: QtGui.QMainWindow instance of the top level Maya windows
	"""
	ptr = mui.MQtUtil.mainWindow()
	if USEPYQT:
		return sip.wrapinstance( long( ptr ), QtCore.QObject )
	else:
		return shiboken.wrapInstance(long(ptr), QtGui.QMainWindow)


def loadSkin( obj, skinName ):
	"""docstring for loadSkin"""
	sshFile=PYFILEDIR  + "/skins/" + skinName + ".stylesheet"
	with open(sshFile,"r") as fh:
		obj.setStyleSheet(fh.read())

def loadUiType(uiFile):
	"""
	Pyside lacks the "loadUiType" command, so we have to convert the ui file to py code in-memory first
	and then execute it in a special frame to retrieve the form_class.
	"""
	if USEPYQT:
		return uic.loadUiType( uiFile )
	else:
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



