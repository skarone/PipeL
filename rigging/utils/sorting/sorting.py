"""
Sort Methods:
	sortedByPosition: compare trasforms position in an specific axis
"""

import maya.cmds as mc
def compPosition( x, y, axis ):
	pos1 = mc.xform( x, q = 1, ws = 1, t = 1 )
	pos2 = mc.xform( y, q = 1, ws = 1, t = 1 )
	if pos1[axis] < pos2[axis]:
		return -1
	elif pos1[axis] == pos2[axis]:
		return 0
	else:
		return 1

def sortedByPosition( objArray, axis = "x" ):
	"""
	objArray: Array of maya transforms
	axis: axis to be compared
	"""
	finalAxis = { "x":0, "y":1, "z":2 }
	axis = finalAxis[axis]
	sortedArray = sorted( objArray, cmp=lambda x,y: compPosition(x,y,axis) )
	return sortedArray



