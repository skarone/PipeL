'''
File: mayaNodes.py
Author: Ignacio Urruty
Description: 
	Handle maya nodes, their attributes and namespaces with this module.
	Also has some maya functions that return mayaNode objects instead of strings

How to Use:
Global Methods:
	ls() # return a list of nodes

Nodes:
	node = mn.Node( 'pSpehere1' ) # create node
	Properties:
		node.name                       # return name of node
		node.name = 'newName'           # rename node
		node.exists                     # node Exists?
		node.fullname                   # return a string with the fullname of the node |group1|group2|node
		node.parent                     # return the directly parent node
		node.parent = node2             # set new parent for node if None is node2 then parent to world, also support strings
		node.allparent                  # return an array of all the parent nodes in order
		node.children                   # return all the children of the node
		node.locked = True              # lock node
		v = node.locked                 # return if the node is locked
		node.type                       # node type
		node.namespace                  # return namespace of object if there is one
		node.namespace = newNameSpace   # move node to new namespace, it will create it if not exists
		node.namespace = 'newNameSpace' # move node to new namespace string, it will create it if not exists

	Methods:
		node()                # select node
		node.delete()         # delete node
		node.duplicate()      # duplicate and return a new Node object
		node.istype( 'type' ) # check if the node is a specific type

	TODO:
		node.inputs      # get incomming connections to node
		node.outputs     # get outcomming connections to node
		node.isinstance
		node.isreference

Attributes:
	att = node.a.tx
	att = node.attr( 'tx' )      # setAttr USEFULL for loops when you need to set many attrs
	Properties:
		node.a.tx.node               # get Node
		node.a.tx.v = 10             # setAttr
		node.a.t.v = ( 0.5, 10, 20 ) # setAttr for attributes with children
		node.a.myString.v = 'Hello'  # setAttr for strings also supported =)
		node.a.tx.v += 5             # setAttr Add value tu current, also works with -*/
		v = node.a.tx.v              # getAttr
		node.a.tx.exists             # node attribute Exists?
		node.a.t.children            # In this case return tx, ty and tz
		node.a.tx.type               # attribute type
		node.a.tx.locked = True      # set lock state for node attribute
		v = node.a.tx.locked         # get lock state for node attribute
		v = node.a.tx.max            # get max value if this attr has, None if not
		node.a.tx.max = 10           # set max value
		v = node.a.tx.min            # get min value if this attr has, None if not
		node.a.tx.min = 10           # set min value
		v = node.a.tx.default        # get default value
		node.a.tx.default = 10       # set default value
		node.a.tx.overrided = True   # create an override
		node.a.tx.overrided = False  # remove an override
		v = node.a.tx.overrided      # know if the attribute has an override in current render layer
	Methods:
		node.a.tx.delete()           # delete node attribute
		node.a.custom.add( dataType = None, attributeType = None ) # add a custom attr =)

	Connections:
		Properties:
			node.a.tx.input                        # get input connection to attribute
			node.a.tx.output                       # get output connections to attribute, this allways return an array
			node.a.tx.hascon                       # check if the node attribute has a connection
		Methods:
			node.a.tx >> node2.a.ty                # connectAttr of node to node2
			node.a.tx.connect( node2.a.ty )        # connectAttr of node to node2
			node.a.tx << node2.a.ty                # connectAttr inverse
			node.a.tx.connect( node2.a.ty, False ) # connectAttr inverse
			node.a.tx // node2.a.ty                # disconnectAttr of node to node2
			node.a.tx.disconnect( node2.a.ty )     # disconnectAttr of node to node2
			node.a.tx.disconnect()                 # also support to just break the connection, this will disconnect if this has an input connection
			node.a.tx | node2.a.ty                 # isConnected ? USE THE PIPE
			node.a.tx.isconnected( node2.a.ty )    # isConnected

	TODO:
		node.a.tx.key              # make a key in current frame

Namespace:
	n = Namespace( 'lit' ) # Namespace node
	Properties:
		n.exists        # check if namespace exists
		n.children      # get children namespaces
		n.nodes         # return the nodes that are in the namespace
		n.parent        # get parent of namespace
		n.isempty       # check if namespace is empty
	Methods:
		n.create()      # create namespace if not exists
		n.set()         # set namespace to current
		n.move( other ) # move all the node of namespace to other namespace
		n >> other      # move all the node of namespace to other namespace using >>
		n.remove()      # remove namespace

		Statics:
			Namespace.fromNode( Node ) # return Namespace from Node
			TODO:
				Namespace.all() # return al Namespaces

'''

try:
	import maya.cmds as mc
except:
	print 'running from outside maya'
import re
import sys

import install.pyregistry.pyregistry as pr
try:
	test = pr.queryValue('HKCU', r'Software\Pipel', 'key' )
	if test != '1561532593':
		print 'Are you stealing PipeL? :( Im Shame of You'
		quit()
except:
	print 'Are you stealing PipeL? :( Im Shame of You'
	quit()

"""
SETTINGS:
	Here we can setup some global settings =)
"""
AUTO_CREATE_NAMESPACE    = True  # create namespace if not exists when you try to set to current
FORCE_CONNECTION         = True  # automatically break connection if there is one that you want to connect
AUTO_UNLOCK_ATTR         = False # automatically unlock attribute for connections or for setting value
AUTO_OVERRIDE_ATTR       = False # automatically override attribute if you set it in a renderLayer different than default

def listHistory( strToSearch = None, **args ):
	"""same as listHistory but with Nodes
	
	:param strToSearch: string or mayaNode object to use in list History.. if None use selection
	:param **args: extra arguments the same as original command
	:returns: Nodes object( array of mayaNodes  )"""
	cmd = ''
	if strToSearch:
		if str(strToSearch.__class__) == "<class 'general.mayaNode.mayaNode.Nodes'>":
			cmd += '['
			for n in strToSearch:
				cmd += '"' + n.name + '",'
			cmd += '],'
		else:
			cmd += '"' + str( strToSearch ) + '",'
	for a in args.keys():
		val = args[a]
		if isinstance(val, str):
			cmd += a + '="' + args[a] + '",'
		else:
			cmd += a + '=' + str( args[a] ) + ','
	nodes = eval( "mc.listHistory(" + cmd + ")" )
	if nodes:
		return Nodes( nodes )

def ls( strToSearch = None, **args ):
	"""return a list of Nodes
	
	:param strToSearch: string or mayaNode to filter list
	:param **args: extra arguments the same as original command
	:returns: Nodes object( array of mayaNodes  )"""
	cmd = ''
	if strToSearch:
		if str(strToSearch.__class__) == "<class 'general.mayaNode.mayaNode.Nodes'>":
			cmd += '['
			for n in strToSearch:
				cmd += '"' + n.name + '",'
			cmd += '],'
		else:
			cmd += '"' + str( strToSearch ) + '",'
	for a in args.keys():
		val = args[a]
		if isinstance(val, str):
			cmd += a + '="' + args[a] + '",'
		else:
			cmd += a + '=' + str( args[a] ) + ','
	nodes = eval( "mc.ls(" + cmd + ")" )
	if nodes:
		return Nodes( nodes )

def listRelatives( strToSearch = None, **args ):
	"""Node version of list relatives maya command

	:param strToSearch: string or mayaNode object to use in list Relatives.. if None use selection
	:param **args: extra arguments the same as original command
	:returns: Nodes object( array of mayaNodes  )"""
	cmd = ''
	if strToSearch:
		cmd += '"' + strToSearch + '",'
	for a in args.keys():
		val = args[a]
		if isinstance(val, str):
			cmd += a + '="' + args[a] + '",'
		else:
			cmd += a + '=' + str( args[a] ) + ','
	nodes = eval( "mc.listRelatives(" + cmd + ")" )
	if nodes:
		return Nodes( nodes )

def createNode( typeOfNode, **args ):
	"""mayaNode version of create node
	
	:param typeOfNode: string type of maya node to create
	:param **args: extra arguments the same as original command
	:returns: mayaNode object
	"""
	cmd = ''
	if typeOfNode:
		cmd += '"' + typeOfNode + '",'
	for a in args.keys():
		val = args[a]
		if isinstance(val, str):
			cmd += a + '="' + args[a] + '",'
		else:
			cmd += a + '=' + str( args[a] ) + ','
	node = eval( "mc.createNode(" + cmd + ")" )
	if node:
		return Node(node)


##################################################
# NODES CLASS

class Nodes(list):
	"""return array of mayaNode objects"""
	def __init__(self, nodesList):
		nods = []
		if not isinstance( nodesList[0], Node ):
			nods = [ Node(n) for n in nodesList ]
		else:
			nods = nodesList
		super(Nodes, self).__init__( nods )

	@property
	def nodes(self):
		""":returns: array of mayaNode objects"""
		try:
			return [ n for n in self ]
		except:
			return None

	@property
	def names(self):
		""":returns: array of mayaNode names (string)"""
		try:
			return [ n.name for n in self ]
		except:
			return None

	@property
	def a(self):
		"""return an array of the same attribute for the nodes"""
		pass

	def select(self):
		"""select all the nodes"""
		mc.select( self.names )

	def parent(self, newParent):
		"""parent all nodes to transform"""
		for n in self.nodes:
			n.parent = newParent

##################################################
# NODE CLASS

class Node(object):
	"""base class to handle maya nodes more easy"""
	def __init__(self, name ):
		self._name = name

	def __str__(self):
		return self._name

	def __repr__(self):
		return self._name

	def __call__(self):
		"""select node when you call it =)"""
		if not self.exists:
			raise NodeNotFound( self._name )
		mc.select( self._name )

	@property
	def name(self):
		""":returns: name of node"""
		return self._name

	@name.setter
	def name(self, newName ):
		"""rename object"""
		if not self.exists:
			raise NodeNotFound( self._name )
		self._name = mc.rename( self.name, newName )

	@property
	def fullname(self):
		""":returns: the FullName of the node, if not exists return False"""
		if not self.exists:
			raise NodeNotFound( self._name )
		return mc.ls( '*' + self._name, l = True )[0]

	@property
	def parent(self):
		""":returns: the parent of the node"""
		if not self.exists:
			raise NodeNotFound( self._name )
		p = mc.listRelatives( self._name, p = True )
		if p:
			return Node( p[0] )
		else:
			return None

	@parent.setter
	def parent(self, newParent):
		"""set a new parent for node, supports string and Node, if newParent = None, set to world
		:param newParent: mayaNode to set for parent for this node"""
		if not self.exists:
			raise NodeNotFound( self.name )
		if not newParent:
			mc.parent( self.name, w = True )
			return
		elif isinstance( newParent, str):
			newParent = Node( newParent )
		if not newParent.exists:
			raise NodeNotFound( newParent.name )
		mc.parent( self.name, newParent.name )

	@property
	def allparents(self):
		""":returns: all parents of the node... recursive"""
		if not self.exists:
			raise NodeNotFound( self._name )
		p = self.parent
		nods = []
		if p != None:
			nods.append( p )
			newNodes = p.allparents
			if newNodes:
				nods.extend( newNodes )
		else:
			return None
		return Nodes( nods )

	@property
	def children(self):
		""":returns: children of the node"""
		if not self.exists:
			raise NodeNotFound( self._name )
		c = mc.listRelatives( self._name, c = True, f = True )
		if c:
			return [ Node( a ) for a in c ] #check how to handle arrays of nodes
		else:
			return []

	@property
	def allchildren(self):
		""":returns: all the children in recursive"""
		child = self.children
		for c in child:
			child.extend( c.allchildren )
		return child

	@property
	def exists(self):
		""":returns: True or False, check if the node really exists"""
		return mc.objExists( self._name )

	@property
	def type(self):
		""":return: Node Type"""
		if not self.exists:
			raise NodeNotFound( self._name )
		return mc.objectType( self.name )

	def istype(self, typ ):
		""":returns: True of False, if the node is a specific type"""
		if not self.exists:
			raise NodeNotFound( self._name )
		return mc.objectType( self.name, isType = typ )

	@property
	def a(self):
		""":returns: attribute object to work with =)"""
		if not self.exists:
			raise NodeNotFound( self._name )
		return NodeAttributeCollection( self )

	@property
	def namespace(self):
		""":returns: namespace of node"""
		return Namespace.fromNode( self )

	@namespace.setter
	def namespace( self, newNamespace ):
		"""move to other namespace"""
		if isinstance( newNamespace, str ):
			newNamespace = Namespace( newNamespace )
		if not newNamespace.exists:
			if AUTO_CREATE_NAMESPACE:
				newNamespace.create()
			else:
				raise NamespaceNotFound( newNamespace.name )
		oldName = self.name
		if self.namespace.name == ':':
			self.name = newNamespace.name[1:] + ':' + oldName
		else:
			self.name = oldName.replace( self.namespace.name[1:], newNamespace.name[1:] )

	def attr(self, attribute):
		""":returns: attribute object to work with =)"""
		if not self.exists:
			raise NodeNotFound( self._name )
		return NodeAttribute(self, attribute)

	@property
	def worldPosition(self):
		""":return: 3 float, the world position if it is a transform node"""
		return mc.xform( self.name, q = True, ws = True, rp = True )

	@property
	def locked(self):
		""":returns: True or False, lock state of the Node"""
		if not self.exists:
			raise NodeNotFound( self.name )
		return mc.lockNode( self.name, q = True, l = True )[0]

	@locked.setter
	def locked(self, state):
		"""unlock Node"""
		if not self.exists:
			raise NodeNotFound( self.name )
		mc.lockNode( self.name, l = state )

	def duplicate(self, newName = None):
		""":returns: new duplicated node"""
		if not self.exists:
			raise NodeNotFound( self.name )
		if newName:
			newNode = mc.duplicate( self.name, n = newName )
		else:
			newNode = mc.duplicate( self.name )
		return Node( newNode[0] )

	def delete(self):
		"""delete node"""
		if not self.exists:
			raise NodeNotFound( self.name ), None, sys.exc_info()[2]
		mc.delete( self.name )

	def listAttr(self, **args):
		""":returns: list the attributes of the node"""
		cmd = ''
		for a in args.keys():
			val = args[a]
			if isinstance(val, str):
				cmd += a + '="' + args[a] + '",'
			else:
				cmd += a + '=' + str( args[a] ) + ','
		attrs = eval( "mc.listAttr( '" + self.name + "'," + cmd + ")" )
		if attrs:
			return [ NodeAttribute( self, a ) for a in attrs ]

	@property
	def shape(self):
		""":returns: the shape of the node if there is one"""
		sha = listRelatives( self.name, s = True, ni = True, f = True )
		if sha:
			return sha[0]
		return None

	@property
	def outputs(self):
		"""return all the outputs connections from node"""
		cons = [ NodeAttribute( Node( a.split('.')[0] ), a.split('.')[1] ) for a in mc.listConnections( self.name, sh = True, s = False, scn = True, p = True, c = True )]
		return [cons[n:n+2] for n in range(0, len(cons), 2)]
		

##################################################
# ATTRIBUTES CLASS

class NodesAttributes(list):
	"""manage a list of attributes"""
	def __init__(self, attributes):
		attrs = []
		if not isinstance( attributes[0], NodeAttribute ):
			attrs = [ NodeAttribute( Node(a[:a.index('.')]), a[a.index('.')+1:]) for a in attributes ]
		else:
			attrs = attributes
		super(NodesAttributes, self).__init__( attrs )

	@property
	def nodes(self):
		"""return the nodes in the attributes array"""
		try:
			return Nodes( [ a.node for a in self ] )
		except:
			return []

	@property
	def values(self):
		"""return the values of the nodes"""
		try:
			return [ a.v for a in self ]
		except:
			return None


##################################################
# ATTRIBUTE CLASS

class NodeAttribute(object):
	def __init__(self, node, attribute):
		self._node = node
		self._attribute = attribute

	def __str__(self):
		return self.fullname

	def __repr__(self):
		return self.fullname

	@property
	def fullname(self):
		"""full name of the attribute with the node --> node.attribute string"""
		return self._node.name + "." + self._attribute

	@property
	def name(self):
		"""name of the attribute"""
		return self._attribute

	@property
	def node(self):
		"""return node of the current attribute"""
		return self._node

	@property
	def v(self):
		"""attribute value"""
		if not self.exists:
			raise AttributeNotFound( self._node.name, self.name )
		return mc.getAttr( self.fullname )

	@v.setter
	def v(self, value):
		"""Set the attribute value.. 
		Handle different types"""
		if not self.exists:
			raise AttributeNotFound( self._node.name, self._attribute )
		ty = self.type
		hasNumber = re.match( r'.+(\d)', ty )
		if hasNumber:
			if len( value ) == int( hasNumber.groups(0)[0] ):
				for v,a in enumerate( self.children ):
					if AUTO_UNLOCK_ATTR:
						a.locked = False
					if AUTO_OVERRIDE_ATTR:
						a.overrided = True
					mc.setAttr( a.fullname, value[v] )
			else:
				raise ValueError( "The attribute %s has different amount of values"%self._attribute )
		elif ty == 'string': #Set STRING Value
			if AUTO_UNLOCK_ATTR:
				self.locked = False
			if AUTO_OVERRIDE_ATTR:
				self.overrided = True
			mc.setAttr(self.fullname, value, type=ty)
		else:
			if AUTO_UNLOCK_ATTR:
				self.locked = False
			if AUTO_OVERRIDE_ATTR:
				self.overrided = True
			mc.setAttr( self.fullname,  value )

	@property
	def children(self):
		"""Return children attributes"""
		if not self.exists:
			raise AttributeNotFound( self._node.name, self._attribute )
		tmpAttr = re.sub( '\[\d+\]$', '' , self._attribute )
		tmpAttr = tmpAttr[tmpAttr.rfind( '.' )+1:]
		children = mc.attributeQuery( tmpAttr, node = self._node.name, lc = True )
		if children:
			return [ NodeAttribute(self._node, self._attribute + '.' + a) for a in children ]
		return []

	@property
	def type(self):
		"""return Attribute Type"""
		if not self.exists:
			raise AttributeNotFound( self._node.name, self._attribute )
		return mc.getAttr(self.fullname, type=True)

	@property
	def exists(self):
		"""attribute exists? """
		tmpAttr = re.sub( '\[\d+\]$', '' , self._attribute )
		tmpAttr = tmpAttr[tmpAttr.rfind( '.' )+1:]
		if self._node.exists:
			return mc.attributeQuery( tmpAttr, node=self._node.name, ex=True)
		else:
			return False

	@property
	def locked(self):
		"""lock attribute"""
		if not self.exists:
			raise AttributeNotFound( self._node.name, self._attribute )
		return mc.getAttr( self.fullname, l = True )

	@locked.setter
	def locked(self, state):
		"""lock attribute"""
		if not self.exists:
			raise AttributeNotFound( self._node.name, self._attribute )
		mc.setAttr( self.fullname, l = state )

	@property
	def size(self):
		"""retur the size of the attribute,
		usefull for array attributes"""
		return mc.getAttr( self.fullname, size = True )

	@property
	def max(self):
		"""return max value if it has, else None"""
		if not self.exists:
			raise AttributeNotFound( self._node.name, self._attribute )
		return mc.addAttr( self.fullname, q = True, max = True )

	@max.setter
	def max(self, value):
		"""set new max value for attribute"""
		if not self.exists:
			raise AttributeNotFound( self._node.name, self._attribute )
		mc.addAttr( self.fullname, e = True, max = value )

	@property
	def min(self):
		"""return min value if it has, else None"""
		if not self.exists:
			raise AttributeNotFound( self._node.name, self._attribute )
		return mc.addAttr( self.fullname, q = True, min = True )

	@min.setter
	def min(self, value):
		"""set new min value for attribute"""
		if not self.exists:
			raise AttributeNotFound( self._node.name, self._attribute )
		mc.addAttr( self.fullname, e = True, min = value )

	@property
	def default(self):
		"""return default value if it has, else None"""
		if not self.exists:
			raise AttributeNotFound( self._node.name, self._attribute )
		return mc.attributeQuery( self._attribute, n = self._node.name, ld = True )[0]

	@default.setter
	def default(self, value):
		"""set new default value for attribute"""
		if not self.exists:
			raise AttributeNotFound( self._node.name, self._attribute )
		mc.addAttr( self.fullname, e = True, dv = value )

	@property
	def input(self):
		"""get input connection if there is one, None if not"""
		if not self.exists:
			raise AttributeNotFound( self._node.name, self._attribute )
		con = mc.listConnections( self.fullname, p = True, d = False, skipConversionNodes = True )
		if con:
			condata = con[0].split( '.', 1 )
			return NodeAttribute( Node( condata[0] ), condata[1] )
		return []

	@property
	def output(self):
		"""get output connections if there is one, None if not, this return an array"""
		if not self.exists:
			raise AttributeNotFound( self._node.name, self._attribute )
		con = mc.listConnections( self.fullname, p = True, s = True, skipConversionNodes = True )
		if con:
			con = NodesAttributes( [ NodeAttribute( Node( a[:a.index('.')] ), a[a.index('.')+1:] ) for a in con ] )
			return con
		else:
			return []

	@property
	def overrided(self):
		"""return if the attribute has override"""
		lay = mc.editRenderLayerGlobals( query=True, currentRenderLayer=True )
		if not 'defaultRenderLayer' == lay:
			if any( a.node.name == lay for a in c.a.v.output ):
				return True
		return False

	@overrided.setter
	def overrided(self, value):
		"""set an override for attribute"""
		lay = mc.editRenderLayerGlobals( query=True, currentRenderLayer=True )
		if not 'defaultRenderLayer' == lay:
			if value:
				mc.editRenderLayerAdjustment( self.fullname ,layer= lay )
			else:
				mc.editRenderLayerAdjustment( self.fullname , remove=True )

	def __rshift__(self, other):
		"""connect attribute using >> """
		self.connect( other )

	def __lshift__(self, other):
		"""connect attribute using << """
		self.connect( other, False )

	def connect( self, other, inOrder = True ):
		"""connect attribute to another or inverse, determined by inOrder"""
		"""
		if not self.exists:
			raise AttributeNotFound( self._node.name, self._attribute )
		if not other.exists:
			raise AttributeNotFound( self._node.name, self._attribute )
		"""
		if inOrder:
			if AUTO_UNLOCK_ATTR:
				other.name.locked = False
			mc.connectAttr( self.fullname, other.fullname, f = FORCE_CONNECTION )
		else:
			if AUTO_UNLOCK_ATTR:
				self.name.locked = False
			mc.connectAttr( other.fullname, self.fullname, f = FORCE_CONNECTION )

	def __floordiv__(self, other):
		"""discconect attribute using // """
		self.disconnect( other )

	def disconnect(self, other = None ):
		"""disconnect attributes, if other is None... it will disconnect to what ever is connected =)"""
		if not self.exists:
			raise AttributeNotFound( self._node.name, self._attribute )
		if not other:
			con = self.input
			if con:
				mc.disconnectAttr( con, self.fullname )
				return
		elif not other.exists:
			raise AttributeNotFound( self._node.name, self._attribute )
		mc.disconnectAttr( self.fullname, other.fullname )

	def __or__(self, other):
		"""is connected ? using | THE PIPE =) """
		return self.isConnected( other )

	def isConnected(self, other, inOrder = True ):
		"""check if the attributes are connected"""
		if not self.exists:
			raise AttributeNotFound( self._node.name, self._attribute )
		if not other.exists:
			raise AttributeNotFound( self._node.name, self._attribute )
		if inOrder:
			return mc.isConnected( self.name, other.name )
		else:
			return mc.isConnected( other.name, self.name )

	def delete(self):
		"""delete attribute"""
		if not self.exists:
			raise AttributeNotFound( self._node.name, self._attribute )
		mc.deleteAttr(self._node.name, at=self._attribute)

	def add( self, **args ):
		"""add custom attribute"""
		cmd = ''
		if args:
			for a in args.keys():
				val = args[a]
				if isinstance(val, str):
					cmd += a + '="' + args[a] + '",'
				else:
					cmd += a + '=' + str( args[a] ) + ','
		eval( "mc.addAttr( '"+ self._node.name + "', longName = '" + self._attribute + "'," + cmd + ")" )

	def alias(self, newName):
		"""alias the current attribute with a new name"""
		mc.aliasAttr( newName, self.fullname )


##################################################
# ATTRIBUTES COLLECTION CLASS

class NodeAttributeCollection(object):

    def __init__(self, node):
        self._node = node

    def __getattr__(self, attribute):
        return NodeAttribute(self._node, attribute)

##################################################
# NAMESPACES

class Namespace(object):
	"""class to control namespaces"""
	def __init__(self, namespace = None ):
		"""if namespace is None... it will take current"""
		if not namespace:
			self._namespace = mc.namespaceInfo( cur = True )
		else:
			self._namespace = namespace 
		if not self._namespace.startswith( ':' ):
			self._namespace = ':' + self._namespace

	def __str__(self):
		"""return string format"""
		return self._namespace

	def __enter__( self ):
		return self

	def __exit__( self, type, value, traceback ):
		mc.namespace( set=self._namespace )

	@property
	def name(self):
		"""return the namespace in string"""
		return self._namespace
	
	def create(self):
		"""create namespace if doesn't exists"""
		if not self.exists:
			names = self._namespace[1:].split(':')
			with Namespace( ':' ).set():
				tmpParent = ''
				for s in names:
					if not mc.namespace( ex = tmpParent + ':' + s ):
						mc.namespace( add = s, p = tmpParent + ':' )
					tmpParent += ':' + s 

	@property
	def exists(self):
		"""check if current namespace exists"""
		return mc.namespace( ex = self._namespace )

	@property
	def children(self):
		"""return the children of the namespace if exists"""
		if not self.exists:
			raise NamespaceNotFound( self.name )
		with self.set():
			childs = mc.namespaceInfo( lon=True )
		if childs:
			childs = [ Namespace( n ) for n in childs ]
		return childs

	@property
	def nodes(self):
		"""return the nodes that have the namespace"""
		if not self.exists:
			raise NamespaceNotFound( self.name )
		with self.set():
			nods = mc.namespaceInfo( lod = True )
			if nods:
				return [ Node( n ) for n in nods ]
		return None

	@property
	def firstParent(self):
		"""return the first namespace of current namespace"""
		nspace = self.parent
		if not self.parent.name == ':':
			nspace = nspace.firstParent
		else:
			nspace = self
		return nspace

	@property
	def parent(self):
		"""return the parent of the current namespace"""
		if not self.exists:
			raise NamespaceNotFound( self.name )
		p = self.name.rindex(':')
		if p == 0:
			return Namespace( ':' )
		else:
			return Namespace( self.name[ :p ] )

	@property
	def empty(self):
		"""return if the namespace is empty"""
		nods = self.nodes
		if nods:
			return True
		else:
			return False

	def remove(self):
		"""remove namespace if exists"""
		if not self.exists:
			raise NamespaceNotFound( self.name )
		mc.namespace( rm = self.name )

	def set(self):
		"""set namespace to current"""
		if not self.exists:
			if AUTO_CREATE_NAMESPACE:
				self.create()
		nsTempSet = Namespace()
		mc.namespace( set = self._namespace )
		return nsTempSet

	def move(self, other):
		"""move current nodes in namespace to other, also support if other is a string"""
		if not self.exists:
			raise NamespaceNotFound( self.name )
		if isinstance( other, str ):
			other = Namespace( other )
		if not other.exists:
			if AUTO_CREATE_NAMESPACE:
				other.create()
			else:
				raise NamespaceNotFound( other.name )
		mc.namespace( mv = [ self.name, other.name ], f = True )
		self._namespace = other.name

	def __rshift__(self,other):
		"""move namespace from this namespace to another with >>"""
		self.move( other )

	def rename(self, newName):
		"""rename current namespace, it will rename all childs namespaces"""
		if not self.exists:
			raise NamespaceNotFound( self.name )
		mc.namespace( ren = newName, f = True )

	@staticmethod
	def fromNode(node):
		"""return namespace from Node"""
		p = node.name.rfind( ':' )
			
		if p == -1:
			return Namespace( ':' )
		else:
			return Namespace( ':'+ node.name[ :p ] )

#####################################################
#ERRORS

class AttributeNotFound( Exception ):
	def __init__(self, node, attribute ):
		self._message = "Node '%s' has no attribute '%s'." % ( node, attribute )
		Exception.__init__(self, self._message)

	def __str__(self):
		return repr( self._message )

class NodeNotFound( Exception ):
	def __init__(self, node ):
		self._message = "Node '%s' doesn\'t exists." % ( node ) 
		Exception.__init__(self, self._message)

	def __str__(self):
		return self._message

class NamespaceNotFound( Exception ):
	def __init__(self, namespace ):
		self._message = "Namespace '%s' doesn\'t exists." % ( namespace )
		Exception.__init__(self, self._message)

	def __str__(self):
		return self._message 
