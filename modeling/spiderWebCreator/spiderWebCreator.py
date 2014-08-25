import maya.cmds as mc
import maya.mel as mm
import general.mayaNode.mayaNode as mn
reload( mn )
import modeling.curve.curve as crv
import rigging.utils.pointOnCurve.pointOnCurve as pntcrv
import random
import math
#crear curvas en base a un vertice y un borde
#obtener posicion del mundo del vertice
#obtener posicion de los vertices del borde
#crear curvas que van desde el punto a los vertices del borde
#loop entre curva y curva, ir subiendo el paramatro de la curva con una formula espiral
#generando una curva entre esos 2 puntos

def drange(start, stop, step):
	r = start
	while r < stop:
		yield r
		r += step

def create( loops = 10, dynamicGuides = False ):
	"""create a spider web based on a polygon mesh, select a vertex for the center of the web and a edge loop for the border"""
	sel = mc.ls( sl = True, fl = True )
	if not sel:
		mc.warning( 'Select a vertex for the center of the web and a loop of edges for the border' )
		return
	vert = sel[0]
	vertPos = mc.xform( vert, q = True, ws = True, t = True )
	edges = sel[1:]
	exists = True
	finalNameSpace = ''
	num = 0
	while exists:
		if not mc.namespace( ex = 'spiderWeb' + str( num ) ):
			exists = False
			finalNameSpace = 'spiderWeb' + str( num )
		num += 1
	space = mn.Namespace( finalNameSpace )
	space.create()
	with space.set():
		#create Base Groups
		baseGrp = mn.Node( mc.createNode('transform') )
		baseGrp.name = 'spiderWeb_grp'
		baseGrp.a.CurveWidth.add( dv = 0.010 )
		baseGrp.a.CurveShader.add( uac = True, attributeType='float3' )
		baseGrp.a.red.add( attributeType='float', parent='CurveShader' )
		baseGrp.a.green.add( attributeType='float', parent='CurveShader' )
		baseGrp.a.blue.add( attributeType='float', parent='CurveShader' )
		shader = mn.createNode( 'aiHair' )
		baseGrp.a.CurveShader.v = [1,1,1]
		crvsGrp = mn.Node( mc.createNode('transform') )
		crvsGrp.name = 'spiderWeb_CRV_grp'
		trfLocs = mn.createNode( 'transform' )
		trfLocs.name = 'spiderWeb_LOC_grp'
		trfLocs.a.v.v = 0
		trfFols = mn.createNode( 'transform' )
		trfFols.name = 'spiderWeb_FOL_grp'
		trfFols.a.v.v = 0
		crvsGrp.parent = baseGrp
		trfLocs.parent = baseGrp
		trfFols.parent = baseGrp
		hrsSys = mn.createNode( 'hairSystem' )
		mn.Node( 'time1' ).a.outTime >> hrsSys.a.currentTime
		hrsSys.parent.parent = baseGrp
		####
		vertecesOnEdges = mc.ls( mc.polyListComponentConversion( edges, fromEdge = True, toVertex = True ), fl = True )
		orderedVertices = getOrderedVerteces( vertecesOnEdges )
		crvs, fols, locs = createGuideCurves( orderedVertices, vertPos, hrsSys, dynamicGuides )
		for c in crvs:
			baseGrp.a.CurveWidth >> c.shape.a.aiCurveWidth
			shader.a.outColor >> c.shape.a.aiCurveShader
		mn.Nodes( crvs ).parent( crvsGrp )
		if fols:
			mn.Nodes( fols ).parent( trfFols )
		if locs:
			mn.Nodes( locs ).parent( trfLocs )
		crvs,fols,locs = createSpiralCurves( crvs, loops, hrsSys )
		for c in crvs:
			baseGrp.a.CurveWidth >> c.shape.a.aiCurveWidth
			shader.a.outColor >> c.shape.a.aiCurveShader
		mn.Nodes( crvs ).parent( crvsGrp )
		mn.Nodes( fols ).parent( trfFols )
		mn.Nodes( locs ).parent( trfLocs )
		hrsSys.parent.name = 'spiderWeb_HRS'

	
def getOrderedVerteces( vertecesOnEdges ):
	"""return an array with the verteces on an loop edge ordered by neightbor"""
	tmpVertEdges = vertecesOnEdges
	nextVert = tmpVertEdges[0]
	orderedVertices = []
	while not len(tmpVertEdges) == 0:
		edgeOnVertex = mc.polyListComponentConversion( nextVert, fromVertex = True, toEdge = True )
		orderedVertices.append( nextVert )
		tmpVertEdges.remove( nextVert )
		for e in edgeOnVertex:
			vertsOnEdg = mc.ls( mc.polyListComponentConversion( e, fromEdge = True, toVertex = True ), fl = True )
			for v in vertsOnEdg:
				if v in tmpVertEdges:
					nextVert = v
					break
	return orderedVertices

def createGuideCurves( orderedVertices, centerVertPos, hrsSys, dynamic = True ):
	crvs = []
	fols = []
	locs = []
	centerLoc = mn.Node( mc.spaceLocator(  )[0] )
	centerLoc.a.t.v = centerVertPos
	locs.append( centerLoc )
	for i,v in enumerate( orderedVertices ):
		vPos = mc.xform( v, q = True, ws = True, t = True )
		if dynamic:
			loc = mn.Node( mc.spaceLocator( )[0] )
			loc.a.t.v = vPos
			curv, folPar = createCurveaBasedOnLocator( centerLoc, loc, 'guide', hrsSys )
			fols.append( folPar )
			locs.append( loc )
		else:
			curv = crv.Curve( mc.curve( d = 3, ep = [centerVertPos, vPos] ) )
			mc.rebuildCurve( curv.name, rpo = 1, rt = 0, end = 1, kr = 2, kcp = 0, kep = 1, kt =0, s= 3, d = 3, tol = 0.01  )
			curv.name = 'spiderWeb_guide_' + str( i ) + '_CRV'
		curv.shape.a.aiRenderCurve.v = 1
		crvs.append( curv )
	return crvs, fols, locs

def createSpiralCurves( crvs, loops, hrsSys ):
	"""create spiral curves for curve guides"""
	i = 0
	maxVal = mc.arclen( crvs[0] )
	for c in crvs:
		if mc.arclen( c ) > maxVal:
			maxVal = mc.arclen( c )    
	prevLoc = ''
	spiralCrvs = []
	fols = []
	locs = []
	count = 0
	baseName = 'spiral'
	for a in drange( 0.0, maxVal, ( 1.0 / len( crvs ) / loops ) ):
		if i == ( len( crvs ) ):
			i = 0
		c = crvs[i]
		i += 1
		offset = a * ( maxVal ) / mc.arclen( c )
		offset = offset + random.uniform(-0.01,0.01)
		if c.shape.a.maxValue.v < offset:
			break
		pointOnCur = pntcrv.PointOnCurve( c )
		nod = pointOnCur.nodeAt( offset )
		loc = mn.Node( mc.spaceLocator(  )[0] )
		nod.a.position >> loc.a.translate
		if prevLoc:
			prevLoc.name = 'spiderWeb_' + str( count ) + '_LOC'
			curv, folPar = createCurveaBasedOnLocator( prevLoc, loc, baseName, hrsSys )
			fols.append( folPar )
			curv.shape.a.aiRenderCurve.v = 1
			spiralCrvs.append( curv )
			count += 1
		locs.append( loc )
		prevLoc = loc
	return spiralCrvs, fols, locs


def createCurveaBasedOnLocator( prevLoc, loc, baseName, hrsSys ):
	leastSquaresMod = mn.createNode( 'leastSquaresModifier' )
	origCurv = crv.Curve( mc.curve( d = 1, ep = [prevLoc.worldPosition, loc.worldPosition] ) )
	index = mm.eval( 'getNextFreeMultiIndex( "'+ hrsSys.name +'.inputHair", 0 )' )
	origCurv.name = 'spiderWeb_base_'+ baseName + '_' + str( index ) + '_CRV'
	mc.rebuildCurve( origCurv.name, rpo = 1, rt = 0, end = 1, kr = 0, kcp = 1, kep = 1, kt =0, s= 4, d = 1, tol = 0.01  )
	origCurv.a.intermediateObject.v = 1
	controledCurv = origCurv.duplicate()
	origCurv.shape.attr( 'worldSpace[0]' ) >> leastSquaresMod.a.inputNurbsObject
	prevLoc.attr( 'worldPosition[0]')      >> leastSquaresMod.attr( 'pointConstraint[0].pointPositionXYZ' )
	leastSquaresMod.attr( 'pointConstraint[0].pointConstraintU' ).v = 0
	loc.attr( 'worldPosition[0]')          >> leastSquaresMod.attr( 'pointConstraint[1].pointPositionXYZ' )
	leastSquaresMod.attr( 'pointConstraint[1].pointConstraintU' ).v = 1
	leastSquaresMod.a.outputNurbsObject    >> controledCurv.shape.a.create
	controledCurv.shape.attr( 'worldMatrix[0]' ) >> leastSquaresMod.a.worldSpaceToObjectSpace
	fol = mn.createNode( 'follicle' )
	fol.a.restPose.v = 1
	fol.a.startDirection.v = 1
	fol.a.pointLock.v = 3
	fol.a.degree.v = 3
	fol.a.sampleDensity.v = 3
	fol.a.outHair >> hrsSys.attr( 'inputHair[' + str( index ) + ']' )
	hrsSys.attr( 'outputHair[' + str( index ) + ']' ) >> fol.a.currentPosition
	controledCurv.shape.attr( 'worldSpace[0]' ) >> fol.a.startPosition
	curv = crv.Curve( mc.curve( d = 3, ep = [prevLoc.worldPosition, loc.worldPosition] ) )
	curv.name = 'spiderWeb_' + baseName + '_' + str( index ) + '_CRV'
	fol.a.outCurve >> curv.a.create
	folPar = fol.parent
	folPar.name = 'spiderWeb_' + baseName + '_' + str( index ) + '_FOL'
	return curv, folPar

