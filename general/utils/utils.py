'''
File: utils.py
Author: Ignacio Urruty
Description: general utilities for the pipe
'''
import general.mayaNode.mayaNode as mn
import maya.cmds as mc
import pipe.mayaFile.mayaFile as mfl
import pipe.file.file as fl

def checkDuplicatedNamesInScene():
	"""check if there is duplicated names if exists.. return the nodes"""
	alltrfs = mn.ls( '*', typ = 'transform', r = True )
	dups = []
	for a in alltrfs:
		if '|' in a.name:
			dups.append( a.name )
	alltrfs = mn.ls( '*', typ = 'mesh', r = True )
	for a in alltrfs:
		if '|' in a.name:
			dups.append( a.name )
	if dups:
		mc.warning( 'There are duplicated names in scene' )
		return mn.Nodes( dups )
	return dups

def selectDuplicatedNamesNodes():
	"""selected the duplicated nodes in the scene"""
	nds = checkDuplicatedNamesInScene()
	if nds:
		nds.select()

def checkScene():
	"""check if the current scene is ok in protocol,
	All transformation Freeze.. 
	All grouped in one group..
	All without history
	All with unique name"""
	meshesWithHistory, meshesWithMaterialPerFace = isMeshWithHistory()
	return transformsWithoutFreeze(), isAllInOneGroup(), meshesWithHistory, meshesWithMaterialPerFace, checkDuplicatedNamesInScene()

def transformsWithoutFreeze():
	"""return all the transforms without freeze"""
	alltrfs = mn.ls( '*', typ = 'transform', r = True )
	alltrfs = _removeCamerasFromArray(alltrfs)
	withoutFreeze = []
	for t in alltrfs:
		if any( t.attr( a ).v != 0 for a in ['tx', 'ty', 'tz', 'rx', 'ry', 'rz'] ):
			withoutFreeze.append( t )
		if any( t.attr( a ).v != 1 for a in ['sx', 'sy', 'sz'] ):
			withoutFreeze.append( t )
	return withoutFreeze

def _removeCamerasFromArray(nodes):
	"""remove camera for array"""
	cameras = [ 'front','persp', 'side', 'top' ]
	return mn.Nodes( [ a for a in nodes if not a.name in cameras ] )

def isAllInOneGroup():
	"""return true if there is all in the same group"""
	alltrfs = mn.ls( '|*', typ = 'transform', r = True )
	alltrfs = _removeCamerasFromArray(alltrfs)
	return len( alltrfs ) == 1

def isMeshWithHistory():
	"""return meshes that has history or material assigned by face"""
	withAssignedMaterialByFace = []
	withHistory = []
	for n in mn.ls( typ = 'mesh', ni = True ):
		his = mn.listHistory( n )
		if not len( his ) == 1:
			if any( 'groupId' in h.name for h in his ):
				withAssignedMaterialByFace.append( n )
				print 'This mesh has the material assigned by faces', n.name, his
				if len( his ) == 3:
					continue
			if any( 'shaveHair' in h.type for h in his ):
				print 'This mesh is related with Shave and Hair cut', n.name, his
				continue
			withHistory.append( n )
	return withHistory, withAssignedMaterialByFace

def withFace():
	"""docstring for withHistory"""
	withHis,withFace = isMeshWithHistory()
	if withFace:
		cur = mfl.currentFile()
		fil = fl.File( 'D:/conCaras/' + cur.name + '.txt' )
		fil.write( 'mierda' )


#####FIXES
def groupAll():
	"""docstring for groupAll"""
	result = mc.promptDialog(
		title         = 'Main Group' ,
		message       = 'Enter Name:',
		button        = ['OK', 'Cancel'],
		defaultButton = 'OK',
		cancelButton  = 'Cancel',
		dismissString = 'Cancel')
	if result == 'OK':
		text = mc.promptDialog(query=True, text=True)
		trfs = mn.ls( '|*', typ = 'transform', r = True )
		trfs = _removeCamerasFromArray( trfs )
		mc.group( trfs, n = text )

def freezeAll():
	"""docstring for freezeAll"""
	nodes = transformsWithoutFreeze()
	if not nodes:
		return
	for n in nodes:
		mc.makeIdentity( n, t = 1, r = 1, s = 1, n = 0, apply = True )

def deleteHistory():
	"""docstring for deleteHistory"""
	meshesWithHistory, meshesWithMaterialPerFace = isMeshWithHistory()
	if meshesWithHistory:
		mc.delete( meshesWithHistory, ch = True)

def autoRename():
	"""docstring for autoRename"""
	nodes = checkDuplicatedNamesInScene()
	if not nodes:
		return
	for n in nodes:
		n.name = n.name.replace( '|', '_' )

def reAssignMaterial():
	"""docstring for reAssignMaterial"""
	meshesWithHistory, meshesWithMaterialPerFace = isMeshWithHistory()
	for n in meshesWithMaterialPerFace:
		his = mn.listHistory( n )
		for h in his:
			if h.type == 'shadingEngine':
				n()
				mc.hyperShade( assign = h.a.surfaceShader.input )

#PANELS
def isolate( node ):
	"""isolate node"""
	node = mn.Node( node )
	currPanel = mc.getPanel( withFocus = True );
	panelType = mc.getPanel( to = currPanel )
	if panelType == 'modelPanel':
		node()
		mc.isolateSelect( state = 1, currPanel )

def desIsolate():
	"""desisolate"""
	currPanel = mc.getPanel( withFocus = True );
	panelType = mc.getPanel( to = currPanel )
	if panelType == 'modelPanel':
		node()
		mc.isolateSelect( state = 0, currPanel )
