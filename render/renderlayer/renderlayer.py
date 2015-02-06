import general.mayaNode.mayaNode as mn
reload( mn )
import maya.cmds as mc
import maya.mel as mm

def renderlayers():
	"""return the renderlayers in the scene"""
	return [ RenderLayer( r.name ) for r in mn.ls( typ = 'renderLayer' ) ]

def current():
	"""return the current renderlayer"""
	renName = mc.editRenderLayerGlobals( query=True, currentRenderLayer=True )
	return RenderLayer( renName )

class RenderLayer(mn.Node):
	"""main class to handle render layers"""
	def __init__(self, name):
		super(RenderLayer, self).__init__( name )

	def create(self):
		"""create render layer if not exists"""
		if not self.exists:
			mc.createRenderLayer( name = self.name, empty = 1 )

	def __repr__(self):
		"""return the representation"""
		return "RenderLayer( %s )"%self.name

	def makeCurrent(self):
		"""make render layer current"""
		mc.editRenderLayerGlobals( currentRenderLayer = self.name )

	@property
	def objects(self):
		"""return the objects in the render layer"""
		try:
			return self.a.renderInfo.output.nodes
		except:
			return []

	@property
	def lights(self):
		"""return the lights in the render layer"""
		if self.objects:
			lits = mn.ls( self.objects, typ=['light','aiAreaLight','aiSkyDomeLight','aiVolumeScattering','aiSky'], l=1, dag = True )
			return lits
		return None

	def add( self, objs ):
		"""add objects to the render layer"""
		for o in objs:
			if o.exists:
				mc.editRenderLayerMembers( self.name, o, noRecurse = True )

	def remove(self, objs):
		"""remove specific objs from render layer"""
		for o in objs:
			if o.exists:
				mc.editRenderLayerMembers( self.name, o, remove = True, noRecurse = True )

	def clean(self):
		"""remove all the objects in the render layers"""
		self.remove( self.objects )

	@property
	def overridesWithValues(self):
		"""return a dictionary with overrided attributes and their new values"""
		inpSize = self.a.adjustments.size
		tweaks = {}
		for i in range(inpSize):
			plg = self.attr( 'adjustments[' +str(i) + '].plug' ).input
			valAttr = self.attr( 'adjustments[' +str(i) + '].value' )
			if plg:
				if valAttr.input: #THere is a connection to the value to override
					tweaks[ plg ] = valAttr.input
				else: #Store plug and new value
					if plg.children:
						count = 0
						for p in plg.children:
							try:
								if 'Angle' in p.type:
									tweaks[ p ] = valAttr.v[0][ count ]/0.0174532925 #deg to rad
								else:
									tweaks[ p ] = valAttr.v[0][ count ]
								count += 1
							except:
								continue
					else:
						if 'Angle' in plg.type:
							tweaks[ plg ] = valAttr.v/0.0174532925 #deg to rad
						else:
							tweaks[ plg ] = valAttr.v
		return tweaks

	@overridesWithValues.setter
	def overridesWithValues(self, tweaksDict):
		"""override values in attributes based on dictionary"""
		if not tweaksDict:
			return
		self.makeCurrent()
		for tw in tweaksDict.keys():
			if not tw.exists:
				continue
			tw.overrided = True
			if str( type( tweaksDict[tw] )) ==  "<class 'general.mayaNode.mayaNode.NodeAttribute'>" :
				if tweaksDict[tw].exists:
					tweaksDict[tw] >> tw
			else:
				tw.v = tweaksDict[tw]

	@property
	def overridedShader(self):
		"""return the shader overrided"""
		shGrp = self.a.shadingGroupOverride.input
		if shGrp:
			try:
				shader = shGrp.node
				return shader
			except:
				return None
		else:
			return None

	@overridedShader.setter
	def overridedShader(self, shader):
		"""assign a shader for the layer to override all the shaders"""
		#shader.a.message >> self.a.shadingGroupOverride
		mm.eval( 'hookShaderOverride("' + self.name + '", "", "' + shader.name + '");' )

	def removeOverridedShader(self):
		"""remove shader override from layer"""
		self.a.shadingGroupOverride.disconnect()

	@property
	def overridesWithConnections(self):
		"""return a dictionary with the overrided attributes and their new connections, and also what shaders to export"""
		inpSize = self.a.outAdjustments.size
		tweaks = {}
		shadersToExport = []
		for i in range(inpSize):
			plg = self.attr( 'outAdjustments[' +str(i) + '].outPlug' ).input
			valAttr = self.attr( 'outAdjustments[' +str(i) + '].outValue' ).output
			if plg:
				if valAttr:
					tweaks[ plg.node ] = valAttr[0].node
					shadersToExport.append( valAttr[0].node ) 
		return tweaks, shadersToExport

	@overridesWithConnections.setter
	def overridesWithConnections(self, connectDict):
		"""make overrides in attributes based on dictionary"""
		if not connectDict:
			return
		self.makeCurrent()
		for c in connectDict.keys():
			if isinstance( c, unicode ):
				continue
			if not c.exists:
				continue
			if connectDict[c].exists:
				c()
				mc.hyperShade( a = connectDict[c] )


