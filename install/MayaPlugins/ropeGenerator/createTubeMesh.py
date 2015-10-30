import maya.OpenMaya as om
import math
import maya.cmds as mc

def getMatrixFromParamCurve( curveFn, param, twist ):
	"""docstring for getMatrixFromParamCurve"""
	pDivPos = om.MPoint()
	curveFn.getPointAtParam( param, pDivPos, om.MSpace.kWorld );
	vTangent = om.MVector( curveFn.tangent( param, om.MSpace.kObject ).normal() );
	#Create Paralel Vector to use as base
	vLocalPos = om.MVector( 0,1,0 )
	vNormal = vLocalPos ^ vTangent
	# vNormal = om.MVector( curveFn.normal( param, om.MSpace.kObject ).normal() );
	qTwist = om.MQuaternion( twist.asRadians(), vTangent )
	vNormal = vNormal.rotateBy( qTwist )
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
	baseVector = om.MPoint( 1,0,0 )
	baseVector2 = om.MPoint( 1,0,0 ) * bMatrix
	points.append( om.MFloatPoint( baseVector2.x, baseVector2.y, baseVector2.z, 1.0 ) )
	for d in range( 1, pointsCount ):
		vVector = om.MVector( baseVector ).rotateBy( om.MVector.kYaxis, om.MAngle(( 360.0 / pointsCount * d ), om.MAngle.kDegrees).asRadians() )
		vVector = om.MPoint( vVector ) * bMatrix
		points.append( om.MFloatPoint( vVector.x, vVector.y, vVector.z, 1.0 ) )
	return points

def createCircleUvs( pointsCount ):
	"""docstring for createCircleUvs"""
	baseVector = om.MPoint( 0.5,0,0 )
	uArray = om.MFloatArray()
	vArray = om.MFloatArray()
	uArray.append( baseVector.x + 0.5 )
	vArray.append( baseVector.z + 0.5 )
	for d in range( 1, pointsCount ):
		vVector = om.MVector( baseVector ).rotateBy( om.MVector.kYaxis, om.MAngle(( 360.0 / pointsCount * d ), om.MAngle.kDegrees).asRadians() )
		uArray.append( vVector.x + 0.5 )
		vArray.append( vVector.z + 0.5 )
	return uArray, vArray

def createRopeUvs( ropesCount, pointsCount, ropeStrength ):
	"""docstring for createRopeUvs"""
	angle = om.MAngle(( 180.0 / ropesCount ), om.MAngle.kDegrees)
	distanceToMoveRope = math.cos(om.MAngle(( 180.0 / ropesCount ), om.MAngle.kDegrees).asRadians() )
	singleRopeRadius = math.sin( angle.asRadians() )
	uArray = om.MFloatArray()
	vArray = om.MFloatArray()
	for d in range( 1, ropesCount + 1 ):
		ropePoints = createHalfRope( pointsCount, singleRopeRadius )
		for ropP in range( ropePoints.length() ):
			ropP = ropePoints[ ropP ]
			ropP = om.MVector( ropP.x, ropP.y, ropP.z * ropeStrength ) + om.MVector( 0,0,-1 ) * distanceToMoveRope
			ropV = om.MVector( ropP ).rotateBy( om.MVector.kYaxis, om.MAngle(( 360.0 / ropesCount * d ), om.MAngle.kDegrees).asRadians() )
			uArray.append( ropV.x + 0.5 )
			vArray.append( ropV.z + 0.5 )
	return uArray, vArray

def createRopesRings( ropesCount, bMatrix, points, pointsCount = 5, ropeStrength = 1 ):
	"""creates ropes base, create half rope and move them to the final position"""
	angle = om.MAngle(( 180.0 / ropesCount ), om.MAngle.kDegrees)
	distanceToMoveRope = math.cos(om.MAngle(( 180.0 / ropesCount ), om.MAngle.kDegrees).asRadians() )
	singleRopeRadius = math.sin( angle.asRadians() )
	for d in range( 1, ropesCount + 1 ):
		ropePoints = createHalfRope( pointsCount, singleRopeRadius )
		for ropP in range( ropePoints.length() ):
			ropP = ropePoints[ ropP ]
			ropP = om.MVector( ropP.x, ropP.y, ropP.z * ropeStrength ) + om.MVector( 0,0,-1 ) * distanceToMoveRope
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
		if d == 1: #add an extra point to make the rope more marked
			baseAngle = om.MAngle(( 180.0 / ( pointsCount ) * 0.25 ), om.MAngle.kDegrees)
			vVector = om.MVector( baseVector ).rotateBy( om.MVector.kYaxis, baseAngle.asRadians() )
			points.append( om.MFloatPoint( vVector.x, vVector.y, vVector.z, 1.0 ) )
		baseAngle = om.MAngle(( 180.0 / ( pointsCount ) * d ), om.MAngle.kDegrees)
		vVector = om.MVector( baseVector ).rotateBy( om.MVector.kYaxis, baseAngle.asRadians() )
		points.append( om.MFloatPoint( vVector.x, vVector.y, vVector.z, 1.0 ) )
		if d == pointsCount - 1:
			baseAngle = om.MAngle(( 180.0 / ( pointsCount ) * (d + 0.75) ), om.MAngle.kDegrees)
			vVector = om.MVector( baseVector ).rotateBy( om.MVector.kYaxis, baseAngle.asRadians() )
			points.append( om.MFloatPoint( vVector.x, vVector.y, vVector.z, 1.0 ) )
	return points

def createTube( obj = 'curveShape1' ):
	divisions = 32
	createRope = True
	ropesCount = 5
	pointsPerRope = 6
	pointsCount = 5
	ropeStrength = 1
	twist = om.MAngle( 0, om.MAngle.kDegrees )
	if createRope:
		pointsCount = (pointsPerRope + 2 ) *ropesCount
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
	uvIds = om.MIntArray()
	uArray = om.MFloatArray()
	vArray = om.MFloatArray()
	baseLeng = lengPerDiv
	uDivNumber = 1.0 / pointsCount
	vDivNumber = 1.0 / divisions
	for d in range( 0, divisions + 1 ):
		if d == 0: #Extreme 1
			param = 0
			faceCounts.append( pointsCount )
			for i in reversed(range( pointsCount )):
				faceConnects.append( i )
				for i in range( pointsCount ):
					uvIds.append( i )
					if createRope: #create Uvs for circle first Face
				uTmpArray,vTmpArray = createRopeUvs( ropesCount, pointsCount, ropeStrength )
			else:
				uTmpArray,vTmpArray = createCircleUvs( pointsCount )
				for u in range( uTmpArray.length() ):
					uArray.append( uTmpArray[u] + 1.0 )
					vArray.append( vTmpArray[u] )
				for i in range( pointsCount + 1 ):
					uArray.append( uDivNumber * i )
					vArray.append( vDivNumber * d )
		else:
			param = curveFn.findParamFromLength( baseLeng )
			for i in range( pointsCount + 1 ):
				uArray.append( uDivNumber * i )
				vArray.append( vDivNumber * d )
			for f in range( pointsCount ):
				faceCounts.append( 4 )
				if f == pointsCount - 1: #for last face we need to change
					faceConnects.append( ( f + 1 + ( d * pointsCount ) ) - pointsCount - pointsCount )
					faceConnects.append( ( f + 1 + ( d * pointsCount ) - pointsCount ) )
					faceConnects.append( f + 1 + ( d * pointsCount ) - 1 )
					faceConnects.append( f + 1 + ( d * pointsCount ) - pointsCount - 1 )
				else:
					faceConnects.append( ( f + ( d * pointsCount ) ) - pointsCount )
					faceConnects.append( f + 1  + ( d * pointsCount ) - pointsCount )
					faceConnects.append( f + 1  + ( d * pointsCount ) )
					faceConnects.append( ( f + ( d * pointsCount ) ) )
				uvIds.append( pointsCount + (( pointsCount + 1 ) * ( d - 1 )) + f)
				uvIds.append( pointsCount + (( pointsCount + 1 ) * ( d - 1 )) + 1 + f )
				uvIds.append( pointsCount + (( pointsCount + 1 ) * ( d )) + 1 + f)
				uvIds.append( pointsCount + (( pointsCount + 1 ) * ( d )) + f)
			if d == divisions: #Extreme 2
				faceCounts.append( pointsCount )
				for i in range( pointsCount ):
					faceConnects.append( ( pointsCount *  divisions ) + i )
					uvIds.append( ( pointsCount *  ( divisions + 2 )) + i + divisions + 1 )
				uTmpArray,vTmpArray = createCircleUvs( pointsCount )
				for u in range( uTmpArray.length() ):
					uArray.append( uTmpArray[u] + 2.0 )
					vArray.append( vTmpArray[u] )
			baseLeng += lengPerDiv
		mTrans = getMatrixFromParamCurve( curveFn, param, twist )
		if createRope:
			createRopesRings( ropesCount, mTrans, points, pointsPerRope, ropeStrength )
		else:
			createCirclePoints( pointsCount, mTrans, points )

	print numVerteces, numFaces, points.length(), faceCounts.length(), faceConnects.length()
	newMesh = meshFS.create(numVerteces, numFaces, points, faceCounts,
							faceConnects, uArray, vArray )
	faceCountsTotal = 0
	for c in range( faceCounts.length() ):
		faceCountsTotal += faceCounts[c]
	print "NumUvs",meshFS.numUVs()
	print "uvsIds",uvIds.length()
	print "faceCountsTotal",faceCountsTotal
	print "uArray leng", uArray.length()
	meshFS.assignUVs( faceCounts, uvIds )

createTube()

