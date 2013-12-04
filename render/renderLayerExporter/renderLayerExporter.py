import render.renderlayer.renderlayer as rlayer
import cPickle as pickle

class RenderLayerExporter(object):
	"""export information from lighting scene"""
	def __init__(self, pathDir):
		self._path = pathDir
		
	def export(self):
		"""export information of scene to path"""
		lays = rlayer.renderlayers()
		data = {}
		for l in lays:

	
	@property
	def dataPath(self):
		"""return path for file"""
		return self._path + '/renderLayerData.data'

	@property
	def lightPath(self):
		"""return path for lights file"""
		return self._path + '/lights.ma'

	@property
	def shaderPath(self):
		"""return the path for the shader file"""
		return self._path + '/shaders.ma'


