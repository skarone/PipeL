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


def createSofts( sysName, curv, mesh, softsCount, useTip ):
	"""docstring for fname"""
	space = mn.Namespace( sysName )
	space.create()
	with space.set():
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
			handle = softMod.create( n.a.t.v[0] )
			handle.parent = grp
	scat.delete()
	obj.delete()

def createJointsOnSofts( sysName, mesh, skin ):
	"""create joints from the softMods of the system"""
	space = mn.Namespace( sysName )
	with space.set():
		for i,s in enumerate( mn.ls( sysName + ':*', typ = 'softModHandle' ) ):
			trans = s.parent
			control = stk.ControlOnMesh( name = sysName + '%i'%i, baseJoint = '', position = trans.worldPosition, mesh = mesh )
			control.create()
			mc.select( mesh, control.skinJoint.name )
			mc.skinCluster( skin, e = True, dr = 4, lw = True, wt=0, ai = control.skinJoint.name )
			control.skinJoint.a.lockInfluenceWeights.v = 0
			s.a.joint.add( at = "message" )
			control.skinJoint.a.soft.add( at = "message" )
			s.a.joint >> control.skinJoint.a.soft
			sf.copyWeightsToJoint( s.name, skin, control.skinJoint.name, mesh )


def deleteSofts():
	"""docstring for fname"""
	pass

def transferWeightToSel( skin, mesh ):
	"""transfer weight of selected softmod to their skin joint"""
	softMo = mn.ls( sl = True, dag = True, typ = 'softModHandle' )
	if softMo:
		for s in softMo:
			sf.copyWeightsToJoint( s.name, skin, s.a.joint.output[0].node.name, mesh )


