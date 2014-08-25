import general.mayaNode.mayaNode as mn
import maya.cmds as mc

def copyVertexFromLeftToRight():
	"""move vertices from right blendshape to match left one"""
	ais = mn.ls( sl = True )
	dups = []
	for a in ais:
		dup = a.duplicate( 'dup_' + a.name[2:] )
		dup()
		dups.append( dup.name )
		mm.eval( 'abSymCtl( "fsBn" )' )
		for v in mc.ls( dup.name + '.vtx[*]', fl = True ):
			pos = mc.xform( v, q = True, t = True )
			mc.xform( v.replace( 'dup_', 'r_' ), t = pos )
		dup.delete()
		
def resetBlendshape( originalMesh = '', blendToReset = '' ):
	"""reset blendshape position to original face"""
	if not isinstance( originalMesh, mn.Node ):
		originalMesh = mn.Node( originalMesh )
	if not isinstance( blendToReset, mn.Node ):
		blendToReset = mn.Node( blendToReset )
	for v in mc.ls( originalMesh.name + '.vtx[*]', fl = True ):
		pos = mc.xform( v, q = True, t = True )
		mc.xform( v.replace( originalMesh.name, blendToReset.name ), t = pos )

def blendTargetsCount( blendNode ):
	"""
	Return the amount of blendshape targets in blend node
	"""
	return blendNode.a.weight.size

def extractBlendsTargets( blendNode, mesh, prefix = "" ):
	"""
	extract all blendshapes from blendshape node
	"""
	for i in range( blendTargetsCount( blendNode ) ):
		at = blendNode.attr( "weight[" +str( i )+"]" )
		geoName = prefix + mc.listAttr( at.fullname, sn = True )[0]
		at.v = 1
		mesh.duplicate( geoName )
		at.v = 0

	

