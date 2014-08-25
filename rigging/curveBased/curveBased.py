import maya.cmds as mc
import general.mayaNode.mayaNode as mn
import maya.mel as mm

import general.curveScatter.curveScatter as crvScat
reload( crvScat )
import modeling.curve.curve as crv
reload( crv )
import rigging.utils.SoftModCluster.SoftModCluster as sf
reload( sf )
import rigging.stickyControl.stickyControl as stk
reload( stk )


def createSofts( sysName, curv, mesh, softsCount, useTip, groupIt = True, vertexToRemove = [] ):
	"""docstring for fname"""
	space = mn.Namespace( sysName )
	space.create()
	softs = []
	with space.set():
		if groupIt:
			grp = mn.Node( mc.group( n = sysName + '_grp', em = True ) )
			grp.a.crvSystem.add( at = "bool" )
		obj = crv.Curve( sysName + '_CRV' )
		obj = obj.create( "sphere" )
		scat = crvScat.CurveScatter( 
				curve = crv.Curve( curv ), 
				objects = [obj],
				pointsCount = softsCount, 
				useTips = useTip, 
				keepConnected = True,
				tangent = 1,
				rand = 0 )
		for i,n in enumerate( scat._nodes ):
			softMod = sf.SoftModCluster( sysName + '_%i'%i + '_SFM', mesh )
			handle = softMod.create( n.a.t.v[0] , vertexToRemove )
			if groupIt:
				handle.parent = grp
			softs.append( handle )
	scat.delete()
	obj.delete()
	return softs

def createJointsOnSofts( sysName, mesh, skin ):
	"""create joints from the softMods of the system"""
	space = mn.Namespace( sysName )
	#with space.set():
	for i,s in enumerate( mn.ls( sysName + ':*', typ = 'softModHandle' ) ):
		softModToSticky( mesh, skin ,s )

def softModToSticky( mesh, skin ,soft, finalMesh = '' ):
	"""creates a sticky point on the softmod location and transfer their weights"""
	trans = soft.parent
	control = stk.ControlOnMesh( name = soft.name.replace( '_SFM', '' ), baseJoint = '', position = trans.worldPosition, mesh = mesh )
	control.create()
	mc.select( mesh, control.skinJoint.name )
	mc.skinCluster( skin, e = True, dr = 4, lw = True, wt=0, ai = control.skinJoint.name )
	control.skinJoint.a.lockInfluenceWeights.v = 0
	if not soft.a.joint.exists:
		print 'no existe joint attribute'
		soft.a.joint.add( at = "message" )
	if not control.skinJoint.a.soft.exists:
		print 'no existe soft attribute'
		control.skinJoint.a.soft.add( at = "message" )
	soft.a.joint >> control.skinJoint.a.soft
	sf.copyWeightsToJoint( soft.name, skin, control.skinJoint.name, mesh, finalMesh )
	return control


def deleteSofts():
	"""docstring for fname"""
	pass

def transferWeightToSel( skin, mesh ):
	"""transfer weight of selected softmod to their skin joint"""
	softMo = mn.ls( sl = True, dag = True, typ = 'softModHandle' )
	if softMo:
		for s in softMo:
			sf.copyWeightsToJoint( s.name, skin, s.a.joint.output[0].node.name, mesh )


