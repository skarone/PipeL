import maya.OpenMaya as OpenMaya
import maya.OpenMayaUI as OpenMayaUI
import maya.OpenMayaMPx as OpenMayaMPx
import maya.OpenMayaAnim as OpenMayaAnim
import math
import sys

kPi = 3.1415926535897931
kEpsilon = 1.0000000000000001e-05
kSolverNodeName = 'stretchSplineSolver'
kSolverNodeId = OpenMaya.MTypeId(554874)

class stretchSplineSolver(OpenMayaMPx.MPxIkSolverNode):
	__module__ = __name__

	def __init__( self):
		OpenMayaMPx.MPxIkSolverNode.__init__(self)
		self.fn = splineSolverFn()



	def solverTypeName(self):
		return kSolverNodeName



	def preSolve(self):
		self.fn.splinePreSolve(self)



	def doSolve(self):
		self.fn.splineDoSolve()



	def postSolve(self, stat):
		self.fn.splinePostSolve()




def nodeCreator():
	return OpenMayaMPx.asMPxPtr(stretchSplineSolver())



def nodeInitializer():
	pass


def initializePlugin(mobject):
	mplugin = OpenMayaMPx.MFnPlugin(mobject, 'Ignacio Urruty', '1.0', 'Any')
	try:
		mplugin.registerNode(kSolverNodeName, kSolverNodeId, nodeCreator, nodeInitializer, OpenMayaMPx.MPxNode.kIkSolverNode)
	except:
		sys.stderr.write(('Failed to register node: %s' % kSolverNodeName))
		raise 



def uninitializePlugin(mobject):
	mplugin = OpenMayaMPx.MFnPlugin(mobject)
	try:
		mplugin.deregisterNode(kSolverNodeId)
	except:
		sys.stderr.write(('Failed to unregister node: %s' % kSolverNodeName))
		raise 



def absoluteValue(x):
	if (x < 0):
		return (-1 * x)
	else:
		return x


class splineSolverFn:
	__module__ = __name__
	__doc__ = '\n    // Name         :Stretchy Ik solver .\n    // Developer    : Ma Yi\n    // Email        : mayi3d@gmail.com\n    // 2007-04-26   :   C++ code change to python . some problems due to not evaluating\n                        during solving process .\n    '
	stretchRatio = 1
	initLength = []
	jointsVectors = []

	def getBoneScales(self, jointFn):
		sxPlug = jointFn.findPlug('sx')
		syPlug = jointFn.findPlug('sy')
		szPlug = jointFn.findPlug('sz')
		sxValue = sxPlug.asDouble()
		syValue = syPlug.asDouble()
		szValue = szPlug.asDouble()
		return (sxValue,syValue,szValue)


	def evaluateDG(self):
		for j in self.joints:
			sxPlug = j.findPlug('sx')
			syPlug = j.findPlug('sy')
			szPlug = j.findPlug('sz')
			sxValue = sxPlug.asDouble()
			sxPlug.setDouble(sxValue)
			syValue = syPlug.asDouble()
			syPlug.setDouble(syValue)
			szValue = szPlug.asDouble()
			szPlug.setDouble(szValue)

	def splinePreSolve(self, solvernode):
#         '\n        initiate all the members of the class.\n        including :\n            handleFn , handlePath , effectorFn ,  startJointFn ,\n            startJointPrefAngle ,  .\n        the reason why I put the initial codes here is fail to load the plugin ,\n        when I put these codes in the __init__() function .\n        '
		solvernode.setRotatePlane(0)
		solvernode.setSingleChainOnly(1)
		solvernode.setPositionOnly(0)
		handleGroup = solvernode.handleGroup()
		handle = handleGroup.handle(0)
		self.handlePath = OpenMaya.MDagPath()
		self.handlePath.getAPathTo(handle, self.handlePath)
		self.handleFn = OpenMayaAnim.MFnIkHandle(self.handlePath)
		if not self.handleFn.hasAttribute('str'):
			fnAttr = OpenMaya.MFnNumericAttribute()
			attr = fnAttr.create('stretchRatio', 'str', OpenMaya.MFnNumericData.kDouble, self.stretchRatio)
			fnAttr.setKeyable(1)
			fnAttr.setWritable(1)
			fnAttr.setMin(0)
			fnAttr.setMax(1)
			fnAttr.setHidden(0)
			fnAttr.setStorable(1)
			fnAttr.setReadable(1)
			self.handleFn.addAttribute(attr, OpenMaya.MFnDependencyNode.kLocalDynamicAttr)
		else:
			strPlug = self.handleFn.findPlug('str')
			self.stretchRatio = strPlug.asDouble()
		effectorPath = OpenMaya.MDagPath()
		self.handleFn.getEffector(effectorPath)
		self.effectorFn = OpenMayaAnim.MFnIkEffector(effectorPath)
		startJointPath = OpenMaya.MDagPath()
		self.handleFn.getStartJoint(startJointPath)
		self.startJointFn = OpenMayaAnim.MFnIkJoint(startJointPath)
		self.joints = []
		currJoint = ''
		inCurvePlug = self.handleFn.findPlug('inCurve')
		curveHandle = inCurvePlug.asMDataHandle()
		inputCurveObject = curveHandle.asNurbsCurveTransformed()
		self.curveFn = OpenMaya.MFnNurbsCurve( inputCurveObject )
		#get joints
		while True:
			effectorPath.pop()
			j = OpenMayaAnim.MFnIkJoint(effectorPath)
			self.joints.append( j )
			currJoint = effectorPath
			if currJoint == startJointPath:
				break
		self.joints = list(reversed(self.joints))
		#get lengths
		for v,j in enumerate( self.joints ):
			pBaseJoint = j.rotatePivot(OpenMaya.MSpace.kWorld)
			if v == len( self.joints ) - 1:
				pEndJoint = self.effectorFn.rotatePivot(OpenMaya.MSpace.kWorld)
			else:
				#get position of next joint
				pEndJoint = self.joints[ v + 1 ].rotatePivot(OpenMaya.MSpace.kWorld)
			jVec = OpenMaya.MVector(pBaseJoint[0]-pEndJoint[0], pBaseJoint[1]-pEndJoint[1], pBaseJoint[2]-pEndJoint[2])
			self.jointsVectors.append( jVec )
			self.initLength.append( jVec.length() )


	def doublePtr(self, x, y, z):
		sul = OpenMaya.MScriptUtil()
		sul.createFromDouble(x, y, z)
		return sul.asDoublePtr()

	def splineDoSolve(self):
		crvLength = self.curveFn.length()
		lengthPerJoint = crvLength / ( len( self.joints ) )
		startLength = 0.0
		#move first joint to base of curve
		pBaseJoint = OpenMaya.MPoint()
		parm = self.curveFn.findParamFromLength( startLength )
		self.curveFn.getPointAtParam( parm, pBaseJoint )
		self.joints[0].setTranslation( OpenMaya.MVector( pBaseJoint ), OpenMaya.MSpace.kWorld )
		#print lengthPerJoint, crvLength
		#print self.initLength
		#caculate rotation for other joints
		for v,j in enumerate(  self.joints  ):
			pBaseJoint = j.rotatePivot(OpenMaya.MSpace.kWorld)
			#print j.fullPathName()
			if v == len( self.joints ) - 1:
				pEndJoint = self.effectorFn.rotatePivot(OpenMaya.MSpace.kWorld)
			else:
				#get position of next joint
				#print self.joints[ v + 1 ].fullPathName()
				pEndJoint = self.joints[ v + 1 ].rotatePivot(OpenMaya.MSpace.kWorld)
			pFinalPos = OpenMaya.MPoint()
			vBaseJoint =OpenMaya.MVector(pBaseJoint[0]-pEndJoint[0], pBaseJoint[1]-pEndJoint[1], pBaseJoint[2]-pEndJoint[2])
			#vBaseJoint = self.jointsVectors[ v ]
			#startLength = startLength + lengthPerJoint
			startLength += (self.initLength[ v ] + self.stretchRatio * ( lengthPerJoint - self.initLength[ v ] ))
			#print startLength
			scale = (self.initLength[ v ] + self.stretchRatio * ( lengthPerJoint - self.initLength[ v ] )) / self.initLength[ v ]
			#scale = lengthPerJoint / self.initLength[ v ]
			#scale = 1
			j.setScale(self.doublePtr(scale, 1, 1))
			parm = self.curveFn.findParamFromLength( startLength )
			self.curveFn.getPointAtParam( parm, pFinalPos )
			#print pFinalPos[0], pFinalPos[1], pFinalPos[2], startLength
			vFinalJoint = OpenMaya.MVector(pBaseJoint[0]-pFinalPos[0], pBaseJoint[1]-pFinalPos[1], pBaseJoint[2]-pFinalPos[2])

			crosVec = vBaseJoint^vFinalJoint
			w = math.sqrt((vBaseJoint.length() * vBaseJoint.length()) * (vFinalJoint.length() * vFinalJoint.length())) + vBaseJoint*vFinalJoint
			q = OpenMaya.MQuaternion(crosVec.x, crosVec.y, crosVec.z, w )
			q.normalizeIt()
			j.rotateBy( q, OpenMaya.MSpace.kWorld )
			#print j.fullPathName(), scale, vBaseJoint.length()
			#need to scale current joint to match lenght

	def splinePostSolve( self):
#         '\n        After solving , DG need to be evaluated .\n        '
		self.evaluateDG()
		self.splineDoSolve()

"""
joint -p -7 0 0 ;
joint -p -4 0 0 ;
joint -e -zso -oj xyz -sao yup joint1;
joint -p -1 0 0 ;
joint -e -zso -oj xyz -sao yup joint2;
joint -p 3 0 0 ;
joint -e -zso -oj xyz -sao yup joint3;
select -r joint1.rotatePivot ;
select -add joint4.rotatePivot ;
ikHandle;
curve -d 3 -p -7 0 -1 -p -6.088889 0 -1.8 -p -4.266667 0 -3.4 -p 0.0666667 0 -3.4 -p 2.688889 0 -1.8 -p 4 0 -1 -k 0 -k 0 -k 0 -k 1 -k 2 -k 3 -k 3 -k 3 ;
connectAttr -force curveShape1.worldSpace[0] ikHandle1.inCurve;
createNode "stretchSplineSolver" -name "stretchyik";
select -r ikHandle1 ;
ikHandle -n "ikHandle1" -e -sol "stretchyik";
//create simple spline handle
joint -p -7 0 0 ;
joint -p -4 0 0 ;
joint -e -zso -oj xyz -sao yup joint5;
joint -p -1 0 0 ;
joint -e -zso -oj xyz -sao yup joint6;
joint -p 3 0 0 ;
joint -e -zso -oj xyz -sao yup joint7;
select -r joint5 ;
select -add joint8 ;
select -add curve1 ;
ikHandle -sol ikSplineSolver -ccv false -pcv false;

"""
#+++ okay decompyling
# decompiled 1 files: 1 okay, 0 failed, 0 verify failed
