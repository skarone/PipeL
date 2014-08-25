import general.mayaNode.mayaNode as mn

class PointOnCurve(object):
	"""control point on curve based on parameters"""
	def __init__(self, curveName):
		self._curve = curveName

	@property
	def curve(self):
		"""return the curve that we are looking"""
		return self._curve

	def at(self, parameter ):
		"""return the point at a specific percent of the curve based on 0 to 1"""
		pass

	def nodeAt(self, parameter):
		"""return a node connected to the curve at the parameter"""
		node = mn.createNode( 'pointOnCurveInfo' )
		self.curve.a.worldSpace >> node.a.inputCurve
		node.a.parameter.v = parameter
		return node

"""
import rigging.utils.pointOnCurve.pointOnCurve as pntcrv
reload( pntcrv )
pntcrv.createTransformsForSelection( 'curveShape1' )
"""

def createTransformsForSelection( cur ):
	curv = crv.Curve( cur )
	#create transforms constrained to a curve based on selected objcets
	trfs = []
	for r in mn.ls( sl = True ):
		pnt = PointOnCurve( curv )
		nd = nodeAt( curv.uParam( r.worldPosition ) )
		grp = mn.createNode( "transform" )
		grp.name = r.name + '_curve_cons_grp'
		nd.a.position >> grp.a.t
		trfs.append( grp )
	return trfs
