import os
import general.ui.pySideHelper as uiH
reload( uiH )
uiH.set_qt_bindings()
from Qt import QtGui,QtCore

import maya.cmds as mc
import general.mayaNode.mayaNode as mn


"""
import general.multiAttribute.multiAttributeUi as maUI
reload( maUI )
maUI.main()
"""

PYFILEDIR = os.path.dirname( os.path.abspath( __file__ ) )

uifile = PYFILEDIR + '/multiAttribute.ui'
fom, base = uiH.loadUiType( uifile )


class MultiAttributeUI(base, fom):
	"""docstring for ProjectCreator"""
	def __init__(self, parent  = uiH.getMayaWindow(), *args ):
		if uiH.USEPYQT:
			super(base, self).__init__(parent)
		else:
			super(MultiAttributeUI, self).__init__(parent)
		self.setupUi(self)
		self.connect(self.select_btn, QtCore.SIGNAL("clicked()"), self.select)
		self.connect(self.lock_btn, QtCore.SIGNAL("clicked()"), self.lock)
		self.connect(self.unlock_btn, QtCore.SIGNAL("clicked()"), self.unlock)
		self.connect(self.apply_btn, QtCore.SIGNAL("clicked()"), self.apply)
		self.connect(self.remove_btn, QtCore.SIGNAL("clicked()"), self.remove)
		QtCore.QObject.connect( self.attribute_le, QtCore.SIGNAL( "textChanged (const QString&)" ), self.text_changed )
		self.fillByTypeCMB()
		self.attribute_le.setFocus()
		self.setObjectName( 'multiAttr_WIN' )
		uiH.loadSkin( self, 'QTDarkGreen' )
		self.attribute_le.setContextMenuPolicy(QtCore.Qt.CustomContextMenu)
		self.attribute_le.customContextMenuRequested.connect(self.showAttributes)
		self.completer = TagsCompleter( self.attribute_le )
		self.completer.setCaseSensitivity(QtCore.Qt.CaseInsensitive)
		QtCore.QObject.connect(self.completer, QtCore.SIGNAL('activated(QString)'), self.complete_text) 
		self.completer.setWidget( self.attribute_le )

 
	def text_changed(self, text):
		all_text = unicode(text)
		text = all_text[:self.attribute_le.cursorPosition()]
		prefix = text.split(',')[-1].strip()
 
		text_tags = []
		for t in all_text.split(','):
			t1 = unicode(t).strip()
			if t1 != '':
				text_tags.append(t)
		text_tags = list(set(text_tags))
		objs = self._getObjects()
		attrs = [a.name for a in objs[0].listAttr( s = True ) ]
		self.completer.update( attrs, text_tags, prefix )
  
	def complete_text(self, text):
		cursor_pos = self.attribute_le.cursorPosition()
		before_text = unicode(self.attribute_le.text())[:cursor_pos]
		after_text = unicode(self.attribute_le.text())[cursor_pos:]
		prefix_len = len(before_text.split(',')[-1].strip())
		self.attribute_le.setText('%s%s, %s' % (before_text[:cursor_pos - prefix_len], text, after_text))
		self.attribute_le.setCursorPosition(cursor_pos - prefix_len + len(text) + 2)

	def showAttributes(self, pos):
		"""docstring for showAttributes"""
		menu=QtGui.QMenu(self)
		for a in self._getObjects()[0].listAttr( s = True ):
			actionProperties = QtGui.QAction( a.name, menu)
			menu.addAction( actionProperties )
			self.connect( actionProperties, QtCore.SIGNAL( "triggered()" ), lambda val = a.name : self.attribute_le.setText(val) )
		menu.popup(self.mapToGlobal(pos))
		self.attribute_le.setFocus()
		
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
		attrs = self._getAttributes()
		value = eval( str( self.value_le.text() ) )
		for o in self._getObjects():
			for attr in attrs:
				o.attr( attr ).overrided = override
				o.attr( attr ).v = value

	def remove(self):
		"""remove override on objects"""
		attrs = self._getAttributes()
		for o in self._getObjects():
			for attr in attrs:
				o.attr( attr ).overrided = False

	def _getAttributes(self):
		"""return the attributes of the line edit"""
		attrs = str( self.attribute_le.text() )
		finalAttrs = []
		for a in attrs.split( ', ' ):
			if a == '':
				continue
			finalAttrs.append( a )
		return finalAttrs

	def lock(self):
		"""lock attribute"""
		attrs = self._getAttributes()
		for o in self._getObjects():
			for attr in attrs:
				o.attr( attr ).locked = True

	def unlock(self):
		"""unlock attribute"""
		attrs = self._getAttributes()
		for o in self._getObjects():
			for attr in attrs:
				o.attr( attr ).locked = False
		

class TagsCompleter(QtGui.QCompleter):
	def __init__(self, parent):
		QtGui.QCompleter.__init__(self, parent)

	def update(self, all_tags, text_tags, completion_prefix):
		tags = list(set(all_tags).difference(text_tags))
		model = QtGui.QStringListModel(tags, self)
		self.setModel(model)
		self.setCompletionPrefix(completion_prefix)
		if completion_prefix.strip() != '':
			self.complete()

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

