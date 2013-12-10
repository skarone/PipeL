import general.mayaNode.mayaNode as mn
import rigging.curveBased.curveBased as crvBased

def createSoftsOnFace( mesh ):
	grp = mn.Node( 'base_head_rig_grp' )
	createSoftOnFaceCurves( mesh, grp )
	createSoftOnFacePoints( mesh, grp )
	
def createSoftOnFaceCurves( mesh, grp ):
	crvs = [c for c in grp.children if c.shape.type == 'nurbsCurve' ]
	for c in crvs:
		crvBased.createSofts( c.parent.name.replace( '_crv','' ), c.name, mesh, c.parent.a.controls_count.v, c.parent.a.use_tips.v )
	


