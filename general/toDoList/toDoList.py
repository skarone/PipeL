# -*- coding: utf-8 -*-
"""
Thomdo

A simple todo-list application written in Python + PySide
"""
import os
import general.ui.pySideHelper as uiH
reload( uiH )
uiH.set_qt_bindings()
from Qt import QtGui,QtCore

INMAYA = False
try:
	import maya.cmds as mc
	INMAYA = True
except:
	pass
INNUKE = False
try:
	import nuke
	INNUKE = True
except:
	pass

import sys
import json
import pipe.settings.settings as sti
reload( sti )

PYFILEDIR = os.path.dirname( os.path.abspath( __file__ ) )

uifile = PYFILEDIR + '/thomdo_gui.ui'
fom, base = uiH.loadUiType( uifile )

TODOFILE = str( os.getenv('USERPROFILE') ) + '/pipel_toDo.json'

class Thomdo(base,fom):
	def __init__(self, parent = None):
		if INMAYA:
			if uiH.USEPYQT:
				super(base, self).__init__(uiH.getMayaWindow())
			else:
				super(Thomdo, self).__init__(uiH.getMayaWindow())
		else:
			if uiH.USEPYQT:
				super(base, self).__init__(parent)
			else:
				super(Thomdo, self).__init__(parent)
		self.setupUi(self)
		self.setObjectName( 'Thomdo' )
		self.entryField.returnPressed.connect(self.return_pressed)
		self.clearButton.clicked.connect(self.clear)
		#self.saveButton.clicked.connect(self.save)
		#self.loadButton.clicked.connect(self.load)
		self.taskList.itemClicked.connect(self.itemClicked)
		self.taskList.itemChanged.connect( self.save )
		self.load()
		self.settings = sti.Settings()
		gen = self.settings.General
		if gen:
			skin = gen[ "skin" ]
			if skin:
				uiH.loadSkin( self, skin )

	def itemClicked(self, item):
		"""check if item is checked if it is... set text to ---"""
		if item.checkState() == QtCore.Qt.Checked:
			fn = item.font()
			fn.setStrikeOut(1)
			item.setFont( fn )
		else:
			fn = item.font()
			fn.setStrikeOut(0)
			item.setFont( fn )

	def clear(self):
		""" clears checked items """
		for item in self._tasks():
			if item.checkState() == QtCore.Qt.Checked:
				row = self.taskList.row(item)
				self.taskList.takeItem(row)
		self.save()

	def save(self):
		""" saves the task as a json file """
		with open(TODOFILE, "w") as f:
			json.dump(self._tasks_dict(), f)

	def load(self):
		""" parses a saved json task file and fills the list """
		if os.path.exists( TODOFILE ):
			with open(TODOFILE, 'rb') as f:
				tasks = json.loads(f.read())
				self.taskList.clear()
				for task in tasks:
					self._add_task(task['title'], task['done'])

	def return_pressed(self):
		""" clears the line edit and inserts the task """
		entered_text = self.entryField.text()
		if entered_text != "":
			self.entryField.clear()
			self._add_task(entered_text, False)

	def _tasks(self):
		""" returns all tasks as a list of QListWidgetItems """
		tasklist = self.taskList
		return [tasklist.item(i) for i in range(tasklist.count())]

	def _tasks_dict(self):
		""" returns all tasks as array of dictionaries """
		dicts = []
		for task in self._tasks():
			done = (task.checkState() == QtCore.Qt.Checked)
			dict = {"title": task.text(), "done": done}
			dicts.insert(0, dict)
		return dicts

	def _add_task(self, title, checked):
		""" inserts a task at the beginning of the ui.taskList widget """
		item = QtGui.QListWidgetItem()
		item.setText(title)
		if checked:
			fn = item.font()
			fn.setStrikeOut(1)
			item.setFont( fn )
			item.setCheckState(QtCore.Qt.Checked)
		else:
			item.setCheckState(QtCore.Qt.Unchecked)
		item.setFlags( item.flags() | QtCore.Qt.ItemIsEditable )
		self.taskList.insertItem(0, item)
		self.save()

def main():
	"""use this to create project in maya"""
	global PyForm
	if INMAYA:
		if mc.window( 'Thomdo', q = 1, ex = 1 ):
			mc.deleteUI( 'Thomdo' )
	if INNUKE:
		PyForm=Thomdo(parent=QtGui.QApplication.activeWindow())
	else:
		PyForm=Thomdo()
	PyForm.show()

if __name__ == "__main__":
	a = QtGui.QApplication(sys.argv)
	global PyForm
	a.setStyle('plastique')
	PyForm=Thomdo()
	PyForm.show()
	sys.exit(a.exec_())
