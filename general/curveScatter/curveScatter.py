"""
Scatter objects allong curve, it will take an array of objects and scatter in the curve.
"""
import random
import iters.iters as it
import rigging.utils.pointOnCurve.pointOnCurve as pCrv

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
		
		for p in range( pointsCount ):
			#place transform in param point
			if not useTips:
				param += startParam
			if rand:
				baseobj = random.choice( objects )
			else:
				baseobj = objsIter.next()
			obj = baseobj.duplicate()
			pcurve = pCrv.PointOnCurve( curve.name )
			pcurveNode = pcurve.nodeAt( param )
			pcurveNode.a.turnOnPercentage.v = 1
			if keepConnected:
				pcurveNode.attr( "result.position" ) >> obj.a.t
				obj.a.parameter.add( k = True )
				obj.a.parameter.min = 0
				obj.a.parameter.max = 1
				obj.a.parameter.v = param
				if tangent:
				obj.a.parameter >> pcurveNode.a.parameter
			else:
				obj.a.t.v = pcurveNode.attr( "result.position" ).v
				pcurveNode.delete()
			if useTips:
				param += startParam
