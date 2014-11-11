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
			super(ManagerUI, self).__init__(parent)
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
		QtCore.QObject.connect( self.searchMesh_le, QtCore.SIGNAL( "textEdited (const QString&)" ), self.searchMesh )
		QtCore.QObject.connect( self.targets_lw, QtCore.SIGNAL( "itemClicked( QListWidgetItem* )" ), self.selectTarget )
		self.connect(self.Create_btn, QtCore.SIGNAL("clicked()"), self.create)
		self.connect(self.baseMesh_btn, QtCore.SIGNAL("clicked()"), self.setBaseMesh)
		self.connect(self.new_btn, QtCore.SIGNAL("clicked()"), self.newMesh)
		self.connect(self.edit_btn, QtCore.SIGNAL("clicked()"), self.editMesh)
		self.connect(self.doneEdit_btn, QtCore.SIGNAL("clicked()"), self.doneEdit)
		self.connect(self.delete_btn, QtCore.SIGNAL("clicked()"), self.deleteMesh)
		self.connect(self.paint_btn, QtCore.SIGNAL("clicked()"), self.paint)
		self.connect(self.corrective_btn, QtCore.SIGNAL("clicked()"), self.corrective)
		#MIRROR
		self.connect(self.addMesh_btn, QtCore.SIGNAL("clicked()"), self.addMesh)
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
		pass

	@property
	def baseMesh(self):
		"""return base Mesh"""
		val = str( self.baseMesh_le.Text())
		return mn.Node( val )

	@property
	def selBlend(self):
		"""return selected blendshape from cmb"""
		return bls.BlendShapeNode( str( self.blends_cmb.currentText()) )

	@property
	def selTargets(self):
		"""return selected targets from list"""
		return [ bls.BlendShapeMesh(s.text()) for s in self.targets_lw.selectedItems()]

	def setBaseMesh(self):
		"""set base mesh based on selection"""
		sel = mc.ls( sl = True )
		self.baseMesh_le.setText( sel[0] )
		self.updateUi()

	def updateUi(self):
		"""update UI based on baseMesh"""
		blends = mc.ls( mc.defaultNavigation( ren = True, d = self.baseMesh.shape.name ), typ = 'blendShape' )
		self.blends_cmb.clear()
		self.blends_cmb.addItems( blends )

	def updateTargets(self):
		"""update Targets list based on cmb selected"""
		self.targets_lw.clear()
		for i,s in enumerate( self.selBlend.meshes ):
			item = QtGui.QListWidgetItem( s.name )
			item.setData(32, s )
			self.targets_lw.setItem( i, item )
			
	def selectTarget(self):
		"""select Targets"""
		sel = mn.Nodes( [ s.name for s in self.selTargets ] )
		sel.select()

	def searchMesh(self):
		"""filter targets tree based on search"""
		pass

	def newMesh(self):
		"""create a new mesh for the blendshape and editit"""
		pass

	def editMesh(self):
		"""show selected mesh to edit"""
		self.selTargets[0].a.v.v = 1
		self.selTargets[0].isolate()

	def doneEdit(self):
		"""docstring for doneEdit"""
		utl.desIsolate()
		self.selTargets[0].a.v.v = 1

	def deleteMesh(self):
		"""delete selected meshes from blendshape"""
		pass

	def paint(self):
		"""paint weights for selected mesh"""
		pass

	def corrective(self):
		"""create corrective blend for 2 selected meshes"""
		pass

	#MIRROR
	def addMesh(self):
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
	PyForm=ManagerUI()
	PyForm.show()

