
"""
import pipe.dependency.dependency as dp
a = dp.Node('a')
b = dp.Node('b')
c = dp.Node('c')
d = dp.Node('d')
e = dp.Node('e')

a.addEdge(b)    # a depends on b
a.addEdge(d)    # a depends on d
b.addEdge(c)    # b depends on c
b.addEdge(e)    # b depends on e
c.addEdge(d)    # c depends on d
c.addEdge(e)    # c depends on e

resolved = []
unresolved = []
dp.dep_resolve(a, resolved,unresolved)
for node in resolved:
	print node.name,


"""


class Node:
	def __init__(self, name):
		self.name = name
		self.edges = []

	def addEdge(self, node):
		self.edges.append(node)


def dep_resolve(node, resolved, unresolved):
	unresolved.append(node)
	for edge in node.edges:
		if edge not in resolved:
			if edge in unresolved:
				raise Exception('Circular reference detected: %s -&gt; %s' % (node.name, edge.name))
			dep_resolve(edge, resolved, unresolved)
	resolved.append(node)
	unresolved.remove(node)

def dep_resolvedArray( depArray ):
	for f in depArray:
		for dep in f[1]:
			f[0].addEdge( depArray[dep][0] )
	result = []
	for f in depArray:
		resolved = []
		unresolved = []
		dep_resolve( f[0], resolved, unresolved )
		resolved.remove( f[0] )
		result.append( [ f[0], resolved ] )
	return result
