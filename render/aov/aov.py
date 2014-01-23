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
		aovNodeName = inter.addAOV( ao )
		aovNode.a.enabled.v = False #TURN IT OFF

def create( name ='' , typ = '' , enabled = '' ):
	"""create Aov Node"""
	if mn.Node( name ).exists:
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
	customAov.rename( name )
	return mn.Node( name )

