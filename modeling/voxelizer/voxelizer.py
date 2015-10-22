import maya.cmds as cmds
import maya.OpenMaya as OpenMaya

def createVoxelForSelection( startFrame = 1, endFrame = 24, voxelSize = 20.0, voxelStep = 0.5 ):
	"""docstring for createVoxelForSelection"""
	selObjts = cmds.ls( sl = True )
	for s in selObjts:
		createVoxelForObj( s, startFrame, endFrame, voxelSize, voxelStep )

def createVoxelForObj(obj, startFrame = 1, endFrame = 24, voxelSize = 20.0, voxelStep = 0.5 ):
	"""docstring for createVoxelForOb"""
	sel = OpenMaya.MSelectionList()
	dagPath = OpenMaya.MDagPath()

	sel.add(obj)
	sel.getDagPath(0, dagPath)

	inMesh = OpenMaya.MFnMesh( dagPath )

	grpReelNames = dict()
	for curTime in xrange(startFrame, endFrame+1) :
		grpName = "frameGrp_%s".zfill(4) % int(curTime)
		grpReelName = cmds.group(name=grpName, empty=True)
		cmds.setKeyframe(grpReelName+".visibility", value=0.0, time=[curTime-0.1])
		cmds.setKeyframe(grpReelName+".visibility", value=1.0, time=[curTime])
		cmds.setKeyframe(grpReelName+".visibility", value=0.0, time=[curTime+1])
		grpReelNames[curTime] = grpReelName

	for grpReelName in grpReelNames :
		if cmds.objExists(grpReelName) :
			cmds.delete(grpReelName)

	for curTime in xrange(startFrame, endFrame+1) :
		cmds.currentTime(curTime)
		voxelIdSet = set()
		#I use while just because xrange with floats is impossible
		i = -voxelSize/2.0
		while i <= voxelSize/2.0 :
			j = -voxelSize/2.0
			while j <= voxelSize/2.0 :
				for axis in ["zSide", "ySide", "xSide"] :
					z = 0
					y = 0
					x = 0
					zOffset = 0
					zDir = 0
					yOffset = 0
					yDir = 0
					xOffset = 0
					xDir = 0
					if axis == "zSide" :
						x = i
						y = j
						zOffset = 10000
						zDir = -1
					elif axis == "ySide" :
						x = i
						z = j
						yOffset = 10000
						yDir = -1
					elif axis == "xSide" :
						y = i
						z = j
						xOffset = 10000
						xDir = -1
					raySource = OpenMaya.MFloatPoint( x+xOffset, y+yOffset, z+zOffset )
					rayDirection = OpenMaya.MFloatVector(xDir, yDir, zDir)
					faceIds=None
					triIds=None
					idsSorted=False
					space=OpenMaya.MSpace.kWorld
					maxParam=99999999
					testBothDirections=False
					accelParams=inMesh.autoUniformGridParams()
					sortHits=False
					hitPoints = OpenMaya.MFloatPointArray()
					hitRayParam=None
					hitFacePtr = None#OpenMaya.MScriptUtil().asIntPtr()
					hitTriangle=None
					hitBary1=None
					hitBary2=None
					hit = inMesh.allIntersections(raySource,
									rayDirection,
									faceIds,
									triIds,
									idsSorted,
									space,
									maxParam,
									testBothDirections,
									accelParams,
									sortHits,
									hitPoints,
									hitRayParam,
									hitFacePtr,
									hitTriangle,
									hitBary1,
									hitBary2)
					if not hit :
						continue
					# for each interestected points
					for k in xrange(hitPoints.length()) :
						cubePosX = round(hitPoints[k].x/voxelStep)*voxelStep
						cubePosY = round(hitPoints[k].y/voxelStep)*voxelStep
						cubePosZ = round(hitPoints[k].z/voxelStep)*voxelStep
						cubeId = "%s%s%s" % (cubePosX, cubePosY, cubePosZ)
						if cubeId in voxelIdSet :
							continue
						else:
							voxelIdSet.add(cubeId)
						myCube = cmds.polyCube(width=voxelStep, height=voxelStep,  depth=voxelStep)[0]
						cmds.polyBevel(myCube, offset=0.02)
						cmds.parent(myCube, grpReelNames[curTime])
						cmds.setAttr(myCube+".translate", cubePosX, cubePosY, cubePosZ)
				j += voxelStep
			i += voxelStep
