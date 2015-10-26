import maya.OpenMaya as om
import math
import maya.cmds as mc

def getMatrixFromParamCurve( curveFn, param, exNormal ):
	"""docstring for getMatrixFromParamCurve"""
	pDivPos = om.MPoint()
	curveFn.getPointAtParam( param, pDivPos, om.MSpace.kWorld );
	vNormal = om.MVector( curveFn.normal( param, om.MSpace.kObject ).normal() );
	vTangent = om.MVector( curveFn.tangent( param, om.MSpace.kObject ).normal() );
	if not exNormal.length() == 0:
		print ( exNormal + vNormal ).length()
		if ( exNormal + vNormal ).length() < 1:
			vNormal = vNormal * -1
	vExtra = vNormal ^ vTangent
	dTrans =[
			vNormal.x, vNormal.y, vNormal.z, 0.0,
			vTangent.x, vTangent.y, vTangent.z, 0.0,
			vExtra.x, vExtra.y, vExtra.z, 0.0,
			pDivPos.x,pDivPos.y,pDivPos.z, 1.0]
	mTrans = om.MMatrix();
	om.MScriptUtil.createMatrixFromList(dTrans,mTrans)
	return mTrans, vNormal

def createCirclePoints( pointsCount, bMatrix, points ):
	"""docstring for createCirclePoints"""
	baseVector = om.MPoint( 1,0,0 )
	baseVector2 = om.MPoint( 1,0,0 ) * bMatrix
	points.append( om.MFloatPoint( baseVector2.x, baseVector2.y, baseVector2.z, 1.0 ) )
	for d in range( 1, pointsCount ):
		vVector = om.MVector( baseVector ).rotateBy( om.MVector.kYaxis, om.MAngle(( 360.0 / pointsCount * d ), om.MAngle.kDegrees).asRadians() )
		vVector = om.MPoint( vVector ) * bMatrix
		points.append( om.MFloatPoint( vVector.x, vVector.y, vVector.z, 1.0 ) )
	return points

def createRopesRings( ropesCount, bMatrix, points, pointsCount = 5 ):
	"""creates ropes base, create half rope and move them to the final position"""
	baseVector = om.MPoint( 1,0,0 )
	angle = om.MAngle(( 180.0 / ropesCount ), om.MAngle.kDegrees)
	distanceToMoveRope = math.sin(om.MAngle(( 360.0 / ropesCount ), om.MAngle.kDegrees).asRadians() )
	singleRopeRadius = math.sin( angle.asRadians() )
	print "distanceToMoveRope", distanceToMoveRope
	for d in range( 1, ropesCount + 1 ):
		ropePoints = createHalfRope( pointsCount, singleRopeRadius )
		for ropP in range( ropePoints.length() ):
			ropP = om.MVector( ropePoints[ ropP ] ) + om.MVector( 0,0,-1 ) * distanceToMoveRope
			basVRot = om.MVector( baseVector ).rotateBy( om.MVector.kYaxis, om.MAngle(( 360.0 / ropesCount * d ), om.MAngle.kDegrees).asRadians() )
			ropV = om.MVector( ropP ).rotateBy( om.MVector.kYaxis, om.MAngle(( 360.0 / ropesCount * d ), om.MAngle.kDegrees).asRadians() )
			ropV = om.MPoint( ropV ) * bMatrix # move vector to final position
			points.append( om.MFloatPoint( ropV.x, ropV.y, ropV.z, 1.0 ) )
	return points

def createHalfRope( pointsCount = 5, radius = 1 ):
	"""create 180 degrees circle, and multiple points by radius"""
	points = om.MFloatPointArray()
	baseVector = om.MPoint( 1,0,0 ) * radius
	points.append( om.MFloatPoint( baseVector.x, baseVector.y, baseVector.z, 1.0 ) )
	for d in range( 1, pointsCount ):
		"""
		if d == 1:
			d = 0.25
		elif d == pointsCount - 1:
			d += 0.75
		"""
		baseAngle = om.MAngle(( 180.0 / ( pointsCount ) * d ), om.MAngle.kDegrees)
		vVector = om.MVector( baseVector ).rotateBy( om.MVector.kYaxis, baseAngle.asRadians() )
		points.append( om.MFloatPoint( vVector.x, vVector.y, vVector.z, 1.0 ) )
	return points

def createTube( obj = 'curveShape1' ):
	divisions = 15
	createRope = True
	ropesCount = 6
	pointsPerRope = 5
	pointsCount = 5
	if createRope:
		pointsCount = pointsPerRope *ropesCount
	sel = om.MSelectionList()
	dagPath = om.MDagPath()
	sel.add(obj)
	sel.getDagPath(0, dagPath)
	curveFn = om.MFnNurbsCurve( dagPath )
	curveFnLeng = curveFn.length()
	meshFS = om.MFnMesh()
	#division throu curve
	lengPerDiv = curveFnLeng / divisions
	#points in ring
	numVerteces = ( divisions + 1 ) * pointsCount
	numFaces = ( pointsCount *  divisions  ) + 2
	points = om.MFloatPointArray()
	faceConnects = om.MIntArray()
	faceCounts = om.MIntArray()
	baseLeng = lengPerDiv
	exNormal = om.MVector(0,0,0)
	for d in range( 0, divisions + 1 ):
		if d == 0: #Extreme 1
			param = 0
			faceCounts.append( pointsCount )
			for i in reversed(range( pointsCount )):
				faceConnects.append( i )
		else:
			param = curveFn.findParamFromLength( baseLeng )
			for i in range( pointsCount ):
				faceCounts.append( 4 )
			for f in range( pointsCount ):
				if f == pointsCount - 1:
					faceConnects.append( ( f + 1 + ( d * pointsCount ) ) - pointsCount - pointsCount )
					faceConnects.append( ( f + 1 + ( d * pointsCount ) - pointsCount ) )
					faceConnects.append( f + 1 + ( d * pointsCount ) - 1 )
					faceConnects.append( f + 1 + ( d * pointsCount ) - pointsCount - 1 )
				else:
					faceConnects.append( ( f + ( d * pointsCount ) ) - pointsCount )
					faceConnects.append( f + 1  + ( d * pointsCount ) - pointsCount )
					faceConnects.append( f + 1  + ( d * pointsCount ) )
					faceConnects.append( ( f + ( d * pointsCount ) ) )
			if d == divisions: #Extreme 2
				faceCounts.append( pointsCount )
				for i in range( pointsCount ):
					faceConnects.append( ( pointsCount *  divisions ) + i )
			baseLeng += lengPerDiv
		mTrans, exNormal = getMatrixFromParamCurve( curveFn, param, exNormal )
		if createRope:
			createRopesRings( ropesCount, mTrans, points, pointsPerRope )
		else:
			createCirclePoints( pointsCount, mTrans, points )
	print numVerteces, numFaces, points.length(), faceCounts.length(), faceConnects.length()
	newMesh = meshFS.create(numVerteces, numFaces, points, faceCounts, faceConnects )

createTube()

