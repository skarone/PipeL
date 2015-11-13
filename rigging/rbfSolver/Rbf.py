import math
import maya.OpenMaya as om
import base as bs
reload(bs)
import random

class Rbf(object):
	"""docstring for Rbf"""
	def __init__(self, *args, **kwargs):
		#args are coordinates array x, y, z and last d their values
		#convert input to MFloatVectorArray
		self.xi = om.MFloatVectorArray()
		for b in range( len( args[0] ) ):
			self.xi.append(om.MFloatVector( args[0][b], args[1][b], args[2][b]))
		self.N = self.xi.length() #amount of z values = amount of vectors
		self.di = args[-1]
		self.norm = self._euclidean_norm
		r = self._call_norm( self.xi, self.xi )
		self.epsilon = kwargs.pop('epsilon', None)
		if self.epsilon is None:
			ximax = self.amax( self.xi ) #max vector
			ximin = self.amin( self.xi ) #min vector
			edges = ximax - ximin
			self.epsilon = math.pow( edges.x*edges.y*edges.z/self.N, 1.0/3.0 )
		self.function = kwargs.pop('function', 'multiquadric')
		self.A = self._init_function( r )
		self.nodes = self.linalg( self.A, self.di )

	def _init_function(self, r):
		"""docstring for _init_function"""
		if isinstance(self.function, str):
			self.function = self.function.lower()
			_mapped = {'inverse': 'inverse_multiquadric',
						'inverse multiquadric': 'inverse_multiquadric',
						'thin-plate': 'thin_plate'}
			if self.function in _mapped:
				self.function = _mapped[self.function]

			func_name = "_h_" + self.function
			if hasattr(self, func_name):
				self._function = getattr(self, func_name)
			else:
				functionlist = [x[3:] for x in dir(self) if x.startswith('_h_')]
				raise ValueError("function must be a callable or one of " +
										", ".join(functionlist))
			self._function = getattr(self, "_h_"+self.function)
		a0 = self._function(r)
		return a0

	def linalg(self, A, di):
		"""docstring for linalg"""
		#first create matrix!
		Amat = bs.Matrix( bs.make_identity( self.xi.length(), self.xi.length() ))
		count = 0
		for x in range(self.xi.length()):
			for y in range(self.xi.length()):
				Amat[x][y] = A[count]
				count += 1
		#now revert mat
		AmatInv = Amat.invert()
		res = []
		if isinstance(di[0], list):
			for d in range(len(di)):
				diMat = bs.Matrix( [[di[d][a]] for a in range( len(di[d]))] )
				res.append( AmatInv*diMat )
		else:
			diMat = bs.Matrix( [[di[a]] for a in range( len(di))] )
			res.append( AmatInv*diMat )
		return res

	def _call_norm(self, x1, x2):
		"""docstring for _call_norm"""
		return self.norm(x1,x2)

	def _euclidean_norm(self, x1, x2):
		"""return the length between the 2 vectors array"""
		res = om.MFloatArray()
		for x in range(x1.length()):
			for y in range(x2.length()):
				#mat[x][y] = (x1[x] - x2[y]).length()
				res.append( (x1[x] - x2[y]).length() )
		return res

	def amax(self, x1):
		"""return the largest number for each axis in x1 array"""
		xmax = x1[0][0]
		ymax = x1[0][1]
		zmax = x1[0][2]
		for x in range(x1.length()):
			if xmax < x1[x][0]:
				xmax = x1[x][0]
			if ymax < x1[x][1]:
				ymax = x1[x][1]
			if zmax < x1[x][2]:
				zmax = x1[x][2]
		return om.MFloatVector(xmax, ymax, zmax)

	def amin(self, x1):
		"""return the smallest vector in x1 array"""
		xmin = x1[0][0]
		ymin = x1[0][1]
		zmin = x1[0][2]
		for x in range(x1.length()):
			if xmin > x1[x][0]:
				xmin = x1[x][0]
			if ymin > x1[x][1]:
				ymin = x1[x][1]
			if zmin > x1[x][2]:
				zmin = x1[x][2]
		return om.MFloatVector(xmin, ymin, zmin)


	def _h_gaussian(self,r):
		res = om.MFloatArray()
		for ri in range(r.length()):
			res.append( math.exp(-(1.0/self.epsilon*r[ri])**2))
		return res

	def _h_multiquadric(self, r):
		"""docstring for _h_multiquadric"""
		res = om.MFloatArray()
		for ri in range(r.length()):
			res.append( math.sqrt((1.0/self.epsilon*r[ri])**2 + 1))
		return res


	def __call__(self, vectors):
		"""docstring for __call__"""
		r = self._call_norm( vectors, self.xi )
		r2 =  self._function(r)
		#convert r2 to matrix
		r2mat = bs.Matrix( bs.make_identity( vectors.length(), self.xi.length() ))
		count = 0
		for x in range(vectors.length()):
			for y in range(self.xi.length()):
				r2mat[x][y] = r2[count]
				count += 1
		res = []
		for n in range(len(self.nodes)):
			res.append( r2mat * self.nodes[n] )
		return res

