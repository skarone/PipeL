import os
import general.ui.pySideHelper as uiH
reload( uiH )

from Qt import QtGui,QtCore

import maya.cmds as mc
import maya.mel as mm
import general.mayaNode.mayaNode as mn
import pipe.settings.settings as sti
reload( sti )



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
		self.fillByTypeCMB()
		self.attribute_le.setFocus()
		self.setObjectName( 'multiAttr_WIN' )
		self.attribute_le.setContextMenuPolicy(QtCore.Qt.CustomContextMenu)
		self.attribute_le.customContextMenuRequested.connect(self.showAttributes)
		self.completer = TagsCompleter( self.attribute_le )
		self.completer.setCaseSensitivity(QtCore.Qt.CaseInsensitive)
		self.completer.setWidget( self.attribute_le )
		self.fromCompleter = TagsCompleter( self.fromAttr_le )
		self.fromCompleter.setCaseSensitivity(QtCore.Qt.CaseInsensitive)
		self.fromCompleter.setWidget( self.fromAttr_le )
		self.toCompleter = TagsCompleter( self.toAttr_le )
		self.toCompleter.setCaseSensitivity(QtCore.Qt.CaseInsensitive)
		self.toCompleter.setWidget( self.toAttr_le )
		self._makeConnections()
		self.settings = sti.Settings()
		gen = self.settings.General
		if gen:
			skin = gen[ "skin" ]
			if skin:
				uiH.loadSkin( self, skin )
		#fill list to create CMB
		typs = ['cluster', 'polyCube', 'polySphere','polyCylinder','polyCone',
				'polyPipe','spaceLocator', 'joint']
		self.listToCreate_cmb.addItems(typs)


	def _makeConnections(self):
		"""docstring for _makeConnections"""
		QtCore.QObject.connect( self.attribute_le, QtCore.SIGNAL( "textChanged (const QString&)" ), self.text_changed )
		QtCore.QObject.connect(self.completer, QtCore.SIGNAL('activated(QString)'), self.complete_text)
		QtCore.QObject.connect( self.fromAttr_le, QtCore.SIGNAL( "textChanged (const QString&)" ), self.from_text_changed )
		QtCore.QObject.connect( self.toAttr_le, QtCore.SIGNAL( "textChanged (const QString&)" ), self.to_text_changed )
		QtCore.QObject.connect(self.fromCompleter, QtCore.SIGNAL('activated(QString)'), self.from_complete_text)
		QtCore.QObject.connect(self.toCompleter, QtCore.SIGNAL('activated(QString)'), self.to_complete_text)
		self.connect(self.select_btn, QtCore.SIGNAL("clicked()"), self.select)
		self.connect(self.selectMatch_btn, QtCore.SIGNAL("clicked()"), self.selectMatch)
		self.connect(self.lock_btn, QtCore.SIGNAL("clicked()"), self.lock)
		self.connect(self.unlock_btn, QtCore.SIGNAL("clicked()"), self.unlock)
		self.connect(self.apply_btn, QtCore.SIGNAL("clicked()"), self.apply)
		self.connect(self.remove_btn, QtCore.SIGNAL("clicked()"), self.remove)
		self.connect(self.connect_btn, QtCore.SIGNAL("clicked()"), self.connectList)
		self.connect(self.setFrom_btn, QtCore.SIGNAL("clicked()"), self.setFrom)
		self.connect(self.addFrom_btn, QtCore.SIGNAL("clicked()"), self.addFrom)
		self.connect(self.removeFrom_btn, QtCore.SIGNAL("clicked()"), self.removeFrom)
		self.connect(self.removeTo_btn, QtCore.SIGNAL("clicked()"), self.removeTo)
		self.connect(self.addTo_btn, QtCore.SIGNAL("clicked()"), self.addTo)
		self.connect(self.setTo_btn, QtCore.SIGNAL("clicked()"), self.setTo)
		self.connect(self.createForList_btn, QtCore.SIGNAL("clicked()"), self.createForList)
		#CONSTRAINS
		self.connect(self.parent_btn, QtCore.SIGNAL("clicked()"), self.parentList)
		self.connect(self.point_btn, QtCore.SIGNAL("clicked()"), self.point)
		self.connect(self.orient_btn, QtCore.SIGNAL("clicked()"), self.orient)
		self.connect(self.scale_btn, QtCore.SIGNAL("clicked()"), self.scale)
		QtCore.QObject.connect( self.from_lw, QtCore.SIGNAL( "itemClicked( QListWidgetItem* )" ), self.selectItem )
		QtCore.QObject.connect( self.to_lw, QtCore.SIGNAL( "itemClicked( QListWidgetItem* )" ), self.selectItem )

	def _getItemsInLists(self, check = True):
		"""return the items in the lists"""
		fromItems = []
		for v in xrange( self.from_lw.count()):
			i = self.from_lw.item(v)
			if uiH.USEPYQT:
				n = i.data(32).toPyObject()
			else:
				n = i.data( 32 )
			fromItems.append( n )
		toItems = []
		for v in xrange( self.to_lw.count()):
			i = self.to_lw.item(v)
			if uiH.USEPYQT:
				n = i.data(32).toPyObject()
			else:
				n = i.data( 32 )
			toItems.append( n )
		if check:
			if not len(fromItems) == len(toItems):
				if not len(fromItems) == 1:
					QtGui.QMessageBox.critical(self, 'Bad Input' , "IN THE FIRST LIST YOU MUST HAVE ONE NODE OR THE SAME AMOUNTS\n OF NODE THAT YOU HAVE IN THE SECOND ONE", QtGui.QMessageBox.Close)

		return fromItems, toItems

	def selectMatch(self):
		"""docstring for selectMatch"""
		attrs = self._getAttributes()
		try:
			value = eval( str( self.value_le.text() ) )
		except:
			value =  str( self.value_le.text() )
		objsToSelect= []
		for o in self._getObjects():
			for attr in attrs:
				if isinstance(value, str):
					if o.attr(attr).exists:
						if value in o.attr(attr).v:
							objsToSelect.append( o )
				elif abs(o.attr( attr ).v-value)<0.001:
					objsToSelect.append( o )
		mc.select( objsToSelect )

	def connectList(self):
		"""docstring for connect"""
		fromItems, toItems = self._getItemsInLists()
		#if fromItems es only 1 item, then connect thisone to all toItems
		fromAttribute = str( self.fromAttr_le.text() )
		toAttribute = str( self.toAttr_le.text() )
		if len( fromItems ) == 1:
			for toNode in toItems:
				fromItems[0].attr( fromAttribute ) >> toNode.attr( toAttribute )
		else:
			for fromNode,toNode in zip( fromItems, toItems ):
				fromNode.attr( fromAttribute ) >> toNode.attr( toAttribute )

	def setFrom(self):
		"""clear and add items to From list"""
		self.from_lw.clear()
		for f in mn.ls( sl = True, fl = True ):
			item = QtGui.QListWidgetItem( f.name )
			item.setData(32, f )
			self.from_lw.addItem( item )
		self._changeListCount( self.from_lw )

	def addFrom(self):
		"""add itmes to From list without cleaning"""
		for f in mn.ls( sl = True, fl = True ):
			item = QtGui.QListWidgetItem( f.name )
			item.setData(32, f )
			self.from_lw.addItem( item )
		self._changeListCount( self.from_lw )

	def removeFrom(self):
		"""remove selected item from Form list"""
		for SelectedItem in self.from_lw.selectedItems():
			self.from_lw.takeItem(self.from_lw.row(SelectedItem))
		self._changeListCount( self.from_lw )

	def removeTo(self):
		"""remove selected item from To list"""
		for SelectedItem in self.to_lw.selectedItems():
			self.to_lw.takeItem(self.to_lw.row(SelectedItem))
		self._changeListCount( self.to_lw )

	def addTo(self):
		"""add itmes to To list without cleaning"""
		for f in mn.ls( sl = True ):
			item = QtGui.QListWidgetItem( f.name )
			item.setData(32, f )
			self.to_lw.addItem( item )
		self._changeListCount( self.to_lw )

	def setTo(self):
		"""clear and add items to To list"""
		self.to_lw.clear()
		for f in mn.ls( sl = True ):
			item = QtGui.QListWidgetItem( f.name )
			item.setData(32, f )
			self.to_lw.addItem( item )
		self._changeListCount( self.to_lw )

	def _changeListCount(self, listWidget):
		"""docstring for _changeListCount"""
		if listWidget == self.to_lw:
			self.toListCount_lbl.setText( str( listWidget.count() ) )
		else:
			self.fromListCount_lbl.setText( str( listWidget.count() ) )


	def parentList(self):
		"""make a parent constraint between lists"""
		fromItems, toItems = self._getItemsInLists()
		maintainOffset = self.maintainOffset_chb.isChecked()
		if len( fromItems ) == 1:
			for toNode in toItems:
				mc.parentConstraint( fromItems[0].name, toNode.name, mo = maintainOffset )
		else:
			for fromNode,toNode in zip( fromItems, toItems ):
				mc.parentConstraint( fromNode.name, toNode.name, mo = maintainOffset )

	def createForList(self):
		"""docstring for createForList"""
		typSel = self.listToCreate_cmb.currentIndex()
		typs = ['cluster', 'polyCube', 'polySphere','polyCylinder','polyCone','polyPipe','spaceLocator', 'joint']
		res = []
		fromItems, toItems = self._getItemsInLists(False)
		for o in fromItems:
			mc.select( cl = True )
			retVal = 0
			if typSel == 0: #cluster
				mc.select( o )
				retVal = 1
			ret = mm.eval( typs[typSel] + ';' )
			if typSel == 7:
				res.append( ret )
			else:
				res.append( ret[retVal] )
		mc.select( res )

	def point(self):
		"""make a point constraint between lists"""
		fromItems, toItems = self._getItemsInLists()
		maintainOffset = self.maintainOffset_chb.isChecked()
		if len( fromItems ) == 1:
			for toNode in toItems:
				mc.pointConstraint( fromItems[0].name, toNode.name, mo = True )
		else:
			for fromNode,toNode in zip( fromItems, toItems ):
				mc.pointConstraint( fromNode.name, toNode.name, mo = True )

	def orient(self):
		"""make a orient constraint between lists"""
		fromItems, toItems = self._getItemsInLists()
		maintainOffset = self.maintainOffset_chb.isChecked()
		if len( fromItems ) == 1:
			for toNode in toItems:
				mc.orientConstraint( fromItems[0].name, toNode.name, mo = maintainOffset )
		else:
			for fromNode,toNode in zip( fromItems, toItems ):
				mc.orientConstraint( fromNode.name, toNode.name, mo = maintainOffset )

	def scale(self):
		"""make a scale constraint between lists"""
		fromItems, toItems = self._getItemsInLists()
		maintainOffset = self.maintainOffset_chb.isChecked()
		if len( fromItems ) == 1:
			for toNode in toItems:
				mc.scaleConstraint( fromItems[0].name, toNode.name, mo = maintainOffset )
		else:
			for fromNode,toNode in zip( fromItems, toItems ):
				mc.scaleConstraint( fromNode.name, toNode.name, mo = maintainOffset )

	def selectItem(self, item):
		"""select node when node is selected in list"""
		if uiH.USEPYQT:
			n = item.data(32).toPyObject()
		else:
			n = item.data( 32 )
		n()

	def from_text_changed(self, text):
		all_text = unicode(text)
		text = all_text[:self.fromAttr_le.cursorPosition()]
		prefix = text.split(',')[-1].strip()
		text_tags = []
		for t in all_text.split(','):
			t1 = unicode(t).strip()
			if t1 != '':
				text_tags.append(t)
		text_tags = list(set(text_tags))
		i = self.from_lw.item(0)
		if i:
			if uiH.USEPYQT:
				n = i.data(32).toPyObject()
			else:
				n = i.data( 32 )
			attrs = [a.name for a in n.listAttr( s = True ) ]
			self.fromCompleter.update( attrs, text_tags, prefix )

	def from_complete_text(self, text):
		cursor_pos = self.fromAttr_le.cursorPosition()
		before_text = unicode(self.fromAttr_le.text())[:cursor_pos]
		after_text = unicode(self.fromAttr_le.text())[cursor_pos:]
		self.fromAttr_le.setText('%s' % (text))
		self.fromAttr_le.setCursorPosition(cursor_pos + len(text) + 1)


	def to_text_changed(self, text):
		all_text = unicode(text)
		text = all_text[:self.toAttr_le.cursorPosition()]
		prefix = text.split(',')[-1].strip()
		text_tags = []
		for t in all_text.split(','):
			t1 = unicode(t).strip()
			if t1 != '':
				text_tags.append(t)
		text_tags = list(set(text_tags))
		i = self.to_lw.item(0)
		if i:
			if uiH.USEPYQT:
				n = i.data(32).toPyObject()
			else:
				n = i.data( 32 )
			attrs = [a.name for a in n.listAttr( s = True ) ]
			self.toCompleter.update( attrs, text_tags, prefix )

	def to_complete_text(self, text):
		cursor_pos = self.toAttr_le.cursorPosition()
		before_text = unicode(self.toAttr_le.text())[:cursor_pos]
		after_text = unicode(self.toAttr_le.text())[cursor_pos:]
		self.toAttr_le.setText('%s' % ( text))
		self.toAttr_le.setCursorPosition(cursor_pos + len(text) + 1)

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
		try:
			value = eval( str( self.value_le.text() ) )
		except:
			value =  str( self.value_le.text() )
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
		for a in attrs.split( ',' ):
			if a.strip() == '':
				continue
			finalAttrs.append( a.strip() )
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

