import general.mayaNode.mayaNode as mn
import mtoa.aovs as aovs
import pymel.core as pm

def aovsInScene():
	"""return all the created aovs in scene"""
	aovs = mn.ls( typ = 'aiAOV' )
	return aovs

def allAovs():
	"""return all the aovs available to be created"""
	aovList = list(set(aovs.getRegisteredAOVs(builtin = True)))
	return aovList

def addAllAovs():
	"""add all the aovs nodes to the scene"""
	inter = aovs.AOVInterface()
	for ao in allAovs():
		aovNode = mn.Node( 'aiAOV_' + ao )
		if aovNode.exists:
			continue
		aovNodeName = addAOV( ao )
		aovNode.a.enabled.v = False #TURN IT OFF

def create(  customAovName = '' ,name ='' , typ = '' , enabled = '' ):
	"""create Aov Node"""
	if mn.Node( customAovName ).exists:
		return
	customAov = pm.createNode( 'aiAOV' )
	customAov.setAttr( 'name', name       )
	customAov.setAttr( 'enabled', enabled )
	customAov.setAttr( 'type', typ        )
	arnoldRenderGlobals = pm.ls( 'defaultArnoldRenderOptions' )[0]
	if not arnoldRenderGlobals.aovList.getArrayIndices():
		nextIndex = 0
	else:
		nextIndex = max(arnoldRenderGlobals.aovList.getArrayIndices())+1
	customAov.message >> arnoldRenderGlobals.aovList[nextIndex]
	customAov.rename( customAovName )
	return mn.Node( customAovName )

def addAOV( aovName, aovType = None ):
	"""docstring for addAov"""
	if aovType is None:
		aovType = aovs.getAOVTypeMap().get(aovName, 'rgba')
	if not isinstance(aovType, int):
		aovType = dict(aovs.TYPES)[aovType]
	aovNode = pm.createNode('aiAOV', name='aiAOV_' + aovName, skipSelect=True)
	out = aovNode.attr('outputs')[0]

	pm.connectAttr('defaultArnoldDriver.message', out.driver)
	filter = aovs.defaultFiltersByName.get(aovName, None)
	if filter:
		node = pm.createNode('aiAOVFilter', skipSelect=True)
		node.aiTranslator.set(filter)
		filterAttr = node.attr('message')
		import mtoa.hooks as hooks
		hooks.setupFilter(filter, aovName)
	else:
		filterAttr = 'defaultArnoldFilter.message'
	pm.connectAttr(filterAttr, out.filter)

	aovNode.attr('name').set(aovName)
	aovNode.attr('type').set(aovType)
	base = pm.PyNode('defaultArnoldRenderOptions')
	aovAttr = base.aovs
	nextPlug = aovAttr.elementByLogicalIndex(aovAttr.numElements())
	aovNode.message.connect(nextPlug)
	aov = aovs.SceneAOV(aovNode, nextPlug)
	return aov
