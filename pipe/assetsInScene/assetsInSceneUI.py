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

uifile = PYFILEDIR + '/assetsInScene.ui'
fom, base = uiH.loadUiType( uifile )

class assetsInSceneUi(base, fom):
	"""docstring for ProjectCreator"""
	def __init__(self, fil,parent=None):
		if uiH.USEPYQT:
			super(base, self).__init__(parent)
		else:
			super(assetsInSceneUi, self).__init__(parent)
		self.setupUi(self)
		self._file = fil
		self.setWindowTitle( str( fil.basename + ' Assets' ) )
		self.connect(self.makeTx_btn, QtCore.SIGNAL("clicked()"), self.makeTx)

	@property
	def fil(self):
		"""return the file"""
		return self._file

	def fillReferencesTable(self):
		"""fill the references table"""
		references = self.fil.references
		self.assets_tw.setRowCount( len( references ) )
		color = [QtGui.QColor( "green" ),
				QtGui.QColor( "red" )]
		for i,t in enumerate(references):
			#NAME
			item = QtGui.QTableWidgetItem( t.basename )
			item.setData(32, t )
			self.assets_tw.setItem( i, 0, item )
			#PATH
			item = QtGui.QTableWidgetItem( t.path )
			if t.exists:
				colVal = 0
			else:
				colVal = 1
			if uiH.USEPYQT:
				item.setBackgroundColor(  color[ colVal ])
			else:
				item.setBackground(  color[ colVal ] )
			self.assets_tw.setItem( i, 1, item )

def main():
	"""use this to create project in maya"""
	pass


