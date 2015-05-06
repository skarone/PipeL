import os
import general.ui.pySideHelper as uiH
reload( uiH )
uiH.set_qt_bindings()
from Qt import QtGui,QtCore
import pipe.houdiniFile.houdiniFile as hfl

PYFILEDIR = os.path.dirname( os.path.abspath( __file__ ) )

uifile = PYFILEDIR + '/houdiniFile.ui'
fom, base = uiH.loadUiType( uifile )

class HoudiniNewFile(base, fom):
	def __init__(self,baseFile, parent = None ):
		if uiH.USEPYQT:
			super(base, self).__init__()
		else:
			super(HoudiniNewFile, self).__init__()
		self.setupUi(self)
		self.setObjectName( 'HoudiniNewFile' )
		self.connect(self.buttonBox, QtCore.SIGNAL("accepted()"), self.createFile)
		self._baseFile = baseFile
		self.baseName_lbl.setText( baseFile.name )
		self.fileName_le.setFocus()
		

	def createFile(self):
		"""create File"""
		name = str(self.fileName_le.text())
		fi = hfl.houdiniFile( self._baseFile.dirPath + '/' + str( self.baseName_lbl.text()) + '_' + name + '.hip' )
		fi.write( '' )
		fi.open()

class Window(QtGui.QMainWindow):
	def __init__(self):
		QtGui.QMainWindow.__init__(self)
		dia = HoudiniNewFile()
		dia.exec_()

