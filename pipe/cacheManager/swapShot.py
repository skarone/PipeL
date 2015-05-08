import pipe.project.project as prj
import maya.cmds as mc
import general.reference.reference as rf

def swapShot( projName, seqName, shotName ):
	"""docstring for swapShot"""
	proj = prj.Project( projName )
	seq  = proj.sequence( seqName )
	#replace cache from current scene T04 to shot T09
	sh = seq.shot( shotName )
	mc.editRenderLayerGlobals( currentRenderLayer='defaultRenderLayer' )
	replaced = []
	new      = []
	removed = []
	refs = mc.ls( '*_RIG*', typ = 'reference' )
	for c in sh.caches[ 'anim' ]:
		sel = mc.ls( c.name + ':*', dag = True, ni = True, typ = ['mesh','nurbsCurve'] )
		if sel:#REPLACE
			mc.select(sel[0])
			print 'REPLACED', c.name
			c.replace()
			replaced.append( c )
		else:#ADD
			print 'ADDED', c.name
			c.importForAsset( proj.asset( c.name[:c.name.rindex( '_' )] ), 1 , c.name, True, False, sh )
			new.append( c )
	for r in refs:
		if any( a.name == r[:-2] for a in sh.caches[ 'anim' ] ):
			continue
		mc.select( r )
		print 'REMOVED', r
		rf.removeSelected()
		removed.append( r )
		
	print 'CACHES ADDED'
	print new
	print 'CACHES REPLACED'
	print replaced
	print 'REFS REMOVED'
	print removed

	#change camera
	cam = mc.ls( '*_CAM:*', typ = 'camera' )
	if cam:
		mc.select( cam )
		rf.removeSelected()
	sh.poolCam.reference()
	tim = sh.animPath.time
	mc.currentUnit( time=tim['tim'], linear = tim['lin'], angle = tim[ 'angle' ] )
	mc.playbackOptions( min = tim[ 'min' ],
						ast = tim[ 'ast' ], 
						max = tim[ 'max' ], 
						aet = tim[ 'aet' ] )
	groupsToAdd = []
	for n in new:
		tr = mc.ls( '|' + n.name + ':*' , typ = 'transform' )
		groupsToAdd.extend( tr )
	if mc.objExists( 'New_Objects' ):
		mc.delete( 'New_Objects' )
	set = mc.sets( n = 'New_Objects', em = True )
	mc.sets( groupsToAdd, include = set )



