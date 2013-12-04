import os
from PyQt4 import QtGui,QtCore, uic

import render.renderlayer.renderlayer as rlayer
reload( rlayer)
import maya.cmds as mc
import maya.mel as mm
import general.mayaNode.mayaNode as mn
import render.aov.aov as aov
reload( aov )
import maya.OpenMayaUI as mui
import sip
from functools import partial

#load UI FILE
PYFILEDIR = os.path.dirname( os.path.abspath( __file__ ) )
uifile = PYFILEDIR + '/lighterHelper.ui'
fom, base = uic.loadUiType( uifile )

def get_maya_main_window( ):
	ptr = mui.MQtUtil.mainWindow( )
	main_win = sip.wrapinstance( long( ptr ), QtCore.QObject )
	return main_win

class LighterHelperUI(base,fom):
	def __init__(self, parent  = get_maya_main_window(), *args ):
		super(base, self).__init__(parent)
		self.setupUi(self)
		self.setObjectName( 'ligther_Helper_WIN' )
		self._makeConnections()
		self._addAllAovs()
		#create an scriptjob thats update the UI on renderlayer change
		mc.scriptJob( e = ["renderLayerManagerChange", partial( self.updateLighterUI )], p = 'ligther_Helper_WIN' )
		self.updateLighterUI()
	
	def _makeConnections(self):
		"""make the connections from the controls to de methods"""
		#OBJECTS
		self.connect( self.addObject_btn            , QtCore.SIGNAL("clicked()") , self.addObjectToLayer )
		self.connect( self.removeObject_btn         , QtCore.SIGNAL("clicked()") , self.removeObjectToLayer )
		self.connect( self.removeAllObjects_btn     , QtCore.SIGNAL("clicked()") , self.removeAllObjectsToLayer )
		#SHADING
		self.connect( self.blackNoAlpha_btn         , QtCore.SIGNAL("clicked()") , lambda shader=["BLACK_NO_ALPHA",[0,0,0,0]]: self.createAssignColor(shader) )
		self.connect( self.color_btn                , QtCore.SIGNAL("clicked()") , self.createColorShaderUI )
		self.connect( self.occ_btn                  , QtCore.SIGNAL("clicked()") , self.createAssignOcclusion )
		self.connect( self.uv_btn                   , QtCore.SIGNAL("clicked()") , self.createAssignUv )
		self.connect( self.shadow_btn               , QtCore.SIGNAL("clicked()") , self.createAssignShadow )
		self.connect( self.zdepth_btn               , QtCore.SIGNAL("clicked()") , self.createAssignZdepth )
		self.connect( self.removeShaderOverride_btn , QtCore.SIGNAL("clicked()") , self.removeShaderOverride )
		#RENDER OVERRIDES
		self.connect( self.applyStatsOverride_btn   , QtCore.SIGNAL("clicked()") , self.applyRenderStats )
		#LIGHTING
		self.connect( self.isolateObject_btn        , QtCore.SIGNAL("clicked()") , self.removeAllObjectsToLayer )
		self.connect( self.isolateLight_btn         , QtCore.SIGNAL("clicked()") , self.removeAllObjectsToLayer )
		self.connect( self.selectObjectByLight_btn  , QtCore.SIGNAL("clicked()") , self.selectObjIllByLight )
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
				self.ignoreMis_chb,         
				]
		for c in chBoxes:
			self.connect( c, QtCore.SIGNAL("stateChanged(int)") , partial( self.renderSettingsChecboxApply, c ) )
		#AOV LIST
		self.aovs_lw.itemChanged.connect( self.setAovsState )
		#EXPORT
		self.connect( self.exportRenderLayers_btn   , QtCore.SIGNAL("clicked()") , self.removeAllObjectsToLayer )
		self.connect( self.importRenderLayers_btn   , QtCore.SIGNAL("clicked()") , self.removeAllObjectsToLayer )


	def _addAllAovs(self):
		"""add all aovs to the scene and in the list"""
		aov.addAllAovs()
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
		mc.undoInfo( swf = False )
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
				self.ignoreMis_chb,         
				]
		for c in chBoxes:
			c.setChecked( arnoldSettings.attr( str( c.objectName() ).replace( '_chb', '' ) ).v )

		mc.undoInfo( swf = True )

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

	############################
	#SHADING
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

	def applyShaderToSel( self, shader, sels ):
		rlay = rlayer.current()
		if not sels:
			rlay.overridedShader = shader
		else:
			sels.select()
			mc.hyperShade( a = shader.name )

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
			mc.undoInfo( ock = True )
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
			mc.undoInfo( cck = True )
		self.applyShaderToSel( shaderNode, sels )

	def removeShaderOverride(self):
		"""docstring for fname"""
		sel = mn.ls( sl = True )
		rlay = rlayer.current()
		if not sel:
			rlay.removeOverridedShader()
		else:
			mc.undoInfo( ock = True )
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
			mc.undoInfo( cck = True )

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
		mc.undoInfo( ock = True )
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
		mc.undoInfo( cck = True )

	###########################
	#LIGHTING
	#TODO ISOLATES!
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
				self.ignoreMis_chb,         
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
		aovNode = item.data(32).toPyObject()
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
	def closeEvent(self, event):
		"""custom close"""
		print 'custom close'
		event.accept()

	


def main():
	"""call this from maya"""
	if mc.window( 'ligther_Helper_WIN', q = 1, ex = 1 ):
		mc.deleteUI( 'ligther_Helper_WIN' )
	PyForm=LighterHelperUI()
	PyForm.show()

