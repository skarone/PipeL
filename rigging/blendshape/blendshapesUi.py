import os

import general.ui.pySideHelper as uiH
reload( uiH )

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

	def targetsOff(self):
		"""docstring for targetsOff"""
		for s in range( self.targets_lw.count() ):
			mn.Node( self.targets_lw.item( s).text() ).a.v.v = 0

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
		self.targetsOff()
		self.selTargets[0].a.v.v = 1
		utl.isolate( self.selTargets[0].name )

	def doneEdit(self):
		"""docstring for doneEdit"""
		utl.desIsolate()
		self.targetsOff()

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
		for n in mn.ls( sl = True ):
			item = QtGui.QListWidgetItem( n.name )
			item.setData(32, n )
			self.meshes_lw.addItem( item )

	def insMesh(self):
		"""clean list and add selected meshes"""
		self.meshes_lw.clear()
		self.addMeshToList()

	def remMesh(self):
		"""remove selected meshes from list Mirror"""
		for s in self.meshes_lw.selectedItems():
			self.meshes_lw.removeItemWidget( s )

	def addVert(self):
		"""add selected vertecies from list vert"""
		for n in mn.ls( sl = True, fl = True ):
			item = QtGui.QListWidgetItem( n.name )
			self.vertex_lw.addItem( item )

	def insVert(self):
		"""clean list vert and add selected verticies"""
		self.vertex_lw.clear()
		self.addVert()

	def remVert(self):
		"""remove selected verteces from list"""
		for s in self.vertex_lw.selectedItems():
			self.vertex_lw.removeItemWidget( s )

	def getSearchAndReplace(self):
		"""return search and replace strings"""
		return [str( self.search_le.text() ), str( self.replace_le.text() )]

	def getSelectedAxis(self):
		"""return the selected axis in the ui"""
		qvbl = self.groupBox.layout()
		for r in [ self.xAxis_rb, self.yAxis_rb, self.zAxis_rb]:
			if r.isChecked():
				return str( r.text() )

	def getVertexList(self):
		"""return the vertex list """
		verts = []
		for v in range( self.vertex_lw.count() ):
			verts.append( str( self.vertex_lw.item(v).text() ))
		return verts

	def reflect(self):
		"""reflect selected meshes with the vertecies in the list, if no verticies reflect all"""
		base = bls.BlendShapeMesh( str( self.baseMesh ), str( self.baseMesh ) )
		axis = self.getSelectedAxis()
		vtexList = self.getVertexList()
		reflectionTable = {}
		base.createReflectionTable( axis, vtexList )
		reflectionTable = base.reflectionVertexTable
		print reflectionTable 
		srcAndRep = self.getSearchAndReplace()
		for s in range( self.meshes_lw.count() ):
			node = str( self.meshes_lw.item(s ).text())
			newNode = mn.Node( node ).duplicate( node.replace( srcAndRep[0], srcAndRep[1] ) )
			bl = bls.BlendShapeMesh( newNode.name, str( self.baseMesh ),reflectionTable )
			print vtexList
			bl.reflect( axis, vtexList )

	def mirror(self):
		"""mirror selected meshes with the vertecies in the list, if no verticies mirror all"""
		base = bls.BlendShapeMesh( str( self.baseMesh ), str( self.baseMesh ) )
		axis = self.getSelectedAxis()
		vtexList = self.getVertexList()
		reflectionTable = {}
		base.createReflectionTable( axis, vtexList )
		reflectionTable = base.reflectionVertexTable
		srcAndRep = self.getSearchAndReplace()
		for s in range( self.meshes_lw.count() ):
			node = str( self.meshes_lw.item(s ).text())
			newNode = mn.Node( node ).duplicate( node.replace( srcAndRep[0], srcAndRep[1] ) )
			bl = bls.BlendShapeMesh( newNode.name, str( self.baseMesh ), reflectionTable )
			bl.mirror( axis, vtexList )

	def asBase(self):
		"""set verteces asBase mesh for meshes in list with the vertecies in the list, if no verticies in list, set all asBasemesh all"""
		vtexList = self.getVertexList()
		for s in range( self.meshes_lw.count() ):
			bl = bls.BlendShapeMesh( str( self.meshes_lw.item(s ).text()), str( self.baseMesh )  )
			bl.asBase( vtexList )

def main():
	"""use this to create project in maya"""
	if mc.window( 'BlendShapeUI', q = 1, ex = 1 ):
		mc.deleteUI( 'BlendShapeUI' )
	PyForm=BlendShapeUI()
	PyForm.show()

