import os

import general.ui.pySideHelper as uiH
reload( uiH )
uiH.set_qt_bindings()
from Qt import QtGui,QtCore

import pipe.settings.settings as sti
reload( sti )

import rigging.blendshape.blendshape as bls
reload( bls )

import maya.cmds as mc
import general.mayaNode.mayaNode as mn
reload( mn )
import maya.mel as mm

#load UI FILE
PYFILEDIR = os.path.dirname( os.path.abspath( __file__ ) )

uifile = PYFILEDIR + '/blendshape.ui'
fom, base = uiH.loadUiType( uifile )

import general.utils.utils as utl
reload( utl )


class BlendShapeUI(base,fom):
	"""manager ui class"""
	def __init__(self, parent  = uiH.getMayaWindow(), *args):
		if uiH.USEPYQT:
			super(base, self).__init__(parent)
		else:
			super(BlendShapeUI, self).__init__(parent)
		self.setupUi(self)
		self.setObjectName( 'BlendShapeUI' )
		self.settings = sti.Settings()
		gen = self.settings.General
		self.makeConnections()
		if gen:
			skin = gen[ "skin" ]
			if skin:
				uiH.loadSkin( self, skin )

	def makeConnections(self):
		"""docstring for makeConnections"""
		QtCore.QObject.connect( self.blends_cmb, QtCore.SIGNAL( "activated( const QString& )" ), self.updateTargets )
		QtCore.QObject.connect( self.searchMesh_le, QtCore.SIGNAL( "textChanged (const QString&)" ), self.searchMesh )
		QtCore.QObject.connect( self.searchMesh_le, QtCore.SIGNAL( "textEdited (const QString&)" ), self.searchMesh )
		QtCore.QObject.connect( self.targets_lw, QtCore.SIGNAL( "itemClicked( QListWidgetItem* )" ), self.selectTarget )
		QtCore.QObject.connect( self.base_sl, QtCore.SIGNAL( "valueChanged( int )"), self.changeValue )
		self.connect(self.Create_btn, QtCore.SIGNAL("clicked()"), self.create)
		self.connect(self.baseMesh_btn, QtCore.SIGNAL("clicked()"), self.setBaseMesh)
		self.connect(self.new_btn, QtCore.SIGNAL("clicked()"), self.newMesh)
		self.connect(self.add_btn, QtCore.SIGNAL("clicked()"), self.addMesh)
		self.connect(self.edit_btn, QtCore.SIGNAL("clicked()"), self.editMesh)
		self.connect(self.doneEdit_btn, QtCore.SIGNAL("clicked()"), self.doneEdit)
		self.connect(self.delete_btn, QtCore.SIGNAL("clicked()"), self.deleteMesh)
		self.connect(self.paint_btn, QtCore.SIGNAL("clicked()"), self.paint)
		self.connect(self.corrective_btn, QtCore.SIGNAL("clicked()"), self.corrective)
		#MIRROR
		self.connect(self.addMesh_btn, QtCore.SIGNAL("clicked()"), self.addMeshToList)
		self.connect(self.insMesh_btn, QtCore.SIGNAL("clicked()"), self.insMesh)
		self.connect(self.remMesh_btn, QtCore.SIGNAL("clicked()"), self.remMesh)
		self.connect(self.addVert_btn, QtCore.SIGNAL("clicked()"), self.addVert)
		self.connect(self.insVert_btn, QtCore.SIGNAL("clicked()"), self.insVert)
		self.connect(self.remVert_btn, QtCore.SIGNAL("clicked()"), self.remVert)
		self.connect(self.reflect_btn, QtCore.SIGNAL("clicked()"), self.reflect)
		self.connect(self.mirror_btn, QtCore.SIGNAL("clicked()"), self.mirror)
		self.connect(self.asBase_btn, QtCore.SIGNAL("clicked()"), self.asBase)

	def create(self):
		"""docstring for create"""
		#ask for blendshape name
		name, ok = QtGui.QInputDialog.getText(self, 'New Mesh', 'New Blendshape Mesh:')
		if ok:
			bls.BlendShapeNode( str( name ) ).create( [], self.baseMesh.name )
			self.updateUi()

	@property
	def baseMesh(self):
		"""return base Mesh"""
		val = str( self.baseMesh_le.text())
		return mn.Node( val )

	@property
	def selBlend(self):
		"""return selected blendshape from cmb"""
		blendName = str( self.blends_cmb.currentText())
		if blendName:
			return bls.BlendShapeNode( str( self.blends_cmb.currentText()) )
		return None

	@property
	def selTargets(self):
		"""return selected targets from list"""
		return [ bls.BlendShapeMesh(s.text(), self.baseMesh ) for s in self.targets_lw.selectedItems()]

	def setBaseMesh(self):
		"""set base mesh based on selection"""
		sel = mc.ls( sl = True )
		self.baseMesh_le.setText( sel[0] )
		self.updateUi()

	def updateUi(self):
		"""update UI based on baseMesh"""
		blends = mc.ls( mc.defaultNavigation( ren = True, d = self.baseMesh.shape.name ), typ = 'blendShape' )
		self.blends_cmb.clear()
		if blends:
			self.blends_cmb.addItems( blends )
		self.updateTargets()

	def updateTargets(self):
		"""update Targets list based on cmb selected"""
		self.targets_lw.clear()
		if not self.selBlend:
			return
		meshes = self.selBlend.meshes
		if not meshes:
			return
		for i,s in enumerate( meshes ):
			if 'dummy' in s.name:
				s = bls.BlendShapeMesh( s.name.replace( 'dummy', 'corrective' ), self.baseMesh )
			item = QtGui.QListWidgetItem( s.name )
			item.setData(32, s )
			self.targets_lw.addItem( item )

	def changeValue(self, value):
		"""set value for selected targets"""
		for s in self.selTargets:
			self.selBlend.attr( s.name ).v = (value/100.0)
			
	def selectTarget(self):
		"""select Targets"""
		sel = mn.Nodes( [ s.name for s in self.selTargets ] )
		sel.select()

	def searchMesh(self, fil):
		"""filter targets tree based on search"""
		#fil = self.search_asset_le.text()
		print self.targets_lw.count()
		for i in range( self.targets_lw.count() ):
			match = True
			item = self.targets_lw.item( i )
			print item.text()
			if fil in str( item.text() ):
				match = False
			item.setHidden( match)

	def newMesh(self):
		"""create a new mesh for the blendshape and editit"""
		self.selBlend.a.envelope.v = 0
		#ask new name
		newName, ok = QtGui.QInputDialog.getText(self, 'New Mesh', 'New Blendshape Mesh:')
		if ok:
			newName = str( newName )
			self.baseMesh.duplicate( newName )
			self.selBlend.addMesh( newName )
			#add and select new mesh in targets list
			item = QtGui.QListWidgetItem( newName )
			item.setData(32, bls.BlendShapeMesh( newName, self.baseMesh) )
			self.targets_lw.addItem( item )
			self.targets_lw.clearSelection()
			self.targets_lw.setCurrentItem( item )
			self.editMesh()
		self.selBlend.a.envelope.v = 1

	def addMesh(self):
		"""add selected meshes to current blendNode"""
		for s in mn.ls(sl = True):
			self.selBlend.addMesh( s )
		self.updateTargets()

	def editMesh(self):
		"""show selected mesh to edit"""
		self.selTargets[0].a.v.v = 1
		utl.isolate( self.selTargets[0].name )

	def doneEdit(self):
		"""docstring for doneEdit"""
		utl.desIsolate()
		self.selTargets[0].a.v.v = 0

	def deleteMesh(self):
		"""delete selected meshes from blendshape"""
		for s in self.selTargets:
			if 'corrective' in s.name:
				s.delete()
				s = bls.BlendShapeMesh(s.name.replace( 'corrective', 'dummy' ), self.baseMesh )
			self.selBlend.removeMesh( s.name )
			s.delete()
		self.updateTargets()

	def paint(self):
		"""paint weights for selected mesh"""
		self.baseMesh()
		mc.ArtPaintBlendShapeWeightsTool()
		mc.textScrollList('blendShapeTargetList',e = True, si = self.selTargets[0].name )
		mm.eval( 'artBlendShapeSelectTarget artAttrCtx "";')

	def corrective(self):
		"""create corrective blend for 2 selected meshes"""
		dummy, corrective = self.selBlend.makeCorrectiveBlend( self.selTargets[0].name, self.selTargets[1].name )
		dummy.a.v.v = 0
		self.updateTargets()
		item = self.targets_lw.findItems( corrective.name, QtCore.Qt.MatchExactly )
		self.targets_lw.clearSelection()
		self.targets_lw.setCurrentItem( item[0] )
		corrective.a.v.v = 0
		self.editMesh()

	#MIRROR
	def addMeshToList(self):
		"""add Mesh to meshes to mirror/reflect"""
		pass

	def insMesh(self):
		"""clean list and add selected meshes"""
		pass

	def remMesh(self):
		"""remove selected meshes from list Mirror"""
		pass

	def addVert(self):
		"""add selected vertecies from list vert"""
		pass

	def insVert(self):
		"""clean list vert and add selected verticies"""
		pass

	def remVert(self):
		"""remove selected verteces from list"""
		pass

	def reflect(self):
		"""reflect selected meshes with the vertecies in the list, if no verticies reflect all"""
		pass

	def mirror(self):
		"""mirror selected meshes with the vertecies in the list, if no verticies mirror all"""
		pass

	def asBase(self):
		"""set verteces asBase mesh for meshes in list with the vertecies in the list, if no verticies in list, set all asBasemesh all"""
		pass


def main():
	"""use this to create project in maya"""
	if mc.window( 'BlendShapeUI', q = 1, ex = 1 ):
		mc.deleteUI( 'BlendShapeUI' )
	PyForm=BlendShapeUI()
	PyForm.show()

