import general.mayaNode.mayaNode as mn
import maya.cmds as mc


def createFollow( obj, constraintObjects ):
	"""create a constraint, and add attribute to object to control"""
	obj = mn.Node( obj )
	objectToConstraint = mn.Node( mc.group( obj.name, n = obj.name + '_grp' ) )
	cons = mn.Node( mc.parentConstraint( constraintObjects, objectToConstraint, mo = True )[0] )
	enum = ''
	attrName = 'follow'
	for a in constraintObjects:
		enum += a + ':'
	if not obj.attr( attrName ).exists:
		obj.a.follow.add( at = "enum", en = enum, k = True )
	else:
		attrName += '2'
		obj.attr( attrName ).add( at = "enum", en = enum, k = True )
	for i,a in enumerate( constraintObjects ):
		cond = mn.createNode( 'condition', n = obj.name + a + '_COND' )
		cond.a.colorIfTrueR.v  = 1
		cond.a.colorIfFalseR.v = 0
		cond.a.secondTerm.v    = i
		obj.attr( attrName ) >> cond.a.firstTerm
		cond.a.outColorR >> cons.attr( a + 'W' + str( i ) )

"""
obj = 'IKArm_R'
constraintObjects = ['Main', 'FKHead_M', 'Root_M']
import rigging.multiFollow.multiFollow as mfw
mfw.createFollow( obj, constraintObjects )
"""
