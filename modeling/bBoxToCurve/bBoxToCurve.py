import general.mayaNode.mayaNode as mn
import maya.cmds as mc

"""
import modeling.bBoxToCurve.bBoxToCurve as bbox
reload( bbox )
bbox.BBoxToSel()

"""

def BBoxToSel():
	sel = mn.ls( sl = True )
	for s in sel:
		BBoxToCurve( s.name )

def BBoxToCurve( obj, autoParent = False ):
	bbinfo = mc.exactWorldBoundingBox( obj ) # xmin, ymin, zmin, xmax, ymax, zmax
	point1 = [bbinfo[0],bbinfo[1],bbinfo[2]]
	point2 = [bbinfo[3],bbinfo[4],bbinfo[5]]
	coords = ([point1[0], point2[1], point2[2] ],
			 point2,
			 [ point2[0], point2[1], point1[2] ],
			 [ point1[0], point2[1], point1[2] ],
			 [ point1[0], point2[1], point2[2] ],
			 [ point1[0], point1[1], point2[2] ],
			 point1,
			 [ point2[0], point1[1], point1[2] ],
			 [ point2[0], point1[1], point2[2] ],
			 [ point1[0], point1[1], point2[2] ],
			 [ point2[0], point1[1], point2[2] ],
			 point2,
			 [ point2[0], point2[1], point1[2] ],
			 [ point2[0], point1[1], point1[2] ],
			 point1,
			 [ point1[0], point2[1], point1[2] ])
	bbox = mc.curve( d = 1, p = coords, k = [ a for a in range(len(coords))], n = "cube#" )
	if autoParent:
		shape = mc.listRelatives( bbox, f = True, s = True )
		mc.select( shape, obj )
		mc.parent( add = True, shape = True )
		mc.delete( bbox )
	return bbox

