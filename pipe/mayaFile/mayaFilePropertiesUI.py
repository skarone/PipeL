import os

import general.ui.pySideHelper as uiH
reload( uiH )
uiH.set_qt_bindings()
from Qt import QtGui,QtCore

import pipe.project.project   as prj
reload( prj )
import pipe.asset.asset as ass
reload( ass )
import shading.textureManager.textureManager as tm
reload(tm)
import pipe.textureFile.textureFile as tfl
reload(tfl)
try:
	import maya.cmds as mc
except:
	pass
import pipe.settings.settings as sti
reload( sti )
import pipe.asset.asset as ass
reload( ass )
import pipe.project.project as prj
reload( prj )
import pipe.file.file as fl
reload( fl )
import pipe.mayaFile.mayaFile as mfl
reload( mfl )
import general.mayaNode.mayaNode as mn
reload( mn )
import re


PYFILEDIR = os.path.dirname( os.path.abspath( __file__ ) )

uifile = PYFILEDIR + '/mayaFileProperties.ui'
fom, base = uiH.loadUiType( uifile )

class MayaFilePropertiesUi(base, fom):
	"""docstring for ProjectCreator"""
	def __init__(self, fil,parent=uiH.getMayaWindow(), inMaya = True):
		if uiH.USEPYQT:
			super(base, self).__init__(parent)
		else:
			super(MayaFilePropertiesUi, self).__init__(parent)

		self.inMaya = inMaya
		self.setupUi(self)
		self._file = fil
		if fil.exists:
			self.filepath_la.setText( str(fil.path) )
			self.setWindowTitle( str( fil.basename + ' Properties' ) )
			self.filedate_la.setText( str(fil.date))
		self.manager = tm.Manager()
		if inMaya:
			pass
		else:
			tim = fil.time
			self.time_startbase_la.setText( str(tim['ast']) )
			self.time_start_la.setText( str(tim['min']) )
			self.time_end_la.setText( str(tim['max']) )
			self.time_endbase_la.setText( str(tim['aet']) )
		self.updateUi()
		QtCore.QObject.connect( self.searchPath_le, QtCore.SIGNAL( "textEdited (const QString&)" ), self.search )
		QtCore.QObject.connect( self.textures_tw, QtCore.SIGNAL( "itemClicked (QTableWidgetItem *)" ), self.selectNode )
		self.connect(self.moveToFolder_btn, QtCore.SIGNAL("clicked()"), self.moveToFolder)
		self.connect(self.replacePath_btn, QtCore.SIGNAL("clicked()"), self.replacePath)
		self.connect(self.toTx_btn, QtCore.SIGNAL("clicked()"), self.toTx)
		self.connect(self.createVersions_btn, QtCore.SIGNAL("clicked()"), self.createVersions)
		self.connect(self.toPng_btn, QtCore.SIGNAL("clicked()"), self.toPng)
		self.connect(self.renameTexture_btn, QtCore.SIGNAL("clicked()"), self.renameTextures)
		self.connect(self.createTx_btn, QtCore.SIGNAL("clicked()"), self.createTx)
		self.setObjectName( 'MayaFilePropertiesUi' )
		self.settings = sti.Settings()
		gen = self.settings.General
		if gen:
			skin = gen[ "skin" ]
			if skin:
				uiH.loadSkin( self, skin )

	#################
	#TEXTURES

	def selectNode(self, item):
		if uiH.USEPYQT:
			texture = item.data(32).toPyObject()
		else:
			texture = item.data(32)
		if self.inMaya:
			texture()

	def moveToFolder(self):
		"""
		move selected textures to folders if none, move all!
		"""
		textures = self.getSelected()
		folderPath = str(QtGui.QFileDialog.getExistingDirectory(self, "Select Directory"))
		if not folderPath:
			return
		if self.inMaya:
			if textures:
				self.manager.moveToFolder( textures, folderPath )
			else:
				self.manager.moveToFolder( self.manager.textures, folderPath )
		else:
			dataToReplace = []
			for t in textures:
				dataToReplace.append( [ t.dirPath, folderPath ] )
				t.copy( folderPath )
			self.fil.replaceData( dataToReplace )
		self.fillTextures()

	def getSelected(self):
		"""
		get the selected textures
		"""
		#TODO REPLACE TO SUPPORT OUTSIDE MAYA =)
		tab, index = self._getCurrentTab()
		textures = []
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
		if self.inMaya:
			if textures:
				self.manager.toTx( textures )
			else:
				self.manager.allToTx()
		else:
			dataToReplace = []
			for t in textures:
				dataToReplace.append( [ t.path, t.toTx().path ] )
				if not t.hasTx:
					t.makeTx( True )
			self.fil.replaceData( dataToReplace )
		self.fillTextures()

	def createTx(self):
		"""docstring for createTx"""
		textures = self.getSelected()
		if self.inMaya:
			self.manager.createTx( textures )
		else:
			for t in textures:
				if not t.hasTx:
					t.makeTx( True )
		self.fillTextures()

	def createVersions(self):
		"""docstring for createVersions"""
		textures = self.getSelected()
		if self.inMaya:
			self.manager.createVersions( textures )
		else:
			for t in textures:
				t.createVersions()

	def toPng(self):
		textures = self.getSelected()
		if self.inMaya:
			if textures:
				self.manager.toPng( textures )
			else:
				self.manager.allToPng()
		else:
			dataToReplace = []
			for t in textures:
				dataToReplace.append( [ t.path, t.toPng().path ] )
			self.fil.replaceData( dataToReplace )
		self.fillTextures()

	def renameTextures(self):
		"""rename selected Textures"""
		textures = self.getSelected()
		if self.inMaya:
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

	def fillTextures(self):
		"""add textures from file"""
		color = [QtGui.QColor( "green" ),
				QtGui.QColor( "red" )]
		if self.inMaya:
			textures = self.manager.textures
		else:
			textures = self.fil.textures
		self.textures_tw.setRowCount( len( textures ) )
		for i,t in enumerate(textures):
			if self.inMaya:
				if t.type == 'aiImage':
					attr = "filename"
				else:
					attr = "ftn"
				f = tfl.textureFile( t.attr( attr ).v )
			else:
				f = t
			#NAME
			item = QtGui.QTableWidgetItem( f.basename )
			item.setCheckState(QtCore.Qt.Unchecked )
			item.setData(32, t )
			self.textures_tw.setItem( i, 0, item )
			#SIZE
			if not f.exists:
				item = QtGui.QTableWidgetItem( "0 MB" )
			else:
				item = QtGui.QTableWidgetItem( "%0.2f MB" %f.size )
			self.textures_tw.setItem( i, 1, item )
			#HASTX
			item = QtGui.QTableWidgetItem( '' )
			colVal = 1
			if f.hasTx:
				if f.exists and f.exists:
					if f.toTx().isOlderThan(f):
						colVal = 1
				else:
					colVal = 0
			else:
				colVal = 1
			if uiH.USEPYQT:
				item.setBackgroundColor(  color[ colVal ])
			else:
				item.setBackground(  color[ colVal ] )
			self.textures_tw.setItem( i, 2, item )
			#PATH
			item = QtGui.QTableWidgetItem( f.path )
			if f.exists:
				colVal = 0
			else:
				colVal = 1
			if uiH.USEPYQT:
				item.setBackgroundColor(  color[ colVal ])
			else:
				item.setBackground(  color[ colVal ] )
			self.textures_tw.setItem( i, 3, item )

	#
	#################

	def replacePath(self):
		tab, index = self._getCurrentTab()
		textures = self.getSelected()
		searchAndReplace = [str(self.searchPath_le.text()),str(self.replacePath_le.text())]
		if index == 0:
			if self.inMaya:
				if textures:
					self.manager.replacePath( textures, searchAndReplace )
				else:
					self.manager.replacePath( self.manager.textures, searchAndReplace )
			else:
				self.fil.changeTextures( srchAndRep = searchAndReplace )
			self.fillTextures()
		elif index == 1:
			if self.inMaya:
				for t in textures:
					rfn = mc.referenceQuery( t.path, rfn = True )
					mc.file( t.path.replace( searchAndReplace[0],searchAndReplace[1]), loadReference = rfn, type = "mayaAscii", options = "v=0" )
			else:
				self.fil.changeReferences( srchAndRep = searchAndReplace )
			self.fillReferencesTable()
		elif index == 2:
			if self.inMaya:
				for t in textures:
					for al in mn.ls( typ = 'AlembicNode' ):
						if t.path == al.a.abc_File.v:
							al.a.abc_File.v = t.path.replace( searchAndReplace[0],searchAndReplace[1] )
							break
			else:
				self.fil.changeCaches( srchAndRep = searchAndReplace )
			self.fillCachesTable()

	def updateUi(self):
		"""updateUi"""
		self.fillTextures()
		self.fillReferencesTable()
		self.fillCachesTable()

	def _getCurrentTab(self):
		"""return the visible table in the ui"""
		currentTab = self.tabWidget.currentIndex()
		if currentTab == 0:
			tabwid = self.textures_tw
		elif currentTab == 1:
			tabwid = self.assets_tw
		elif currentTab == 2:
			tabwid = self.caches_tw
		return tabwid, currentTab

	def search(self, fil):
		"""search asset based on line edit string"""
		#fil = self.search_asset_le.text()
		tabs = [ self.textures_tw, self.assets_tw, self.caches_tw ]
		for tab in tabs:
			for i in range( tab.rowCount() ):
				match = False
				for j in range( tab.columnCount() ):
					item = tab.item( i, j )
					if fil in str( item.text() ):
						match = True
						break
				tab.setRowHidden( i, not match )

	@property
	def fil(self):
		"""return the file"""
		return self._file

	def fillReferencesTable(self):
		"""fill the references table"""
		if self.inMaya:
			references = []
			sel = mc.ls( rf = True )
			for s in sel:
				try:
					references.append( mfl.mayaFile( mc.referenceQuery( s, f = True ) ))
				except:
					continue
		else:
			references = self.fil.references
		self.assets_tw.setRowCount( len( references ) )
		color = [QtGui.QColor( "green" ),QtGui.QColor( "red" )]
		for i,t in enumerate(references):
			item = QtGui.QTableWidgetItem( t.basename )
			item.setData(32, t )
			self.assets_tw.setItem( i, 0, item )
			area = t.basename.split( '_' )[-1]
			item = QtGui.QTableWidgetItem( area )
			self.assets_tw.setItem( i, 1, item )
			needs = 'No'
			if 'Shot' in t.path:
				origFile = mfl.mayaFile( re.sub(r'Sequences[^)]*Assets', 'Assets', t.path) )
				if t.isOlderThan( origFile ):
					needs = 'Yes'
			item = QtGui.QTableWidgetItem( needs )
			self.assets_tw.setItem( i, 2, item )
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
			self.assets_tw.setItem( i, 3, item )

	def fillCachesTable(self):
		"""fill the caches table"""
		if self.inMaya:
			caches = []
			for a in mn.ls( typ = 'AlembicNode' ):
				caches.append( fl.File( a.a.abc_File.v ) )
		else:
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
			if uiH.USEPYQT:
				item.setBackgroundColor(  color[ colVal ])
			else:
				item.setBackground(  color[ colVal ] )
			self.caches_tw.setItem( i, 2, item )

class Window(QtGui.QMainWindow):
	def __init__(self):
		QtGui.QMainWindow.__init__(self)
		dia = MayaFilePropertiesUi()
		dia.exec_()
	
def main():
	"""use this to create project in maya"""
	if mc.window( 'MayaFilePropertiesUi', q = 1, ex = 1 ):
		mc.deleteUI( 'MayaFilePropertiesUi' )
	PyForm=MayaFilePropertiesUi(mfl.currentFile(), inMaya = True )
	PyForm.show()


if __name__=="__main__":
	import sys
	a = QtGui.QApplication(sys.argv)
	global PyForm
	a.setStyle('plastique')
	PyForm=Window()
	PyForm.show()
	sys.exit(a.exec_())

