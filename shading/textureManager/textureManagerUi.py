import os

import general.ui.pySideHelper as uiH
reload( uiH )
uiH.set_qt_bindings()
from Qt import QtGui,QtCore

import shading.textureManager.textureManager as tm
reload(tm)
import pipe.textureFile.textureFile as tfl
reload(tfl)
import maya.cmds as mc
import pipe.settings.settings as sti
reload( sti )


#load UI FILE
PYFILEDIR = os.path.dirname( os.path.abspath( __file__ ) )

uifile = PYFILEDIR + '/textureManager.ui'
fom, base = uiH.loadUiType( uifile )

class ManagerUI(base,fom):
	"""manager ui class"""
	def __init__(self, parent  = uiH.getMayaWindow(), *args):
		if uiH.USEPYQT:
			super(base, self).__init__(parent)
		else:
			super(ManagerUI, self).__init__(parent)
		self.setupUi(self)
		self._makeConnections()
		self.manager = tm.Manager()
		self.fillTextures()
		self.setObjectName( 'textureManager_WIN' )
		self.settings = sti.Settings()
		gen = self.settings.General
		
		if gen:
			skin = gen[ "skin" ]
			if skin:
				uiH.loadSkin( self, skin )

	def _makeConnections(self):
		QtCore.QObject.connect( self.searchPath_le, QtCore.SIGNAL( "textEdited (const QString&)" ), self.searchTexture )
		QtCore.QObject.connect( self.textures_tw, QtCore.SIGNAL( "itemClicked (QTableWidgetItem *)" ), self.selectNode )
		self.connect(self.moveToFolder_btn, QtCore.SIGNAL("clicked()"), self.moveToFolder)
		self.connect(self.toHigh_btn, QtCore.SIGNAL("clicked()"), self.toHigh)
		self.connect(self.toLow_btn, QtCore.SIGNAL("clicked()"), self.toLow)
		self.connect(self.toMid_btn, QtCore.SIGNAL("clicked()"), self.toMid)
		self.connect(self.replacePath_btn, QtCore.SIGNAL("clicked()"), self.replacePath)
		self.connect(self.toTx_btn, QtCore.SIGNAL("clicked()"), self.toTx)
		self.connect(self.createVersions_btn, QtCore.SIGNAL("clicked()"), self.createVersions)
		self.connect(self.toPng_btn, QtCore.SIGNAL("clicked()"), self.toPng)
		self.connect(self.refresh_btn, QtCore.SIGNAL("clicked()"), self.fillTextures)
		self.connect(self.renameTexture_btn, QtCore.SIGNAL("clicked()"), self.renameTextures)
		self.connect(self.createTx_btn, QtCore.SIGNAL("clicked()"), self.createTx)

	def toHigh(self):
		"""docstring for toHigh"""
		textures = self.getSelected()
		self.manager.toHigh( textures )

	def toMid(self):
		"""docstring for toMid"""
		textures = self.getSelected()
		self.manager.toMid( textures )

	def toLow(self):
		"""docstring for toLow"""
		textures = self.getSelected()
		self.manager.toLow( textures )

	def moveToFolder(self):
		"""
		move selected textures to folders if none, move all!
		"""
		textures = self.getSelected()
		folderPath = str(QtGui.QFileDialog.getExistingDirectory(self, "Select Directory"))
		print folderPath
		if not folderPath:
			return
		if textures:
			self.manager.moveToFolder( textures, folderPath )
		else:
			self.manager.moveToFolder( self.manager.textures, folderPath )
		self.fillTextures()

	def selectNode(self, item):
		if uiH.USEPYQT:
			texture = item.data(32).toPyObject()
		else:
			texture = item.data(32)
		texture()

	def getSelected(self):
		"""
		get the selected textures
		"""
		textures = []
		tab = self.textures_tw
		for r in range( tab.rowCount() ):
			for c in range( tab.columnCount() ):
				item = tab.item( r, c )
				if item.checkState() == 2:
					if uiH.USEPYQT:
						textures.append( item.data(32).toPyObject())
					else:
						textures.append( item.data(32))
		if not textures:
			for r in range( tab.rowCount() ):
				if tab.isRowHidden( r ):
					continue
				item = tab.item( r, 0 )
				if uiH.USEPYQT:
					textures.append( item.data(32).toPyObject() )
				else:
					textures.append( item.data(32) )
		return textures

	def toTx(self):
		textures = self.getSelected()
		if textures:
			self.manager.toTx( textures )
		else:
			self.manager.allToTx()
		self.fillTextures()

	def createTx(self):
		"""docstring for createTx"""
		textures = self.getSelected()
		self.manager.createTx( textures )
		self.fillTextures()

	def createVersions(self):
		"""docstring for createVersions"""
		textures = self.getSelected()
		self.manager.createVersions( textures )
		self.fillTextures()

	def toPng(self):
		textures = self.getSelected()
		if textures:
			self.manager.toPng( textures )
		else:
			self.manager.allToPng()
		self.fillTextures()

	def replacePath(self):
		textures = self.getSelected()
		searchAndReplace = [str(self.searchPath_le.text()),str(self.replacePath_le.text())]
		if textures:
			self.manager.replacePath( textures, searchAndReplace )
		else:
			self.manager.replacePath( self.manager.textures, searchAndReplace )
		self.fillTextures()

	def fillTextures(self):
		"""
		fill the tw with the textures of the scene
		"""
		color = [QtGui.QColor( "green" ),
				QtGui.QColor( "red" )]
		textures = self.manager.textures
		if not textures:
			return
		self.textures_tw.clearContents()
		self.textures_tw.setRowCount( len( textures ) )
		for i,t in enumerate(textures):
			if t.type == 'aiImage':
				attr = "filename"
			else:
				attr = "ftn"
			f = tfl.textureFile( t.attr( attr ).v )
			#NAME
			item = QtGui.QTableWidgetItem( t.name )
			item.setCheckState(QtCore.Qt.Unchecked )
			item.setData(32, t )
			self.textures_tw.setItem( i, 0, item )
			#SIZE
			if not f.exists:
				item = QtGui.QTableWidgetItem( "0 MB" )
			else:
				if f.hasUdim:
					item = QtGui.QTableWidgetItem( "UDIM")
				else:
					item = QtGui.QTableWidgetItem( "%0.2f MB" %f.size )
			self.textures_tw.setItem( i, 1, item )
			#HASTX
			item = QtGui.QTableWidgetItem( '' )
			if f.exists:
				if not f.hasUdim:
					if f.hasTx:
						if f.toTx().isOlderThan(f):
							colVal = 1
						else:
							colVal = 0
					else:
						colVal = 1
				else:
					colVal = 1
			else:
				colVal = 1
			if uiH.USEPYQT:
				item.setBackgroundColor( color[ colVal ])
			else:
				item.setBackground( color[ colVal ] )
			self.textures_tw.setItem( i, 2, item )
			#PATH
			item = QtGui.QTableWidgetItem( f.path )
			if f.exists:
				colVal = 0
			else:
				colVal = 1
			if uiH.USEPYQT:
				item.setBackgroundColor( color[ colVal ])
			else:
				item.setBackground( color[ colVal ] )
			self.textures_tw.setItem( i, 3, item )

	def searchTexture(self, fil):
		"""search asset based on line edit string"""
		#fil = self.search_asset_le.text()
		for i in range( self.textures_tw.rowCount() ):
			match = False
			for j in range( self.textures_tw.columnCount() ):
				item = self.textures_tw.item( i, j )
				if fil in str( item.text() ):
					match = True
					break
			self.textures_tw.setRowHidden( i, not match )

	def renameTextures(self):
		"""rename selected Textures"""
		textures = self.getSelected()
		for t in textures:
			if t.type == 'aiImage':
				attr = "filename"
			else:
				attr = "ftn"
			f = tfl.textureFile( t.attr( attr ).v )
			result = mc.promptDialog(
					title         = 'Rename Texture ' + f.name,
					message       = 'Enter New Name:',
					button        = ['OK', 'Cancel','Stop'],
					defaultButton = 'OK',
					tx            = f.name,
					cancelButton  = 'Cancel',
					dismissString = 'Cancel')
			if result == 'OK':
				newName = mc.promptDialog(query=True, text=True)
				self.manager.renameTexture( t, newName )
			elif result == 'Stop':
				return
		self.fillTextures()

class Window(QtGui.QMainWindow):
	def __init__(self):
		QtGui.QMainWindow.__init__(self)
		dia = MultiAttributeUI()
		dia.exec_()

def main():
	"""use this to create project in maya"""
	if mc.window( 'textureManager_WIN', q = 1, ex = 1 ):
		mc.deleteUI( 'textureManager_WIN' )
	PyForm=ManagerUI()
	PyForm.show()
