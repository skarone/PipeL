# Python code
import maya.cmds as mc
import maya.OpenMaya as om

def getInstances():
	instances = []
	iterDag = om.MItDag(om.MItDag.kBreadthFirst)
	while not iterDag.isDone():
		instanced = om.MItDag.isInstanced(iterDag)
		if instanced:
			instances.append(iterDag.fullPathName())
		iterDag.next()
	return instances



def uninstance():
	instances = getInstances()
	while len(instances):
		parent = mc.listRelatives(instances[0], parent=True, fullPath=True)[0]
		mc.duplicate(parent, renameChildren=True)
		mc.delete(parent)
		instances = getInstances()
		print instances

