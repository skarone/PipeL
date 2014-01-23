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

	@property
	def objects(self):
		"""return the objects in the render layer"""
		try:
			return self.a.renderInfo.output.nodes
		except:
			return []

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
		objsWithOverNoConnInLay = self.a.adjustments.output
		tweaksDict = {}
		if not objsWithOverNoConnInLay:
			return {}
		for tw in objsWithOverNoConnInLay:
			if tw.type =='message':
				cons =  tw.output
				if cons:
					tweaksDict[tw] = cons[0].name
			else:
				plg = [ a for a in tw.output if self.name in a.fullname ]
				if plg:
					plig = mn.NodeAttribute( self, plg[0].name.replace( '.plug', '.value' ) )
					print plig.fullname
					tweaksDict[tw] = plig.v
				else:
					tweaksDict[tw] = tw.v
		return tweaksDict

	@overridesWithValues.setter
	def overridesWithValues(self, tweaksDict):
		"""override values in attributes based on dictionary"""
		for tw in tweaksDict.keys():
			if 'initialShadingGroup' in tw: #FIX TEMPORAL
				continue
			if not tw.exists:
				continue
			tw.overrided = True
			typ = tw.type
			#check if the attribute has an input connection
			inpt = tw.input
			if inpt:
				inpt // tw #disconnect
			if ( 'surfaceShader' in attrTweaks and isinstance( objTweaks[attrTweaks], str )) or typ == 'message' : # CONNECTION
				tw >> tweaksDict[ tw ]
			else:
				tw.v = tweaksDict[tw]

	@property
	def overridedShader(self):
		"""return the shader overrided"""
		shGrp = self.a.shadingGroupOverride.input
		if shGrp:
			shader = shGrp.node.a.surfaceShader.input.node
			return shader
		else:
			return None

	@overridedShader.setter
	def overridedShader(self, shader):
		"""assign a shader for the layer to override all the shaders"""
		mm.eval( 'hookShaderOverride("' + self.name + '", "", "' + shader.name + '");' )

	def removeOverridedShader(self):
		"""remove shader override from layer"""
		self.a.shadingGroupOverride.disconnect()

	@property
	def overridesWithConnections(self):
		"""return a dictionary with the overrided attributes and their new connections, and also what shaders to export"""
		conns = self.a.outAdjustments.output
		if conns:
			nds = conns.nodes
		else:
			return None, None
		objsWithOverWithConnInLay = nds
		connectDict = {}
		shadersToExport = []
		for cv in range( 0, len( objsWithOverWithConnInLay ), 2 ):
			if objsWithOverWithConnInLay[cv + 1].type == 'shadingEngine':
				connectDict[objsWithOverWithConnInLay[cv]] = objsWithOverWithConnInLay[cv+1]
				shadersToExport.append( objsWithOverWithConnInLay[cv+1] )	#HERE WE KNOW WHAT SHADERS WE NEED TO EXPORT =)
			elif objsWithOverWithConnInLay[cv].type == 'shadingEngine':
				connectDict[objsWithOverWithConnInLay[cv+1]] = objsWithOverWithConnInLay[cv]
				shadersToExport.append( objsWithOverWithConnInLay[cv] )		#HERE WE KNOW WHAT SHADERS WE NEED TO EXPORT =)
		shadersToExport = list(set(shadersToExport))
		return connectDict, shadersToExport

	@overridesWithConnections.setter
	def overridesWithConnections(self, connectDict):
		"""make overrides in attributes based on dictionary"""
		for c in connectDict.keys():
			if not c.exists:
				continue
			c()
			mc.hyperShade( a = connectDict[c] )


