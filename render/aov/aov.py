import general.mayaNode.mayaNode as mn
import mtoa.aovs as aovs


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
