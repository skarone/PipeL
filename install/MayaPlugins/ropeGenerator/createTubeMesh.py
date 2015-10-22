import maya.OpenMaya as om

def getMatrixFromParamCurve( curveFn, param ):
	"""docstring for getMatrixFromParamCurve"""
	pDivPos = om.MPoint()
	curveFn.getPointAtParam( 0, pDivPos, om.MSpace.kWorld );
	vNormal = om.MVector( curveFn.normal( 0, om.MSpace.kObject ) );
	vTangent = om.MVector( curveFn.tangent( 0, om.MSpace.kObject ) );
	vExtra = vNormal ^ vTangent
	dTrans =[
			vExtra.x, vExtra.y, vExtra.z, 0.0,
			vTangent.x, vTangent.y, vTangent.z, 0.0,
			vNormal.x, vNormal.y, vNormal.z, 0.0,
			pDivPos.x,pDivPos.y,pDivPos.z, 1.0]
	mTrans = om.MMatrix();
	om.MScriptUtil.createMatrixFromList(dTrans,mTrans)
	return mTrans


def createCirclePoints( pointsCount, bMatrix, points ):
	"""docstring for createCirclePoints"""
	#points = om.MFloatPointArray()
	baseVector = om.MVector( 0,0,1 )
	baseVector2 = om.MVector( 0,0,1 ) * bMatrix
	points.append( om.MFloatPoint( baseVector2.x, baseVector2.y, baseVector2.z, 1.0 ) )
	rotVector = om.MVector( 0, 1, 0 )
	for d in range( 1, pointsCount ):
		vVector = baseVector.rotateBy( om.MVector.kYaxis, om.MAngle(( 360.0 / pointsCount * d ), om.MAngle.kDegrees).asRadians() )
		vVector = vVector * bMatrix
		points.append( om.MFloatPoint( vVector.x, vVector.y, vVector.z, 1.0 ) )
	return points

def createTube( obj = 'curveShape1' ):
	sel = om.MSelectionList()
	dagPath = om.MDagPath()

	sel.add(obj)
	sel.getDagPath(0, dagPath)

	curveFn = om.MFnNurbsCurve( dagPath )
	meshFS = om.MFnMesh()
	#division throu curve
	divisions = 5
	#points in ring
	pointsCount = 5
	numVerteces = divisions * pointsCount
	numFaces = pointsCount + 2

	points = om.MFloatPointArray()
	faceConnects = om.MIntArray()
	faceCounts = om.MIntArray()
	faceConnects.append( 0 )

	for d in range( 0, divisions + 1 ):
		if d == 0:
			param = 0
			faceCounts.append( pointsCount )
			for i in range( pointsCount ):
				faceConnects.append( i )
		elif d == divisions:
			param = float(d) / float( divisions )
			faceCounts.append( pointsCount )
			for i in range( pointsCount ): #ERROR
				faceConnects.append( ( pointsCount * divisions ) + i )
		else:
			param = float(d) / float( divisions )
			for i in range( pointsCount ):
				faceCounts.append( 4 )
			for f in range( pointsCount ):
				faceConnects.append( ( f + ( d * pointsCount ) ) - pointsCount )
				faceConnects.append( f + 1  + ( d * pointsCount ) - pointsCount )
				faceConnects.append( f + 1  + ( d * pointsCount ) )
				faceConnects.append( ( f + ( d * pointsCount ) ) )
		mTrans = getMatrixFromParamCurve( curveFn, param )
		createCirclePoints( pointsCount, mTrans, points )
		faceConnects.append( d )

	newMesh = meshFS.create(numVerteces, numFaces, points, faceCounts, faceConnects )
	#fIndex = om.MIntArray()
	#fIndex.append( 0 )
	#meshFS.extrudeFaces( fIndex, 1, om.MFloatVector( 0, 1, 0 ), True )
	#meshFS.extrudeFaces( fIndex, 1, om.MFloatVector( 0, 1, 0 ), True )
	#meshFS.updateSurface()
	#nodeName = meshFS.name()


createTube()

