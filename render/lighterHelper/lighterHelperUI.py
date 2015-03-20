import os

import general.ui.pySideHelper as uiH
reload( uiH )
uiH.set_qt_bindings()
from Qt import QtGui,QtCore

import render.renderlayer.renderlayer as rlayer
reload( rlayer)
import render.renderLayerExporter.renderLayerExporter as rlExp
reload( rlExp )
import maya.cmds as mc
import maya.mel as mm
import general.mayaNode.mayaNode as mn
reload( mn )
import render.aov.aov as aov
reload( aov )
import mtoa.core as cor
from functools import partial
import pipe.mayaFile.mayaFile as mfl
reload( mfl )
import general.undo.undo as undo
import shading.textureManager.textureManager as tm
reload(tm)

#load UI FILE
PYFILEDIR = os.path.dirname( os.path.abspath( __file__ ) )
uifile = PYFILEDIR + '/lighterHelper.ui'
fom, base = uiH.loadUiType( uifile )


class LighterHelperUI(base,fom):
	def __init__(self, parent  = uiH.getMayaWindow(), *args ):
		if uiH.USEPYQT:
			super(base, self).__init__(parent)
		else:
			super(LighterHelperUI, self).__init__(parent)
		self.setupUi(self)
		#load arnold if it is not loaded
		self.loadArnold()
		self.setObjectName( 'ligther_Helper_WIN' )
		self._makeConnections()
		self._addAllAovs()
		#create an scriptjob thats update the UI on renderlayer change
		mc.scriptJob( e = ["renderLayerManagerChange", partial( self.updateLighterUI )], p = 'ligther_Helper_WIN' )
		self.updateLighterUI()
		#set icons for toolbar
		self.actionSpot.setIcon(QtGui.QIcon(":/spotlight.png"))
		self.actionDirectional.setIcon(QtGui.QIcon(":/directionallight.png"))
		self.actionPoint.setIcon(QtGui.QIcon(":/pointlight.png"))
		self.actionAmbient.setIcon(QtGui.QIcon(":/ambientlight.png"))
		self.actionArea.setIcon(QtGui.QIcon(":/arealight.png"))
		self.actionVolume.setIcon(QtGui.QIcon(":/volumelight.png"))
		self.actionRenderGlobals.setIcon(QtGui.QIcon(":/renderGlobals.png"))
		self.actionRenderView.setIcon(QtGui.QIcon(":/render.png"))
		self.actionLookThrough.setIcon(QtGui.QIcon(":/fileTextureView.png"))
		#internal variables
		self.isolatedLights = [] #lights that are beign turn off when we want to isolate others!
		self.isolatedObjects = [] #objects that are beign turn off when we one to isolate others!
		uiH.loadSkin( self, 'QTDarkGreen' )
		
	def _makeConnections(self):
		"""make the connections from the controls to de methods"""
		#OBJECTS
		self.connect( self.addObject_btn            , QtCore.SIGNAL("clicked()") , self.addObjectToLayer )
		self.connect( self.removeObject_btn         , QtCore.SIGNAL("clicked()") , self.removeObjectToLayer )
		self.connect( self.removeAllObjects_btn     , QtCore.SIGNAL("clicked()") , self.removeAllObjectsToLayer )
		#OBJECTS QUALITY
		self.connect( self.toLow_btn     , QtCore.SIGNAL("clicked()") , self.toLow )
		self.connect( self.toMid_btn     , QtCore.SIGNAL("clicked()") , self.toMid )
		self.connect( self.toHigh_btn     , QtCore.SIGNAL("clicked()") , self.toHigh )
		self.connect( self.dispOff_btn     , QtCore.SIGNAL("clicked()") , self.dispOff )
		self.connect( self.dispOn_btn     , QtCore.SIGNAL("clicked()") , self.dispOn )
		self.connect( self.plusSub_btn     , QtCore.SIGNAL("clicked()") , self.plusSub )
		self.connect( self.zeroSub_btn     , QtCore.SIGNAL("clicked()") , self.zeroSub )
		self.connect( self.minusSub_btn     , QtCore.SIGNAL("clicked()") , self.minusSub )
		#SHADING
		self.connect( self.mateInArnold_btn         , QtCore.SIGNAL("clicked()") , self.createMateColorShaderUI )
		self.connect( self.blackNoAlpha_btn         , QtCore.SIGNAL("clicked()") , lambda shader=["BLACK_NO_ALPHA",[0,0,0,0]]: self.createAssignColor(shader) )
		self.connect( self.color_btn                , QtCore.SIGNAL("clicked()") , self.createColorShaderUI )
		self.connect( self.aiStandard_btn           , QtCore.SIGNAL("clicked()") , self.createAssignAiStandard )
		self.connect( self.occ_btn                  , QtCore.SIGNAL("clicked()") , self.createAssignOcclusion )
		self.connect( self.uv_btn                   , QtCore.SIGNAL("clicked()") , self.createAssignUv )
		self.connect( self.shadow_btn               , QtCore.SIGNAL("clicked()") , self.createAssignShadow )
		self.connect( self.zdepth_btn               , QtCore.SIGNAL("clicked()") , self.createAssignZdepth )
		self.connect( self.removeShaderOverride_btn , QtCore.SIGNAL("clicked()") , self.removeShaderOverride )
		#RENDER OVERRIDES
		self.connect( self.applyStatsOverride_btn   , QtCore.SIGNAL("clicked()") , self.applyRenderStats )
		#LIGHTING
		self.connect( self.isolateObject_btn        , QtCore.SIGNAL("clicked()") , self.isolateSelectedObjects )
		self.connect( self.isolateLight_btn         , QtCore.SIGNAL("clicked()") , self.isolateSelectedLight )
		self.connect( self.selectObjectByLight_btn  , QtCore.SIGNAL("clicked()") , self.selectObjIllByLight )
		self.connect( self.selectLightsInLayer_btn  , QtCore.SIGNAL("clicked()") , self.selectLightsInLayer )
		self.connect( self.selectLightByObject_btn  , QtCore.SIGNAL("clicked()") , self.selectLitIllObj )
		self.connect( self.makeLightLink_btn        , QtCore.SIGNAL("clicked()") , self.makeLightLink )
		self.connect( self.breakLightLink_btn       , QtCore.SIGNAL("clicked()") , self.breakLightLink )
		self.connect( self.applyLightSample_btn     , QtCore.SIGNAL("clicked()") , self.changeSampleLights )
		self.connect( self.ipr_btn                  , QtCore.SIGNAL("clicked()") , self.removeAllObjectsToLayer )
		#RENDER SETTINGS
		self.connect( self.lowRenderSettings_btn    , QtCore.SIGNAL("clicked()") , self.removeAllObjectsToLayer )
		self.connect( self.highRenderSettings_btn   , QtCore.SIGNAL("clicked()") , self.removeAllObjectsToLayer )
		self.connect( self.saveRenderSettings_btn   , QtCore.SIGNAL("clicked()") , self.removeAllObjectsToLayer )
		self.connect( self.loadRenderSettings_btn   , QtCore.SIGNAL("clicked()") , self.removeAllObjectsToLayer )
		self.connect( self.aovsOff_btn              , QtCore.SIGNAL("clicked()") , partial( self.aovsSwitch, False ) )
		self.connect( self.aovsOn_btn               , QtCore.SIGNAL("clicked()") , partial( self.aovsSwitch, True ) )
		self.connect( self.overridesOff_btn         , QtCore.SIGNAL("clicked()") , lambda state=False: self.setOverrides(state) )
		self.connect( self.overridesOn_btn          , QtCore.SIGNAL("clicked()") , lambda state=True: self.setOverrides(state) )
		arnoldSettings = mn.Node( 'defaultArnoldRenderOptions' )
		#SPINBOXES  
		spinBoxes = [ 
				self.AASamples_sb,              
				self.GIDiffuseSamples_sb,       
				self.GIGlossySamples_sb,        
				self.GIRefractionSamples_sb,    
				self.GITotalDepth_sb,           
				self.GIDiffuseDepth_sb,         
				self.GIGlossyDepth_sb,          
				self.GIReflectionDepth_sb,      
				self.GIRefractionDepth_sb,      
				self.autoTransparencyDepth_sb  
				]
		for s in spinBoxes:
			att = arnoldSettings.attr( str( s.objectName() ).replace( '_sb', '' ) )
			mc.scriptJob( ac = [att.fullname, partial( self.updateLighterUI )], p = 'ligther_Helper_WIN' )
			self.connect( s, QtCore.SIGNAL("valueChanged(int)") , partial( self.renderSettingsSpinBoxApply, s ) )
		#CHECBOXES stateChanged
		chBoxes = [
				self.ignoreTextures_chb,    
				self.ignoreAtmosphere_chb,  
				self.ignoreShadows_chb,     
				self.ignoreDisplacement_chb,
				self.ignoreSmoothing_chb,   
				self.ignoreSss_chb,         
				self.ignoreDof_chb,         
				self.ignoreShaders_chb,     
				self.ignoreLights_chb,      
				self.ignoreSubdivision_chb,
				self.ignoreBump_chb,        
				self.ignoreMotionBlur_chb,  
				#self.ignoreMis_chb,         
				]
		for c in chBoxes:
			att = arnoldSettings.attr( str( c.objectName() ).replace( '_chb', '' ) )
			mc.scriptJob( ac = [att.fullname, partial( self.updateLighterUI )], p = 'ligther_Helper_WIN' )
			self.connect( c, QtCore.SIGNAL("stateChanged(int)") , partial( self.renderSettingsChecboxApply, c ) )
		#AOV LIST
		self.aovs_lw.itemChanged.connect( self.setAovsState )
		#EXPORT
		self.connect( self.exportRenderLayers_btn   , QtCore.SIGNAL("clicked()") , self.exportRenderData )
		self.connect( self.importRenderLayers_btn   , QtCore.SIGNAL("clicked()") , self.importRenderData )
		#TOOLBAR
		self.connect( self.actionSpot   , QtCore.SIGNAL("triggered()") , partial( self.createLight, "spotLight" ) )
		self.connect( self.actionDirectional   , QtCore.SIGNAL("triggered()") , partial( self.createLight, "directionalLight" ) )
		self.connect( self.actionPoint   , QtCore.SIGNAL("triggered()") , partial( self.createLight, "pointLight" ) )
		self.connect( self.actionArea   , QtCore.SIGNAL("triggered()") , partial( self.createLight, "areaLight" ) )
		self.connect( self.actionVolume   , QtCore.SIGNAL("triggered()") , partial( self.createLight, "volumeLight" ) )
		self.connect( self.actionAmbient   , QtCore.SIGNAL("triggered()") , partial( self.createLight, "ambientLight" ) )
		self.connect( self.actionRenderGlobals  , QtCore.SIGNAL("triggered()") , self.openRenderSettings )
		self.connect( self.actionRenderView  , QtCore.SIGNAL("triggered()") , self.openRenderView )
		self.connect( self.actionLookThrough  , QtCore.SIGNAL("triggered()") , self.lookThroughSelected)

	def _addAllAovs(self):
		"""add all aovs to the scene and in the list"""
		aov.addAllAovs()
		if not mn.Node( 'aiAOV_motionvector' ).a.defaultValue.input:
			aov.createMotionVectorAov()
		aovs = aov.aovsInScene()
		for ao in aovs:
			item = QtGui.QListWidgetItem( ao.a.name.v )
			if ao.a.enabled.v: 
				state = QtCore.Qt.Checked 
			else: 
				state = QtCore.Qt.Unchecked
			item.setCheckState( state )
			item.setData(32, ao )
			self.aovs_lw.addItem( item )

	def updateLighterUI(self):
		"""update Ui based on render layer"""
		with undo.Undo():
			arnoldSettings = mn.Node( 'defaultArnoldRenderOptions' )
			spinBoxes = [ 
					self.AASamples_sb,              
					self.GIDiffuseSamples_sb,       
					self.GIGlossySamples_sb,        
					self.GIRefractionSamples_sb,    
					self.GITotalDepth_sb,           
					self.GIDiffuseDepth_sb,         
					self.GIGlossyDepth_sb,          
					self.GIReflectionDepth_sb,      
					self.GIRefractionDepth_sb,      
					self.autoTransparencyDepth_sb  
					]
			for s in spinBoxes:
				s.setValue( arnoldSettings.attr( str( s.objectName() ).replace( '_sb', '' ) ).v )

			chBoxes = [
					self.ignoreTextures_chb,    
					self.ignoreAtmosphere_chb,  
					self.ignoreShadows_chb,     
					self.ignoreDisplacement_chb,
					self.ignoreSmoothing_chb,   
					self.ignoreSss_chb,         
					self.ignoreDof_chb,         
					self.ignoreShaders_chb,     
					self.ignoreLights_chb,      
					self.ignoreSubdivision_chb,
					self.ignoreBump_chb,        
					self.ignoreMotionBlur_chb,  
					#self.ignoreMis_chb,         
					]
			for c in chBoxes:
				c.setChecked( arnoldSettings.attr( str( c.objectName() ).replace( '_chb', '' ) ).v )

			for v in range( self.aovs_lw.count() ):
				i = self.aovs_lw.item( v )
				if uiH.USEPYQT:
					aovNode = i.data(32).toPyObject()
				else:
					aovNode = i.data(32)
				if aovNode.a.enabled.v:
					i.setCheckState(QtCore.Qt.Checked)
				else:
					i.setCheckState(QtCore.Qt.Unchecked)


	##########################
	#OBJECTS
	def addObjectToLayer(self):
		"""docstring for addObjectToLayer"""
		rlay = rlayer.current()
		rlay.add( mn.ls( sl = True ) )

	def removeObjectToLayer(self):
		"""docstring for removeObjectToLayer"""
		rlay = rlayer.current()
		rlay.remove( mn.ls( sl = True ) )

	def removeAllObjectsToLayer(self):
		"""docstring for remove"""
		rlay = rlayer.current()
		rlay.clean()


	##########################
	#OBJECTS QUALITY
	def getTexturesForSelection(self):
		"""docstring for getTexturesForSelection"""
		textures = []
		for n in mn.ls(sl = True):
			for t in mn.listHistory( n.shader ):
				if t.type == 'file':
					textures.append( t )
		return textures

	def toLow(self):
		manager = tm.Manager()
		manager.toLow( self.getTexturesForSelection() )
	
	def toMid(self):
		manager = tm.Manager()
		manager.toMid( self.getTexturesForSelection() )
		
	def toHigh(self):
		manager = tm.Manager()
		manager.toHigh( self.getTexturesForSelection() )
		
	def dispOff(self):
		for n in mn.ls( sl = True ):
			n.shape.a.aiDispHeight.v = 0
		
	def dispOn(self):
		for n in mn.ls( sl = True ):
			n.shape.a.aiDispHeight.v = 1

	def plusSub(self):
		for n in mn.ls( sl = True ):
			n.shape.a.aiSubdivType.v = 1
			n.shape.a.aiSubdivIterations.v = 1 + n.shape.a.aiSubdivIterations.v
		
	def zeroSub(self):
		for n in mn.ls( sl = True ):
			n.shape.a.aiSubdivType.v = 0
		
	def minusSub(self):
		for n in mn.ls( sl = True ):
			if not n.shape.a.aiSubdivIterations.v == 0:
				n.shape.a.aiSubdivType.v = 1
				n.shape.a.aiSubdivIterations.v = n.shape.a.aiSubdivIterations.v - 1

	############################
	#SHADING
	def createMateColorShaderUI(self):
		"""ui to create a custom color, then calls createAssignShader"""
		mc.layoutDialog( ui = self.assignCustomMateColorUI )

	def assignCustomMateColorUI( self, colorMat = 'RL_SOMECOLOR', col = (1,1,1)):
		mc.columnLayout()
		mc.colorSliderGrp( 'customColorColorSlider', rgb = col )
		mc.checkBox( 'customAlpha_chb', l = 'With Alpha', v = True )
		mc.rowColumnLayout( nc = 2 )
		mc.button( l = 'Create', w = 120, c = self.assignNewMateColorUi )
		mc.button( l = 'Cancel', w = 120, c = self.dismissCustomColorUI )

	def assignNewMateColorUi(self, *args):
		"""docstring for assignNewMateColorUi"""
		col = mc.colorSliderGrp( 'customColorColorSlider', q = 1, rgb = 1 )
		alph = mc.checkBox( 'customAlpha_chb', q = True, v = True )
		mc.layoutDialog( dismiss="Cancel" )
		self.assignNewMateColor( col, alph )
	
	def assignNewMateColor(self, col = (0,0,0), alph = 1):
		"""turn On Mate for Arnold and set color! for selected objects"""
		for n in mn.ls( sl = True ):
			eng = n.shader
			if eng:
				try:
					sha = eng.a.surfaceShader.input.node
					sha.a.aiEnableMatte.overrided = 1
					sha.a.aiEnableMatte.v = 1
					sha.a.aiMatteColor.overrided = 1
					sha.a.aiMatteColor.v = [col[0],col[1],col[2]]
					sha.a.aiMatteColorA.overrided = 1
					sha.a.aiMatteColorA.v = alph
				except:
					continue

	def createColorShaderUI(self):
		"""ui to create a custom color, then calls createAssignShader"""
		mc.layoutDialog( ui = self.assignCustomColorUI )

	def assignCustomColorUI( self, colorMat = 'RL_SOMECOLOR', col = (1,1,1)):
		mc.columnLayout()
		mc.textFieldGrp( 'customColorTextField',
						 l   = 'Shader Name:',
						 tx  = colorMat,
						 ct2 = ['left','left'],
						 cl2 = ['left','left'],
						 cw2 = [80,160]
						 )
		mc.colorSliderGrp( 'customColorColorSlider', rgb = col )
		mc.checkBox( 'customAlpha_chb', l = 'With Alpha', v = True )
		mc.rowColumnLayout( nc = 2 )
		mc.button( l = 'Create', w = 120, c = self.assignNewColor )
		mc.button( l = 'Cancel', w = 120, c = self.dismissCustomColorUI )

	def dismissCustomColorUI(self, *args):
		"""docstring for dismissCustomColorUI"""
		mc.layoutDialog( dismiss="Cancel" )

	def assignNewColor(self, *args):
		colorMat = mc.textFieldGrp( 'customColorTextField', q = 1, tx = 1 )
		col = mc.colorSliderGrp( 'customColorColorSlider', q = 1, rgb = 1 )
		alph = mc.checkBox( 'customAlpha_chb', q = True, v = True )
		col.append( alph )
		mc.layoutDialog( dismiss="Cancel" )
		if mc.objExists( colorMat ):
			res = mc.confirmDialog( title='Confirm', message='There is a shader with this name, do you want to use it?', button=['Yes','No'], defaultButton='Yes', cancelButton='No', dismissString='No' )
			if res == 'Yes':
				self.createAssignColor( [colorMat, col] ) #ASSIGN COLOR
			else:
				self.assignCustomColorUI( [colorMat, col] ) #GO BACK TO SELECT COLOR
		else:
			self.createAssignColor( [colorMat, col] ) #ASSIGN COLOR

	def createAssignColor(self, shader):
		"""docstring for createShader"""
		sels = mn.ls( sl = True )
		shaderName = str(shader[0])
		shaderColor = shader[1]
		shaderNode = mn.Node( shaderName )
		if not shaderNode.exists:
			shaderNode = mn.createNode( 'surfaceShader', n = shaderName )
			shaderNode.a.outColor.v = [shaderColor[0], shaderColor[1], shaderColor[2]]
			shaderNode.a.outMatteOpacity.v = [shaderColor[3],shaderColor[3],shaderColor[3]]
		self.applyShaderToSel( shaderNode, sels )

	def createAssignOcclusion(self):
		"""docstring for fname"""
		sels = mn.ls( sl = True )
		shaderNode = mn.Node( 'OCC_MAT' )
		if not shaderNode.exists:
			shaderNode = mn.createNode( 'aiAmbientOcclusion', n = 'OCC_MAT' )
		self.applyShaderToSel( shaderNode, sels )

	def createAssignAiStandard(self):
		"""docstring for createAssignAiStandard"""
		sels = mn.ls( sl = True )
		shaderNode = mn.Node( 'aiStandard_MAT' )
		if not shaderNode.exists:
			shaderNode = mn.createNode( 'aiStandard', n = 'aiStandard_MAT' )
		self.applyShaderToSel( shaderNode, sels )

	def applyShaderToSel( self, shader, sels ):
		rlay = rlayer.current()
		if not sels:
			rlay.overridedShader = shader
		else:
			sels.select()
			mc.hyperShade( a = shader.name )
		self.applyShaderToHair( shader, sels )
	
	def applyShaderToHair(self,shader, sels):
		"""docstring for applyShaderToHair"""
		hairSel = []
		if sels:
			for s in sels:
				hai = mn.listRelatives( s.name, type = 'hairSystem', ad = True )
				if hai:
					hairSel.extend( hai )
				try:
					hai = mn.listRelatives( s.name, type = 'shaveHair', ad = True )
					if hai:
						hairSel.extend( hai )
				except:
					pass
		else:
			hairSel = mn.ls( typ = 'hairSystem' )
			try:
				hairSel.extend( mn.ls( typ = 'shaveHair' ) )
			except:
				pass
		if not hairSel:
			return
		for h in hairSel:
			h.a.aiHairShader.overrided = True
			try:
				shader.a.outColor >> h.a.aiHairShader
			except:
				continue

	def createAssignUv(self):
		"""docstring for fname"""
		sels = mn.ls( sl = True )
		shaderNode = mn.Node( 'UV_MAT' )
		if not shaderNode.exists:
			shaderNode = mn.createNode( 'aiUtility', n = 'UV_MAT' )
			shaderNode.a.colorMode.v = 5
			shaderNode.a.shadeMode.v = 2
		self.applyShaderToSel( shaderNode, sels )

	def createAssignShadow(self):
		"""create and assign a aiShadowCatcher to selection"""
		sels = mn.ls( sl = True )
		shaderNode = mn.Node( 'SHADOW_MAT' )
		if not shaderNode.exists:
			shaderNode = mn.createNode( 'aiShadowCatcher', n = 'SHADOW_MAT' )
		self.applyShaderToSel( shaderNode, sels )

	def createAssignZdepth(self):
		"""docstring for fname"""
		sels = mn.ls( sl = True )
		shaderNode = mn.Node( 'ZDEPTH_MAT' )
		if not shaderNode.exists:
			with undo.Undo():
				shaderNode = mn.createNode( 'surfaceShader'  , n = 'ZDEPTH_MAT' )
				rangeNode  = mn.createNode( 'setRange'       , n = 'range_ZDEPTH_RNG' )
				multyNode  = mn.createNode( 'multiplyDivide' , n = 'multy_ZDEPTH_MUL' )
				rampNode   = mn.createNode( 'ramp'           , n = 'ramp_ZDEPTH_RMP' )
				sampleNode = mn.createNode( 'samplerInfo'    , n = 'ramp_ZDEPTH_RMP' )
				#make connections
				sampleNode.a.pointCameraZ   >> multyNode.a.input1X
				multyNode.a.output          >> rangeNode.a.value
				multyNode.a.input2X.v = -1
				rangeNode.a.outValueX       >> rampNode.a.uCoord
				rangeNode.a.outValueX       >> rampNode.a.vCoord
				rangeNode.a.oldMaxX.v = 100
				rampNode.a.outColor         >> shaderNode.a.outColor
				rampNode.attr( 'colorEntryList[0].position' ).v = 0
				rampNode.attr( 'colorEntryList[0].color' ).v = [0,0,0]
				rampNode.attr( 'colorEntryList[1].position' ).v = 1
				rampNode.attr( 'colorEntryList[1].color' ).v = [1,1,1]
		self.applyShaderToSel( shaderNode, sels )

	def removeShaderOverride(self):
		"""docstring for fname"""
		sel = mn.ls( sl = True )
		rlay = rlayer.current()
		if not sel:
			rlay.removeOverridedShader()
		else:
			with undo.Undo():
				for s in sel:
					childs = s.allchildren
					if childs:
						for c in childs:
							shap = c.shape
							if shap:
								mc.editRenderLayerAdjustment( shap.name + '.instObjGroups', remove = True )
					shap = s.shape
					if shap:
						mc.editRenderLayerAdjustment( shap.name + '.instObjGroups', remove = True )

	###########################
	#RENDER STATS OVERRIDE

	def applyRenderStats(self):
		"""apply settings to render stats for selected objects"""
		sel = mn.ls( sl = True )
		if not sel:
			return
		items = [self.shapeOverrides_01_lay.itemAt(i) for i in range(self.shapeOverrides_01_lay.count())] 
		items.extend( [self.shapeOverrides_02_lay.itemAt(i) for i in range(self.shapeOverrides_02_lay.count())] )
		valsDict = {}
		for w in items:
			valsDict[str( w.widget().text() )] = w.widget().isChecked()
		with undo.Undo():
			for s in sel:
				childs = s.allchildren
				sha = s.shape
				if childs:
					for c in childs:
						shap = c.shape
						if shap:
							for v in valsDict.keys():
								value = valsDict[ v ]
								try:
									if not value == shap.attr( v ).v:
										shap.attr( v ).overrided = True
										shap.attr( v ).v = valsDict[ v ]
								except:
									continue
				for v in valsDict.keys():
					try:
						value = valsDict[ v ]
						if not value == sha.attr( v ).v:
							sha.attr( v ).overrided = True
							sha.attr( v ).v = valsDict[ v ]
					except:
						continue

	###########################
	#LIGHTING
	def isolateSelectedObjects(self):
		"""isolate Selecetd objects"""
		sel = mn.ls( sl = True, dag = True, typ = ['transform'], l = 1 )
		self.desisolateObjects()
		if not sel:
			return
		self.isolatedObjects = [o for o in mn.ls( typ = 'transform' ) if o.a.v] #only visibile transforms
		for o in self.isolatedObjects:
			o.a.v.v = 0
		for o in sel:
			o.a.v.v = 1

	def desisolateObjects(self):
		"""set back objects visibility on"""
		for o in self.isolatedObjects:
			o.a.v.v = True

	def isolateSelectedLight(self):
		"""isolate Selected Light"""
		sel = mn.ls( sl = True, dag = True, typ = ['light','aiAreaLight','aiSkyDomeLight','aiVolumeScattering'], l = 1 )
		self.desisolateLight() #back all to normal before we make a light isolated
		self.isolateLight_btn.setStyleSheet('QPushButton {background-color: rgb(255, 0, 0)}')
		if not sel:
			self.isolateLight_btn.setStyleSheet('QPushButton {background-color: rgb(0, 170, 255)}')
			return
		lits = mn.ls( typ=['light','aiAreaLight','aiSkyDomeLight','aiVolumeScattering'], l=1 )
		self.isolatedLights = []
		for l in lits:
			try:
				if l.parent.a.v:
					self.isolatedLights.append( l.parent )
					l.parent.a.v.v = 0
			except:
				continue
		for l in sel:
			l.parent.a.v.v = 1

	def desisolateLight(self):
		"""desisolate all lights from past isolate"""
		for l in self.isolatedLights:
			try:
				l.a.v.v = 1
			except:
				continue

	def createLight(self, light):
		"""create light on camera position if we can know what camera use"""
		if light == 'areaLight':
			lit = mn.Node( mc.shadingNode( light, asLight = True ) )
		else:
			lit = mn.Node( mm.eval( light ) ).parent
		cam = self.getCurrentCamera()
		if cam:
			cons = mn.Node( mc.parentConstraint( cam.name, lit.name )[0] )
			cons.delete()
		
	def openRenderSettings(self):
		"""open render settings ui"""
		mm.eval( 'unifiedRenderGlobalsWindow' )

	def openRenderView(self):
		"""open render view ui"""
		mm.eval( 'RenderViewWindow' )

	def selectLightsInLayer(self):
		"""select lights in render layer"""
		lits = rlayer.current().lights
		if lits:
			lits.select()

	def selectObjIllByLight(self):
		"""select objects illuminated by selected Light"""
		mm.eval( 'SelectObjectsIlluminatedByLight();' )

	def selectLitIllObj(self):
		"""select lights illuminating object"""
		mm.eval( 'SelectLightsIlluminatingObject();' )

	def makeLightLink(self):
		"""make a light link in selected objects"""
		mm.eval( 'lightlink -make -useActiveLights -useActiveObjects;' )

	def breakLightLink(self):
		"""break a light link for selected objects"""
		mm.eval( 'lightlink -break -useActiveLights -useActiveObjects;' )

	def changeSampleLights(self):
		"""change the samples in selected lights, if none is selected change in all"""
		lits = mn.ls( sl = True, dag = True, typ = ['light', 'aiAreaLight'] )
		if not lits:
			lits = mn.ls( typ = ['light', 'aiAreaLight'] )
		if not lits:
			return
		val = self.lightSamples_sb.value()
		for l in lits:
			l.a.aiSamples.v = val

	###########################
	#RENDER SETTINGS
	def setOverrides(self, state ):
		"""turn all checkboxes on"""
		chBoxes = [
				self.ignoreTextures_chb,    
				self.ignoreAtmosphere_chb,  
				self.ignoreShadows_chb,     
				self.ignoreDisplacement_chb,
				self.ignoreSmoothing_chb,   
				self.ignoreSss_chb,         
				self.ignoreDof_chb,         
				self.ignoreShaders_chb,     
				self.ignoreLights_chb,      
				self.ignoreSubdivision_chb,
				self.ignoreBump_chb,        
				self.ignoreMotionBlur_chb,  
				#self.ignoreMis_chb,         
				]
		for c in chBoxes:
			c.setChecked( state )
	
	def renderSettingsSpinBoxApply(self, spinbox):
		"""change settings for spinBox"""
		over = self.overrideRenderSettings_chb.isChecked()
		arnoldSettings = mn.Node( 'defaultArnoldRenderOptions' )
		att = arnoldSettings.attr( str( spinbox.objectName() ).replace( '_sb', '' ) )
		val = spinbox.value()
		if not att.v == val:
			att.overrided = over
			att.v = val

	def renderSettingsChecboxApply(self, checkbox):
		"""change setting for checkbox"""
		over = self.overrideRenderSettings_chb.isChecked()
		arnoldSettings = mn.Node( 'defaultArnoldRenderOptions' )
		att = arnoldSettings.attr( str( checkbox.objectName() ).replace( '_chb', '' ) )
		val = checkbox.isChecked()
		if not att.v == val:
			att.overrided = over
			att.v = val

	#AOVS
	def setAovsState(self, item):
		"""change state in aovs"""
		over = self.overrideRenderSettings_chb.isChecked()
		if uiH.USEPYQT:
			aovNode = item.data(32).toPyObject()
		else:
			aovNode = item.data(32)
		aovNode.a.enabled.overrided = over
		aovNode.a.enabled.v = item.checkState() == QtCore.Qt.Checked

	def aovsSwitch(self, state):
		"""set all aovs to a specific state"""
		for index in xrange(self.aovs_lw.count()):
			item = self.aovs_lw.item( index )
			if state:
				state = QtCore.Qt.Checked
			else:
				state = QtCore.Qt.Unchecked
			item.setCheckState( state )

	###########################
	# EXTRAS
	def closeEvent(self, event):
		"""custom close"""
		print 'custom close'
		self.desisolateLight()
		event.accept()
	
	def loadArnold(self):
		version = mc.about(v = True).split()[0]
		if mc.pluginInfo('mtoa', q=1, l=1):
			print "Arnold is loaded.\n";
		else:
			mc.loadPlugin("C:/solidAngle/mtoadeploy/" + version + "/plug-ins/mtoa.mll")
		if not mn.Node( 'defaultArnoldRenderOptions' ).exists:
			cor.createOptions()
		mc.setAttr("defaultRenderGlobals.currentRenderer", "arnold", type="string")
		mc.setAttr( "defaultViewColorManager.imageColorProfile", 2 )
		mc.setAttr( "defaultArnoldRenderOptions.display_gamma", 1 )
		mc.setAttr( "defaultArnoldRenderOptions.shader_gamma" ,1 )
		mc.setAttr( "defaultArnoldRenderOptions.texture_gamma", 1 )
		mc.setAttr( "defaultArnoldRenderOptions.range_type" ,0 )
		mc.setAttr( "defaultArnoldDriver.halfPrecision", 1 )
		mc.setAttr( "defaultArnoldDriver.preserveLayerName", 1)
		mc.setAttr( "defaultRenderGlobals.extensionPadding", 4)
		mc.setAttr( "defaultRenderGlobals.animation", 1)
		mc.setAttr( "defaultRenderGlobals.outFormatControl", 0 )
		mc.setAttr( "defaultRenderGlobals.putFrameBeforeExt", 1 )
		mc.setAttr( "defaultRenderGlobals.periodInExt", 1)
		mc.setAttr( "defaultArnoldDriver.mergeAOVs", 1 )
		mc.setAttr( "defaultArnoldRenderOptions.use_existing_tiled_textures", 1 )
		try:
			for c in mn.ls( typ = 'camera' ):
				c.a.aiShutterEnd.v = 0
				c.a.motionBlurOverride.v = 1
		except:
			pass
		
		

	def getCurrentCamera(self):
		pan = mc.getPanel(wf=1)
		cam = ""
		if ( "modelPanel" == mc.getPanel(to=pan) ):
			cam = mc.modelEditor(pan,q=1,camera=1);
			print mc.nodeType(cam)
		if(cam == ""):
			return None
		return mn.Node( cam );

	###########################
	# EXPORT / IMPORT
	def exportRenderData(self):
		"""export render Data from scene"""
		pathDir = self.getDirForRenderData()
		if not os.path.exists( pathDir ):
			os.makedirs( pathDir )
		rlExporter = rlExp.RenderLayerExporter( pathDir )
		rlExporter.export(  self.renderLayersOpt_chb.isChecked(), 
							self.lightsOpt_chb.isChecked(),
							self.aovsOpt_chb.isChecked(),
							self.shadersOpt_chb.isChecked(),
							self.masterSettings_chb.isChecked()
							)

	def importRenderData(self):
		"""import render Data to scene"""
		asset = ''
		searchAndReplace = [str( self.searchAsset_le.text() ), str( self.replaceAsset_le.text() )]
		print searchAndReplace
		pathDir = self.getDirForRenderData()
		if self.onlySelected_chb.isChecked():
			sel = mc.ls( sl = True )
			if sel:
				if ':' in sel[0]:
					asset = sel[0][ : -len( sel[0].split( ':' )[-1] ) ]
		rlExporter = rlExp.RenderLayerExporter( pathDir )
		rlExporter.importAll(  self.renderLayersOpt_chb.isChecked(), 
							self.lightsOpt_chb.isChecked(),
							self.shadersOpt_chb.isChecked(),
							self.aovsOpt_chb.isChecked(),
							self.masterSettings_chb.isChecked(),
							asset,
							searchAndReplace
							)
	
	def getDirForRenderData(self):
		"""get the directory for the render layer data"""
		if self.useSceneForlder_chb.isChecked():
			pathDir = mfl.currentFile().dirPath + '/Data/'
		else:
			pathDir = str(QtGui.QFileDialog.getExistingDirectory(self, "Select Directory"))
		return pathDir
		

	def lookThroughSelected(self):
		"""look Through To selected object"""
		mc.lookThru( mc.ls(sl = True)[0], nc=1.0, fc=5000.0)

def main():
	"""call this from maya"""
	if mc.window( 'ligther_Helper_WIN', q = 1, ex = 1 ):
		mc.deleteUI( 'ligther_Helper_WIN' )
	PyForm=LighterHelperUI()
	PyForm.show()

