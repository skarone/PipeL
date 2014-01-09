import os
from PyQt4 import QtGui,QtCore, uic
import maya.cmds as mc
import general.mayaNode.mayaNode as mn
import maya.OpenMayaUI as mui
import sip


"""
import general.multiAttribute.multiAttributeUi as maUI
reload( maUI )
maUI.main()
"""

PYFILEDIR = os.path.dirname( os.path.abspath( __file__ ) )

uifile = PYFILEDIR + '/multiAttribute.ui'
fom, base = uic.loadUiType( uifile )

def get_maya_main_window( ):
	ptr = mui.MQtUtil.mainWindow( )
	main_win = sip.wrapinstance( long( ptr ), QtCore.QObject )
	return main_win


class MultiAttributeUI(base, fom):
	"""docstring for ProjectCreator"""
	def __init__(self, parent  = get_maya_main_window(), *args ):
		super(base, self).__init__(parent)
		self.setupUi(self)
		self.connect(self.select_btn, QtCore.SIGNAL("clicked()"), self.select)
		self.connect(self.lock_btn, QtCore.SIGNAL("clicked()"), self.lock)
		self.connect(self.unlock_btn, QtCore.SIGNAL("clicked()"), self.unlock)
		self.connect(self.apply_btn, QtCore.SIGNAL("clicked()"), self.apply)
		self.connect(self.remove_btn, QtCore.SIGNAL("clicked()"), self.remove)
		self.fillByTypeCMB()
		self.attribute_le.setFocus()
		self.setObjectName( 'multiAttr_WIN' )

	def fillByTypeCMB(self):
		"""fill combo box with types"""
		self.type_cmb.clear()
		allTypes = sorted( mc.allNodeTypes() )
		allTypes.insert( 0, '' )
		self.type_cmb.addItems( allTypes )

	def _getObjects(self):
		"""return the objects that match the search"""
		search = str( self.search_le.text() )
		byType = str( self.type_cmb.currentText() )
		onSel  = self.onSelection_chb.isChecked()
		objs   = []
		if byType == '':
			objs = mn.ls( search, ni = True, sl = onSel )
		else:
			objs = mn.ls( search, type = byType, ni = True, sl = onSel )
		return objs

	def select(self):
		"""select objects that match search"""
		mc.select( [a.name for a in self._getObjects()] )

	def apply(self):
		"""set values for attribute"""
		override = self.override_chb.isChecked()
		mn.AUTO_ATTR_OVERRIDE = override
		attr = str( self.attribute_le.text() )
		value = eval( str( self.value_le.text() ) )
		for o in self._getObjects():
			o.attr( attr ).overrided = override
			o.attr( attr ).v = value

	def remove(self):
		"""remove override on objects"""
		attr = str( self.attribute_le.text() )
		for o in self._getObjects():
			o.attr( attr ).overrided = False

	def lock(self):
		"""lock attribute"""
		attr = str( self.attribute_le.text() )
		for o in self._getObjects():
			o.attr( attr ).locked = True

	def unlock(self):
		"""unlock attribute"""
		attr = str( self.attribute_le.text() )
		for o in self._getObjects():
			o.attr( attr ).locked = False
		
		

class Window(QtGui.QMainWindow):
	def __init__(self):
		QtGui.QMainWindow.__init__(self)
		dia = MultiAttributeUI()
		dia.exec_()
	
def main():
	"""use this to create project in maya"""
	if mc.window( 'multiAttr_WIN', q = 1, ex = 1 ):
		mc.deleteUI( 'multiAttr_WIN' )
	PyForm=MultiAttributeUI()
	PyForm.show()


if __name__=="__main__":
	import sys
	a = QtGui.QApplication(sys.argv)
	global PyForm
	a.setStyle('plastique')
	PyForm=Window()
	PyForm.show()
	sys.exit(a.exec_())

