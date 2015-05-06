import hou
import _hou

def createNode( typ, nivel = '/obj' ):
	"""create node and return create Node"""
	n = hou.node( nivel ).createNode( typ )
	return Node( n.name() )

class Node(hou.Node):
	"""docstring for Node"""
	def __init__(self, name ):
		self._node = hou.node( name )

	@property
	def name(self):
		"""docstring for name"""
		return self._node.name()

	@property
	def parent(self):
		"""docstring for nivel"""
		return self._node.parent()
		
	@name.setter
	def name(self, newName):
		"""rename"""
		self._node.setName( newName )

	@property
	def a(self):
		"""docstring for a"""
		return NodeAttributeCollection( self )

	def attr(self, attribute):
		"""docstring for attr"""
		return NodeAttribute(self, attribute)
	
	@property
	def listAttrs(self):
		"""return attributes of node"""
		return self._node.parms()


class NodeAttribute(object):
	def __init__(self, node, attribute):
		self._node = node
		self._attribute = attribute
		self.uid = hash(node.name + attribute)
		self.parm = self._node._node.parm( attribute )

	@property
	def v(self):
		"""return attribute value"""
		return self.parm.eval()

	@v.setter
	def v(self, value):
		"""docstring for v"""
		self.parm.set( value )

	def pressButton(self):
		self.parm.pressButton()

class NodeAttributeCollection(object):

    def __init__(self, node):
        self._node = node

    def __getattr__(self, attribute):
        return NodeAttribute(self._node, attribute)

class ClassName(object):
	"""docstring for ClassName"""
	def __init__(self, arg):
		super(ClassName, self).__init__()
		self.arg = arg
		
