import general.mayaNode.mayaNode as mn

class PointOnCurve(object):
	"""control point on curve based on parameters"""
	def __init__(self, curveName):
		self._curve = mn.Node( curveName )

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
