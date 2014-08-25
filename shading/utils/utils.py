import general.mayaNode.mayaNode as mn

def createGammaForSelectedNodes( useExistingGama = True, gammaValue = 0.454 ):
	"""create gamma nodes based on selection"""
	for n in mn.ls( sl = True ):
		createGammaForNode( n, useExistingGama, gammaValue )

def createGammaForNode( node, useExistingGama = True, gammaValue = 0.454 ):
	outputs = node.a.outColor.output
	if outputs:
		newGam = None
		if useExistingGama:
			newGam = [ o.node for o in outputs if o.node.type == 'gammaCorrect' ]
			if newGam:
				newGam = newGam[0]
		if not newGam:
			newGam = mn.createNode( 'gammaCorrect' )
			newGam.name = node.name + '_GAM'
		newGam.a.gammaX.v = gammaValue
		newGam.a.gammaY.v = gammaValue
		newGam.a.gammaZ.v = gammaValue
		try:
			node.a.outColor >> newGam.a.value
		except:
			pass
		for o in outputs:
			if o.node.type == 'gammaCorrect':
				continue
			newGam.a.outValue >> o
