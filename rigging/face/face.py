import general.mayaNode.mayaNode as mn
import maya.cmds as mc
import rigging.curveBased.curveBased as crvBased
reload( crvBased )
import rigging.utils.SoftModCluster.SoftModCluster as sf
reload( sf )
"""
HOW TO USE:
	IMPORT BASE_HEAD_RIG_GRP IN SCENE, MODIFY POSITION OF CURVES ( CRV ) AND LOCATORS ( PNT ) INSIDE THAT GRP, ADD EXTRA CURVES OR LOCATORS.
	AND RUN THE CODE ABOVE

import rigging.face.face as fc
reload( fc )
import maya.cmds as mc
mesh = 'Cuerpo1Shape' #MESH TO BE DEFORM
vertexToRemove = mc.ls( sl = True, fl = True ) #LIST OF VERTECES THAT YOU DONT WONT TO BE MODIFIED BY THE DEFORMERS ( EX: EYELIDS )
asd = fc.createSoftsOnFace( mesh, vertexToRemove )
"""

def createSoftsOnFace( mesh, vertexToRemove = [] ):
	grp = mn.Node( 'base_head_rig_grp' )
	softs = createSoftOnFaceCurves( mesh, grp, vertexToRemove )
	softs.extend( createSoftOnFacePoints( mesh, grp, vertexToRemove ) )
	faceSoftsGrp = mn.Node( mc.group( n = 'face_SFM_grp', em = True ) )
	for s in softs:
		s.parent = faceSoftsGrp
	#removeEyeLidsFromSofts( vertex, softs )
	return softs

def removeEyeLidsFromSofts( vertex, softs ):
	"""remove eyelids verteces from softs so they don't move them"""
	if not vertex:
		return
	print 'in remove eyelids softs'
	for s in softs:
		se = s.name.replace( 'Handle', 'Set' )
		mc.sets( vertex, rm = se )
	
def createSoftOnFaceCurves( mesh, grp, vertexToRemove = [] ):
	crvs = [c for c in grp.children if c.shape.type == 'nurbsCurve' ]
	softs = []
	for c in crvs:
		softs.extend( crvBased.createSofts( c.name.replace( '_crv','' ), c.name, mesh, c.a.controls_count.v, c.a.use_tips.v , False, vertexToRemove ) )
	return softs

def createSoftOnFacePoints( mesh, grp, vertexToRemove = [] ):
	pnts = [c for c in grp.children if c.shape.type == 'locator' ]
	softs = []
	for l in pnts:
		softMod = sf.SoftModCluster( l.name.replace( '_pnt','' ) + '_SFM', mesh )
		handle = softMod.create( l.a.t.v[0], vertexToRemove )
		softs.append( handle )
	return softs

def softModsToStickys( mesh, skin = '' ):
	"""convert all the soft mods of the face to stickys"""
	grp = mn.Node( 'face_SFM_grp' )
	sticksGrp = mn.Node( mc.group( n = 'faceRig_grp', em = True ) )
	if skin == '': #THERE IS NO SKIN... CREATE ONE WITH A BASE JOINT
		mc.select(d=True)
		jnt = mn.Node( mc.joint(p=(0,0,0), n = 'faceBase_jnt') )
		skin = mc.skinCluster( jnt.name, mesh, dr=4.5, normalizeWeights = 2)[0]
		jnt.parent = sticksGrp
	softs = [c.shape for c in grp.children if c.shape.type == 'softModHandle' ]
	for i,s in enumerate( softs ):
		control = crvBased.softModToSticky( mesh, skin, s )
		control.parent( sticksGrp )

	
	


