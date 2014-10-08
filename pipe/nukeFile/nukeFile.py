import os
try:
	import nuke
	import nukescripts
except:
	pass
import pipe.file.file as fl
import re

class nukeFile(fl.File):
	"""docstring for nukeFile"""
	def __init__(self, path):
		super(nukeFile, self).__init__(path)
		
	def save(self):
		"""docstring for save"""
		nuke.scriptSaveAs( self.path )

	def open(self):
		"""docstring for open"""
		nukescripts.utils.executeInMainThread(nuke.scriptOpen,(self.path,))
		#nuke.scriptOpen( self.path )

	@property
	def nodes(self):
		"""return all the files inside nuke"""
		pat = re.compile( '\n(?P<Path>[A-Z]\w+) {(\n(?: .+\n)+)}' )
		# ((?P<Attr>\w+) (.+)\n+)+ \n}
		search = pat.findall
		with open(self.path) as fl:
			matches = search(fl.read())
			refs = [ ma for ma in matches]
		nukeTree = []
		for r in refs:
			n = Node( r[0] )
			for a in r[1].split( '\n' ):
				spli = a.split( ' ', 1 )
				if len(spli) == 2:
					finalSpli = spli[1].split( ' ', 1 )
					attr = finalSpli[0]
					value = finalSpli[1]
					n.addAttr( attr, value )
			nukeTree.append( n )
		return nukeTree

	@property
	def start(self):
		"""docstring for start"""
		return self.root.attrs[ 'frame' ]

	@property
	def end(self):
		"""docstring for start"""
		return self.root.attrs[ 'last_frame' ]

	@property
	def fps(self):
		"""docstring for fps"""
		return self.root.attrs[ 'fps' ]

	@property
	def dependences(self):
		"""docstring for dependences"""
		deps = []
		for n in self.nodes:
			if n.Type != 'Write':
				for a in n.attrs:
					if 'file' == a:
						deps.append( n.attrs[a] )
		return deps

	@property
	def root(self):
		"""docstring for root"""
		for n in self.nodes:
			if n.Type == 'Root':
				return n

class Node(object):
	"""docstring for Node"""
	def __init__(self, Type):
		self._Type = Type
		self._attrs = {}

	@property
	def Type(self):
		"""docstring for Type"""
		return self._Type

	@property
	def attrs(self):
		"""docstring for attrs"""
		return self._attrs

	def addAttr(self, attrname, value):
		"""docstring for addAttr"""
		self._attrs[attrname] = value
	
		
		
