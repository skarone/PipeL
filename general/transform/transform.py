import maya.cmds as mc

def snap( master, slave ):
	#constrains
	oCons = mc.orientConstraint( master, slave, w = 1 ) 
	pCons = mc.pointConstraint( master, slave ,w = 1 )
	mc.refresh()

	mc.delete( oCons )
	mc.delete( pCons )
