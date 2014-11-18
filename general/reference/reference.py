try:
	import maya.cmds as mc
	import maya.mel as mm
except:
	pass

import general.mayaNode.mayaNode as mn

"""
import general.reference.reference as rf

rf.reloadSelected()
"""

def getReferenceFromSelected():
	"""docstring for getReferenceFromSelected"""
	objs = mn.ls( sl = True )
	references = []
	for obj in objs:
		references.append( Reference( mc.referenceQuery( obj.name, rfn = True ) ) )
	return references

class Reference(mn.Node):
	"""manage reference like objects =)"""
	def __init__(self, refNode):
		super(Reference, self).__init__( refNode )
	
	@property
	def nodes(self):
		"""return the nodes of the reference"""
		return [mn.Node(a) for a in mc.referenceQuery( self.name, nodes=True )]

	def reload(self):
		"""reload reference"""
		mc.file( self.file.path, loadReference = self.name )

	def unload(self):
		"""unload reference"""
		mc.file( self.file.path, ur = self.name )

	def remove(self):
		"""remove reference"""
		mc.file( referenceNode  = self.name, removeReference = True  )

	def duplicate(self):
		"""docstring for duplicate"""
		pass

	def file(self):
		"""return the path of the reference file"""
		return fl.File( mc.referenceQuery( self.name, f = True ) )



def reloadSelected():
	"""reload selected object"""
	#reload reference
	objs = mn.ls( sl = True )
	for obj in objs:
		try:
			referenceNode = mc.referenceQuery( obj.name, rfn = True )
			path = mc.referenceQuery( obj.name, f = True )
			mc.file( path, loadReference = referenceNode )
		except:
			continue

def unloadSelected():
	"""unload selected reference"""
	objs = mn.ls( sl = True )
	for obj in objs:
		try:
			referenceNode = mc.referenceQuery( obj.name, rfn = True )
			path = mc.referenceQuery( obj.name, f = True )
			mc.file( path, ur = referenceNode )
		except:
			continue

def removeSelected():
	"""unload selected reference"""
	objs = mn.ls( sl = True )
	for obj in objs:
		try:
			referenceNode = mc.referenceQuery( obj.name, rfn = True )
			path = mc.referenceQuery( obj.name, f = True )
			mc.file( referenceNode  = referenceNode, removeReference = True  )
		except:
			continue

def loaded():
	"""return al the references that are loaded to the scene"""
	loaded = []
	numLoaded = 0
	refs = mc.file( q = True, r = True )
	for r in refs:
		if not mc.file( r, q = True, dr = True ):
			loaded.append( r )
	return loaded

def unload():
	"""unload reference node"""
	pass

def dupReferenceForSelectedObjects():
	"""
	Duplicate reference of the selected objects, only one time, and copy their edits
	"""
	allreadyDup = []
	for a in mc.ls( sl = True ):
		ap = mc.referenceQuery( a, referenceNode=True, topReference=True )
		if any( ap == r for r in allreadyDup ):
			print 'skipping',a
			continue
		allreadyDup.append( ap )
		edits = mc.referenceQuery( ap , editStrings = True )
		mc.select( a )
		try:
			mm.eval( 'duplicateReference 0 ""' )
		except:
			print 'maya de mierda'
		baseOldName = edits[0][edits[0].find( '|' )+1:edits[0].find( ':' )]
		baseNewName = mc.ls( sl = True )[0].split( ':' )[0]
		for e in edits:
			print '"""""""'
			print e
			print baseOldName,baseNewName
			try:
				mm.eval( e.replace( baseOldName, baseNewName, 1 ) )
			except:
				continue



