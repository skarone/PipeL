import os

import general.ui.pySideHelper as uiH
reload( uiH )
uiH.set_qt_bindings()
from Qt import QtGui,QtCore

import general.mayaNode.mayaNode as mn
import hair.hairSystem.hairSystem as hr

#load UI FILE
PYFILEDIR = os.path.dirname( os.path.abspath( __file__ ) )
uifile = PYFILEDIR + '/hair.ui'
fom, base = uiH.loadUiType( uifile )

import maya.cmds as mc

class hairUi(base,fom):
	def __init__(self, parent  = uiH.getMayaWindow(), *args ):
		if uiH.USEPYQT:
			super(base, self).__init__(parent)
		else:
			super(hairUi, self).__init__(parent)
		self.setupUi(self)
		self._makeConnections()
		self.setObjectName( 'hairUi' )
		uiH.loadSkin( self, 'QTDarkGreen' )

	def _makeConnections(self):
		"""docstring for _makeConnections"""
		self.connect( self.insertScalp_btn, QtCore.SIGNAL("clicked()") , self.insertScalp)
		self.connect( self.addGroup_btn, QtCore.SIGNAL("clicked()") , self.addGroup )
		self.connect( self.removeGroup_btn, QtCore.SIGNAL("clicked()") , self.removeGroup )
		self.connect( self.clearGroups_btn, QtCore.SIGNAL("clicked()") , self.clearGroups )
		self.connect( self.create_btn, QtCore.SIGNAL("clicked()") , self.create )

	def insertScalp(self):
		"""docstring for insertScalp"""
		sel = mn.ls( sl = True )
		if sel:
			self.scalp_le.setText( sel[0].name )

	def addGroup(self):
		"""docstring for addGroup"""
		sel = mn.ls( sl = True )
		if sel:
			self.groups_lw.addItems( sel.names )

	def removeGroup(self):
		"""docstring for removeGroup"""
		for SelectedItem in self.groups_lw.selectedItems():
			self.groups_lw.takeItem(self.groups_lw.row(SelectedItem))

	def clearGroups(self):
		"""docstring for clearGroups"""
		self.groups_lw.clear()

	def create(self):
		"""docstring for create"""
		scalp = str( self.scalp_le.text() )
		for index in xrange(self.groups_lw.count()):
			grp = mn.Node( str( self.groups_lw.item(index).text()) )
			mc.select( grp.children )
			asd = hr.hairSystemAutomator( sysName = grp.name.replace( '_lock_grp', '' ), scalp = scalp )

def main():
	"""call this from maya"""
	if mc.window( 'hairUi', q = 1, ex = 1 ):
		mc.deleteUI( 'hairUi' )
	PyForm=hairUi()
	PyForm.show()
