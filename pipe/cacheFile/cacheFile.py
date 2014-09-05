try:
	import maya.cmds as mc
except:
	pass
import general.mayaNode.mayaNode as mn
import general.reference.reference as rf
import pipe.file.file as fl
"""
Exportar alembic... al parecer tengo que importar (La referencia no sirve, porque cambia el nombre del shape) el archivo de shading y hacer un blendshape en world con el rig..., la solucion es hacer que siempre los nombres esten bien ... hacer un check de escena
y exportar directamente el sha...


import pipe.cacheFile.cacheFile as cfl
reload( cfl )
import pipe.asset.asset as ass
import pipe.project.project as prj
cac = cfl.CacheFile( r'P:\Pony_Halloween_Fantasmas\Maya\Sequences\Terror\Shots\s002_T02\Pool\Anim\Chico_01_RIG.abc' )

cac.importForAsset2( ass.Asset( 'Chico_01', prj.Project( 'Pony_Halloween_Fantasmas' ) ), customNamespace = cac.name )

"""
def createBlendshape( replace = [ 'Rig', 'Final' ]):
	"""create blendshape between RIG and FINAL
	FINAL allways is the render asset"""
	sel = mn.ls( sl = True, s = True, dag = True, ni = True )
	if sel:
		sel = mn.ls( sel[0].name[:sel[0].name.rindex(':')] + ':*', dag = True, ni = True, typ = 'mesh' )
	for r in sel:
		rSha = mn.Node( r.name.replace( replace[0], replace[1] ) )
		blend = mc.blendShape( r.name, rSha.name, o = 'world' )[0]
		mc.blendShape( blend, edit=True, w=[(0, 1)] )

class CacheFile(fl.File):
	"""custom cache file, to handles caches for maya"""
	def __init__( self, path, nodes = None ):
		super(CacheFile, self).__init__( path )
		if nodes:
			self._nodes = mn.ls( nodes, s = True, dag = True, ni = True )
		else:
			self._nodes = None
	
	@property
	def nodes(self):
		"""return the nodes for the cache"""
		return self._nodes

	def export(self, fr = None, asset = None ):
		"""export cache for selected file"""
		if self.exists:
			super(CacheFile, self).newVersion()
		cmd = '-f ' + self.path + ' -uv -ro '
		if self.nodes:
			if asset:
				sel = mn.ls( self.nodes[0].name[:self.nodes[0].name.rindex(':')] + ':*', dag = True, ni = True, typ = 'mesh' )
			sel.select()
			cmd += '-sl '
		if not fr:
			#get frame range from timeslider
			start = mc.playbackOptions(q = True, min = True )
			end   = mc.playbackOptions(q = True, max = True )
			cmd += '-fr ' + str( start ) + ' ' + str( end )
		print cmd
		mc.refresh( su = True )
		mc.AbcExport( j = cmd )
		mc.refresh( su = False )

	def exportAsset(self, asset, importFinal = False):
		"""export all the geometry for the selected asset"""
		#get asset..
		#import asset for render
		if importFinal:
			self._nodes = asset.shadingPath.imp(  )
			#create blendshape between rig and render assets
			createBlendshape()
		#export cache
		self.export( fr = None, asset = asset )

	def imp( self, **args ):
		"""import cache to scene"""
		cmd = '"' + self.path + '",'
		for a in args.keys():
			val = args[a]
			if isinstance(val, str):
				cmd += a + '="' + args[a] + '",'
			else:
				cmd += a + '=' + str( args[a] ) + ','
		finalCmd = "mc.AbcImport(" + cmd + ")"
		abcNode = mn.Node( eval( "mc.AbcImport(" + cmd + ")" ) )
		return abcNode

	def importForAsset(self, asset, customNamespace = None, referenceAsset = True ):
		"""import cache and assign to asset"""
		#reference render asset
		#connect cache to objects
		if referenceAsset:
			nodes = asset.shadingPath.reference( customNamespace )
			mshs = mn.ls( nodes, typ = 'mesh', ni = True, l = True )
		else:
			nodes = asset.shadingPath.imp( customNamespace )
			if nodes:
				print nodes
				mshs = mn.ls( nodes, typ = 'mesh', ni = True, l = True )
			else:
				mshs = mn.ls( customNamespace + ':*', typ = 'mesh', ni = True, l = True )
			#filter meshes
		mshs.select()
		abcNode = self.imp( mode = 'import', connect = "/", createIfNotFound = True )
		"""
		#reconnect via polyTransfer so we can use the original uvs from shape
		attrs = abcNode.listAttr( c = True, m = True, ro = True, hd = True )
		for a in attrs:
			out = a.output
			if not out:
				continue
			for o in out:
				midMesh = mn.createNode( 'mesh' )
				midMesh.a.intermediateObject.v = 1
				polyTrans = mn.createNode( 'polyTransfer' )
				polyTrans.a.vertices.v = 1
				polyTrans.a.uvSets.v = 0
				a >> polyTrans.a.otherPoly
				midMesh.a.outMesh >> polyTrans.a.inputPolymesh
				o.node.a.outMesh >> midMesh.a.inMesh
				polyTrans.a.output >> o
		nodes[0]()
		rf.reloadSelected()
		"""


	def importForAsset2(self, asset, customNamespace = None ):
		"""import cache and assign to asset"""
		#reference render asset
		#connect cache to objects
		nodes = asset.shadingPath.reference( customNamespace )
		#filter meshes
		mshs = mn.ls( nodes, typ = 'mesh', ni = True, l = True )
		mshs.select()
		abcNode = self.imp( mode = 'import', connect = "/", createIfNotFound = True )
		#reconnect via polyTransfer so we can use the original uvs from shape
		attrs = abcNode.listAttr( c = True, m = True, ro = True, hd = True )
		for a in attrs:
			out = a.output
			if not out:
				continue
			for o in out:
				midMesh = mn.createNode( 'mesh' )
				o.disconnect()
				a >> midMesh.a.inMesh
				polyTrans = mc.transferAttributes( midMesh.name, o.node.name, transferPositions = 1, transferNormals = 1, transferUVs = 0, transferColors = 0, sampleSpace = 5, searchMethod = 3 )
				midMesh.a.intermediateObject.v = 1
				midMesh.parent.delete()
		nodes[0]()
		rf.reloadSelected()



	

