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

uifile = PYFILEDIR + '/mayaFileProperties.ui'
fom, base = uiH.loadUiType( uifile )

class MayaFilePropertiesUi(base, fom):
	"""docstring for ProjectCreator"""
	def __init__(self, fil,parent=None):
		if uiH.USEPYQT:
			super(base, self).__init__(parent)
		else:
			super(MayaFilePropertiesUi, self).__init__(parent)
		self.setupUi(self)
		self._file = fil
		self.filepath_la.setText( str(fil.path) )
		self.setWindowTitle( str( fil.basename + ' Properties' ) )
		if not fil.exists:
			return
		if fil.isZero:
			return
		self.filedate_la.setText( str(fil.date))
		tim = fil.time
		self.time_startbase_la.setText( str(tim['ast']) )
		self.time_start_la.setText( str(tim['min']) )
		self.time_end_la.setText( str(tim['max']) )
		self.time_endbase_la.setText( str(tim['aet']) )
		self.updateUi()
		self.connect(self.makeTx_btn, QtCore.SIGNAL("clicked()"), self.makeTx)

	def makeTx(self):
		"""make tx for all the textures in the mayaFile"""
		for t in self.fil.textures:
			if t.hasTx:
				continue
			t.createVersions()
		self.fillTexturesTable()

	def updateUi(self):
		"""updateUi"""
		self.fillTexturesTable()
		self.fillReferencesTable()
		self.fillCachesTable()

	@property
	def fil(self):
		"""return the file"""
		return self._file

	def fillTexturesTable(self):
		"""add textures from file"""
		color = [QtGui.QColor( "green" ),
				QtGui.QColor( "red" )]
		textures = self.fil.textures
		self.textures_tw.setRowCount( len( textures ) )
		for i,t in enumerate(textures):
			#NAME
			item = QtGui.QTableWidgetItem( t.basename )
			item.setData(32, t )
			self.textures_tw.setItem( i, 0, item )
			#SIZE
			item = QtGui.QTableWidgetItem( "%0.2f MB" %t.size )
			self.textures_tw.setItem( i, 1, item )
			#HASTX
			item = QtGui.QTableWidgetItem( '' )
			if t.hasTx:
				colVal = 0
			else:
				colVal = 1
			item.setBackgroundColor( color[ colVal ])
			self.textures_tw.setItem( i, 2, item )
			#PATH
			item = QtGui.QTableWidgetItem( t.path )
			if t.exists:
				colVal = 0
			else:
				colVal = 1
			item.setBackgroundColor( color[ colVal ])
			self.textures_tw.setItem( i, 3, item )

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
			item.setBackgroundColor( color[ colVal ])
			self.assets_tw.setItem( i, 1, item )

	def fillCachesTable(self):
		"""fill the caches table"""
		caches = self.fil.caches
		self.caches_tw.setRowCount( len( caches ) )
		color = [QtGui.QColor( "green" ),
				QtGui.QColor( "red" )]
		for i,t in enumerate(caches):
			#NAME
			item = QtGui.QTableWidgetItem( t.basename )
			item.setData(32, t )
			self.caches_tw.setItem( i, 0, item )
			#SIZE
			item = QtGui.QTableWidgetItem( str( t.size ) )
			self.caches_tw.setItem( i, 1, item )
			#PATH
			item = QtGui.QTableWidgetItem( t.path )
			if t.exists:
				colVal = 0
			else:
				colVal = 1
			item.setBackgroundColor( color[ colVal ])
			self.caches_tw.setItem( i, 2, item )

class Window(QtGui.QMainWindow):
	def __init__(self):
		QtGui.QMainWindow.__init__(self)
		dia = MayaFilePropertiesUi()
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

