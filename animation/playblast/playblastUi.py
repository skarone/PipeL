import os
import pipe.mayaFile.mayaFile as mfl
import pipe.file.file as fl
import general.ui.pySideHelper as uiH
reload( uiH )
uiH.set_qt_bindings()
from Qt import QtGui,QtCore

PYFILEDIR = os.path.dirname(os.path.abspath(__file__))

uifile = PYFILEDIR + '/playblast.ui'
fom, base = uiH.loadUiType( uifile )

import animation.playblast.playblast as plb
reload(plb)
import maya.cmds as mc

class PlayblastUi(base,fom):
	"""manager ui class"""
	def __init__(self, parent = uiH.getMayaWindow() ):
		if uiH.USEPYQT:
			super(base, self).__init__(parent)
		else:
			super(PlayblastUi, self).__init__(parent)
		self.setupUi(self)
		self._makeConnections()
		self.setObjectName( 'PlayblastUi' )

	def _makeConnections(self):
		"""docstring for _makeConnections"""
		self.connect( self.playblast_btn , QtCore.SIGNAL("clicked()") , self.playblast )
		self.connect( self.publish_btn , QtCore.SIGNAL("clicked()") , self.publish )

	def playblast(self):
		"""docstring for playblast"""
		plb.playblastCurrentFile()

	def publish(self):
		"""docstring for publish"""
		fil = mfl.currentFile()
		if not fil:
			print 'Please Save File To create Playblast'
			return
		movFil = fl.File( fil.versionPath + fil.name + '_v' + str( fil.version ).zfill( 3 ) + '.mov' )
		if movFil.exists:
			movFil.copy( fil.dirPath + fil.name + '.mov' )

def main():
	if mc.window( 'PlayblastUi', q = 1, ex = 1 ):
		mc.deleteUI( 'PlayblastUi' )
	PyForm=PlayblastUi()
	PyForm.show()
