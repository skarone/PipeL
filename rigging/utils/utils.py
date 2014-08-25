import maya.cmds as mc
import general.mayaNode.mayaNode as mn

def getSkinFromGeo(mesh):
	"""return the skincluster node from mesh"""
	skins = [ h for h in mc.listHistory( mesh, pdo = 1, il = 2 ) if mc.nodeType( h ) == 'skinCluster' ]
	return skins

def copyVertexWeights( fromVertex, fromSkin, toVerteces, toSkin ):
	"""copy vertex skin weights from vertex to verteces list"""
	VtxJoints = mc.skinPercent(fromSkin, fromVertex, ib = 0.0001, q = True, t = None )
	VtxSkinValue = mc.skinPercent( fromSkin, fromVertex, ib = 0.0001, q = True, v = True )
	for v in toVerteces:
		mc.setAttr( toSkin + '.normalizeWeights', 0 )
		for i in range( len(VtxJoints) ):
			mc.skinPercent( toSkin, v, pruneWeights = 100, normalize = False )
		for i in range( len( VtxJoints ) ):
			mc.skinPercent( toSkin, v, tv = [(VtxJoints[i], VtxSkinValue[i])] )
		mc.setAttr( toSkin + '.normalizeWeights', 1 )

def addJointAssInfluence( jntName = '', mesh = ''):
	"""add Joint to influence mesh
	:param jntName: joint Name to add as influece
	:param mesh:    mesh name"""
	skn = getSkinFromGeo( mesh )
	mc.skinCluster( skn, e = True, dr = 4, lw = True, wt = 0, ai = jntName )

def addSelectedJointsToSelectedMesh():
	"""select all the joints you want to add and then select the mesh"""
	jnts = mc.ls( sl = True )
	msh = jnts[-1]
	jnts.remove( msh )
	for j in jnts:
		addJointAssInfluence( j, msh )
