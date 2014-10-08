import os

import general.ui.pySideHelper as uiH
reload( uiH )
uiH.set_qt_bindings()
from Qt import QtGui,QtCore

import pipe.project.project   as prj
import pipe.asset.asset as ass
reload( ass )
reload( prj )

PYFILEDIR = os.path.dirname( os.path.abspath( __file__ ) )

uifile = PYFILEDIR + '/nukeFileProperties.ui'
fom, base = uiH.loadUiType( uifile )

class NukeFilePropertiesUi(base, fom):
	"""docstring for ProjectCreator"""
	def __init__(self, fil,parent=None):
		if uiH.USEPYQT:
			super(base, self).__init__(parent)
		else:
			super(NukeFilePropertiesUi, self).__init__(parent)
		self.setupUi(self)
		self._file = fil
		self.filepath_la.setText( str(fil.path) )
		self.setWindowTitle( str( fil.basename + ' Properties' ) )
		if not fil.exists:
			return
		if fil.isZero:
			return
		self.filedate_la.setText( str(fil.date))
		self.time_start_la.setText( fil.start )
		self.fps_la.setText( fil.fps )
		self.time_end_la.setText( fil.end )

	@property
	def fil(self):
		"""return the file"""
		return self._file

	def fillTexturesTable(self):
		"""add textures from file"""
		color = [QtGui.QColor( "green" ),
				QtGui.QColor( "red" )]
		deps = self.fil.dependences
		self.textures_tw.setRowCount( len( deps ) )
		for i,t in enumerate(deps):
			#NAME
			item = QtGui.QTableWidgetItem( t.Type )
			self.textures_tw.setItem( i, 0, item )
			#PATH
			item = QtGui.QTableWidgetItem( t.path )
			self.textures_tw.setItem( i, 2, item )

class Window(QtGui.QMainWindow):
	def __init__(self):
		QtGui.QMainWindow.__init__(self)
		dia = NukeFilePropertiesUi()
		dia.exec_()
	
def main():
	"""use this to create project in maya"""
	pass


if __name__=="__main__":
	import sys
	a = QtGui.QApplication(sys.argv)
	global PyForm
	a.setStyle('plastique')
	PyForm=Window()
	PyForm.show()
	sys.exit(a.exec_())

