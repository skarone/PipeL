import maya.OpenMaya as om

def getMatrixFromParamCurve( curveFn, param ):
	"""docstring for getMatrixFromParamCurve"""
	pDivPos = om.MPoint()
	curveFn.getPointAtParam( param, pDivPos, om.MSpace.kWorld );
	print pDivPos.x, pDivPos.y, pDivPos.z
	vNormal = om.MVector( curveFn.normal( param, om.MSpace.kObject ).normal() );
	vTangent = om.MVector( curveFn.tangent( param, om.MSpace.kObject ).normal() );
	vExtra = vNormal ^ vTangent
	dTrans =[
			vNormal.x, vNormal.y, vNormal.z, 0.0,
			vTangent.x, vTangent.y, vTangent.z, 0.0,
			vExtra.x, vExtra.y, vExtra.z, 0.0,
			pDivPos.x,pDivPos.y,pDivPos.z, 1.0]
	mTrans = om.MMatrix();
	om.MScriptUtil.createMatrixFromList(dTrans,mTrans)
	return mTrans


def createCirclePoints( pointsCount, bMatrix, points ):
	"""docstring for createCirclePoints"""
	#points = om.MFloatPointArray()
	baseVector = om.MPoint( 1,0,0 )
	baseVector2 = om.MPoint( 1,0,0 ) * bMatrix
	points.append( om.MFloatPoint( baseVector2.x, baseVector2.y, baseVector2.z, 1.0 ) )
	rotVector = om.MVector( 0, 1, 0 )
	for d in range( 1, pointsCount ):
		vVector = om.MVector( baseVector ).rotateBy( om.MVector.kYaxis, om.MAngle(( 360.0 / pointsCount * d ), om.MAngle.kDegrees).asRadians() )
		vVector = om.MPoint( vVector ) * bMatrix
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
	divisions = 15
	#points in ring
	pointsCount = 5
	numVerteces = ( divisions + 1 ) * pointsCount
	numFaces = ( pointsCount *  divisions  ) + 2

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
		else:
			param = float(d) / float( divisions )
			for i in range( pointsCount ):
				faceCounts.append( 4 )
			for f in range( pointsCount + 1 ):
				faceConnects.append( ( f + ( d * pointsCount ) ) - pointsCount )
				faceConnects.append( f + 1  + ( d * pointsCount ) - pointsCount )
				faceConnects.append( f + 1  + ( d * pointsCount ) )
				faceConnects.append( ( f + ( d * pointsCount ) ) )
			if d == divisions:
				faceCounts.append( pointsCount )
				for i in range( pointsCount ):
					faceConnects.append( ( pointsCount * ( divisions - 2) ) + i )
		mTrans = getMatrixFromParamCurve( curveFn, param )
		createCirclePoints( pointsCount, mTrans, points )
		#faceConnects.append( d )
	print numVerteces, numFaces, points.length(), faceCounts.length(), faceConnects.length()
	newMesh = meshFS.create(numVerteces, numFaces, points, faceCounts, faceConnects )


createTube()

