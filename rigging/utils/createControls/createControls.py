import modeling.curve.curve as crv
import general.transform.transform as trf
import general.mayaNode.mayaNode as mn
import maya.cmds as mc

"""
import rigging.utils.createControls.createControls as ctls
reload( ctls )
ctls.createControlsForSelection()
"""

def createControlsForSelection( shape = 'circleX',childsAlso = True, par = None, lastAlso = False, constraint = True ):
	#CREATE A CONTROL FOR THE SELECTED OBJECTS, WITH OFFSET GROUP AND CONSTRAINT
	#ALSO FOR THEIR CHILDRENS EXCEPT LAST
	for s in mn.ls( sl = True ):
		grp = createControl( s, shape, childsAlso, par, lastAlso, constraint )

            
def createControl( s, shape = 'circleX', childsAlso = True, par = None, lastAlso = False, constraint = True ):
    if not lastAlso and not s.children:
        return
    grp = mn.createNode( "transform", ss = True )
    grp.name = s.name + "_grp"
    curv = crv.Curve( s.name + "_ctl" )
    curv = curv.create( shape )
    trf.snap( s, grp )
    curv.parent = grp
    curv.a.t.v  = [0]*3
    curv.a.r.v  = [0]*3
    if par:
        grp.parent = par
    if constraint:
        mc.parentConstraint( curv, s, mo = True )
        mc.scaleConstraint( curv, s, mo = True )
    if childsAlso and s.children:
		for c in s.children:
			c = mn.Node( c.name.split( '|' )[-1] )
			createControl( c, shape, True, curv, lastAlso, constraint )
    return grp

