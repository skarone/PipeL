"""
Scatter objects allong curve, it will take an array of objects and scatter in the curve.


import general.curveScatter.curveScatter as crvScat
import modeling.curve.curve as crv
import general.mayaNode.mayaNode as mn

crvScat.CurveScatter( 
        curve = crv.Curve( 'curveShape1' ), 
        objects = [mn.Node( 'pSphere1' ),mn.Node( 'pCone1' ),mn.Node( 'pCube1' )],
        pointsCount = 10, 
        useTips = True, 
        keepConnected = True,
        tangent = 1,
        rand = 0 )

"""
import random
import iters.iters as it
import rigging.utils.pointOnCurve.pointOnCurve as pCrv
import general.mayaNode.mayaNode as mn
import general.undo.undo as undo
import maya.cmds as mc

class CurveScatter(object):
	"""main class to handle scatter"""
	def __init__(self, curve, objects, pointsCount, useTips = False, keepConnected = True, tangent = False,rand = False  ):
		"""creates objects allong curve,
		curve: Curve Class object that handles the curve
		objects: Array of one o more transforms objects to position allong curve
		pointsCount: Amount of points in the curve
		useTips: is to position objects in the curve
		keepConnected: Keep pointOnCurveInfo connected between transform and curve
		tangent: Manage rotation on objects also
		rand: Place the objects in random order"""
		if useTips:
			val = -1
		else:
			val = 1
		startParam = 1.0 / ( pointsCount + val )
		param      = 0
		objsIter = it.bicycle( objects )
		with undo.Undo():
			for p in range( pointsCount ):
				#place transform in param point
				if not useTips:
					param += startParam
				if rand:
					baseobj = random.choice( objects )
				else:
					baseobj = objsIter.next()
				obj = baseobj.duplicate()
				pcurveNode = mn.Node( mc.pathAnimation( obj.name, su=0.5,  c=curve.name, fm = True, follow=tangent ) )
				animCurve = pcurveNode.a.uValue.input.node
				animCurve.delete()
				if keepConnected:
					obj.a.parameter.add( k = True )
					obj.a.parameter.v = param
					obj.a.parameter.min = 0
					obj.a.parameter.max = 1
					obj.a.parameter >> pcurveNode.a.uValue
				else:
					if param > 1.0:
						param = 1
					pcurveNode.a.uValue.v = param
					t = obj.a.t.v
					r = obj.a.r.v
					pcurveNode.delete()
					obj.a.t.v = t[0]
					obj.a.r.v = r[0]
				if useTips:
					param += startParam

