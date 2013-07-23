import maya.cmds as mc
import maya.OpenMaya as om
vertCount = mc.polyEvaluate( 'hrs:laura:C_hairGeo_helmetSK__MSKSH', v = True )
vertVal = []
result = []
for v in range( 0, vertCount ):
	asd = mc.xform( 'hrs:laura:C_hairGeo_helmetSK__MSKSH.vtx[%i'%v+']', q = True, ws = True, t = True )
	if not vertVal == []:
		vec = om.MVector( asd[0],asd[1],asd[2] )
		if any( vec.isEquivalent( x ) for x in vertVal ):
			print v,'tiene el mismo valor!'
			result.append( 'hrs:laura:C_hairGeo_helmetSK__MSKSH.vtx[%i'%v+']' )
	vertVal.append( vec )


