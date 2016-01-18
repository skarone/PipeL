import modeling.curve.curve as crv
import general.transform.transform as trf
import general.mayaNode.mayaNode as mn
reload(mn)
import maya.cmds as mc

"""
import rigging.utils.createControls.createControls as ctls
reload( ctls )
ctls.createControlsForSelection()
"""

def createControlsForSelection( shape = 'circleX',childsAlso = True, par = None, lastAlso = False, constraint = True, connect = False, offsetGroup = True ):
	#CREATE A CONTROL FOR THE SELECTED OBJECTS, WITH OFFSET GROUP AND CONSTRAINT
	#ALSO FOR THEIR CHILDRENS EXCEPT LAST
	for s in mn.ls( sl = True ):
		createControl( s, shape, childsAlso, par, lastAlso, constraint, connect, offsetGroup )

def createControl( si, shape = 'circleX', childsAlso = True, par = None, lastAlso = False, constraint = True, connect = False, offsetGroup = True ):
	if not lastAlso and not si.children:
		return
	if shape == 'joint':
		mc.select( cl = True )
		curv = mn.Node( mc.joint( n = si.name + "_jnt" ) )
	elif shape == 'locator':
		curv = mn.Node( mc.spaceLocator( n = si.name + '_loc' )[0] )
	else:
		curv = crv.Curve( si.name + "_ctl" )
		curv = curv.create( shape )
	if offsetGroup:
		grp = mn.createNode( "transform", ss = True )
		grp.name = si.name + "_grp"
		trf.snap( si, grp )
		curv.parent = grp
		curv.a.t.v  = [0]*3
		curv.a.r.v  = [0]*3
		if par:
			grp.parent = par
	else:
		trf.snap( si, curv )
		curv.freeze()
	if constraint:
		mc.parentConstraint( curv, si, mo = True )
		mc.scaleConstraint( curv, si, mo = True )
	if connect:
		curv.a.t >> si.a.t
		curv.a.r >> si.a.r
		curv.a.s >> si.a.s
	if childsAlso and si.children:
		for c in si.children:
			c = mn.Node( c.name.split( '|' )[-1] )
			createControl( c, shape, True, curv, lastAlso, constraint, connect, offsetGroup )

