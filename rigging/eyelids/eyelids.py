#get verteces and center
#sort from left to right, based on position
#create joints based on verteces positions and center
#create Locators
#Aim contrstraint joints bases to locators
#create base curve
#attach locators to base curve
#rebuild base curve to create controller curve
#rebuildCurve -ch 1 -rpo 1 -rt 0 -end 1 -kr 2 -kcp 0 -kep 1 -kt 0 -s 2 -d 3 -tol 0.01 "L_upLidHigh_CRV1";
#wire deformer base curve with controller curve
#create joints on every cv of controller curve
#skin controller curve with created joints
#create controls on each skin joint
#parent contraint middle controlers to main controles
#create smart blink curves
"""
import rigging.eyelids.eyelids as eyeLids
reload( eyeLids ) 
#TopVertex = mc.ls( sl = 1 , fl = True ) 
#LowVertex = mc.ls( sl = 1 , fl = True ) 
eyelids = eyeLids.EyeLidsRig( 
topEyelidsVertexList = TopVertex, 
lowEyelidsVertexList = LowVertex, 
centerPivot = "cluster1Handle" , 
mirror = False, 
initialSide = 'L'
)

"""


import rigging.utils.sorting.sorting as sorting
reload( sorting )
import general.mayaNode.mayaNode as mn
import maya.cmds as mc
import maya.OpenMaya as OpenMaya
import modeling.curve.curve as crv
reload( crv )

class EyeLidsRig(object):
	"""create an eyelids rig system"""
	def __init__(self, topEyelidsVertexList, lowEyelidsVertexList, centerPivot, mirror = True, initialSide = 'L' ):
		"""topEyelidsVertexList = array of verteces of the border of the upper eyelid
		lowEyelidsVertexList = array of verteces of the border of the lower eyelid
		centerPivot = center of the eye( it has to be a sphere )
		mirror = mirror the system in the X axis
		initialSide = The side that the system is initialy created"""
		self.topEyelidsVertexList = [ mc.xform( v, q = 1, ws = 1, t = 1 ) for v in topEyelidsVertexList ]
		self.lowEyelidsVertexList = [ mc.xform( v, q = 1, ws = 1, t = 1 ) for v in lowEyelidsVertexList ]
		self.centerPivot = centerPivot
		self.center = mc.xform( self.centerPivot, q = 1, ws = 1, rp = 1 )
		self.SCALE = OpenMaya.MVector( self.topEyelidsVertexList[0][0] - self.center[0],self.topEyelidsVertexList[0][1] - self.center[1],self.topEyelidsVertexList[0][2] - self.center[2] ).length()
		print self.SCALE, "SCALE"
		self.initialSide = initialSide
		self.createJoints()
		if mirror:
			#recreate EyeLids system but with the VertexList multiplied by -1 in X axis
			self.topEyelidsVertexList = [ self.negativeXPoint(p) for p in self.topEyelidsVertexList]
			self.lowEyelidsVertexList = [ self.negativeXPoint(p) for p in self.lowEyelidsVertexList]
			self.center = self.negativeXPoint( self.center )
			if self.initialSide == 'L':
				self.initialSide = 'R'
			else:
				self.initialSide = 'L'
			self.createJoints()

	def createJoints(self):
		"""create the joints of the system"""
		grp = mn.Node( mc.group( n = self.initialSide + "_Eyelid_GRP", em = True ) )
		locs = self._createBaseJoints( self.topEyelidsVertexList, self.initialSide + "_topEyelid", False, grp ) #TOP
		curv, crvGrp = self.createCurves( self.topEyelidsVertexList, locs, self.initialSide + "_topEyelid" )
		crvGrp.parent = grp
		topControls, topGrp = self.createControls( curv, self.initialSide + "_topEyelid" )
		topGrp.parent = grp
		locs = self._createBaseJoints( self.lowEyelidsVertexList, self.initialSide + "_lowEyelid", True, grp ) #BOTTOM
		curv,crvGrp = self.createCurves( self.lowEyelidsVertexList, locs, self.initialSide + "_lowEyelid" )
		crvGrp.parent = grp
		lowControls, lowGrp = self.createControls( curv, self.initialSide + "_lowEyelid" )
		lowGrp.parent = grp
		lowControls[0].parent = topControls[0]
		lowControls[-1].parent = topControls[-1]
		lowControls[0].a.v.v = 0
		lowControls[0].a.v.locked = 1
		lowControls[-1].a.v.v = 0
		lowControls[-1].a.v.locked = 1

	def _createBaseJoints(self, verteces, baseName, skipTips = False, baseGrp = None ):
		"""create based joints with the verteces and name it all with baseName"""
		#Create UP vector Locator
		upVecLoc = mn.Node( mc.spaceLocator( n = baseName + '_UP_LOC' )[0] )
		upVecLoc.shape.a.localScale.v = [self.SCALE]*3
		upVecLoc.a.t.v = [ self.center[0], self.center[1] + 1, self.center[2] ]
		upVecLoc.parent = baseGrp
		#GROUPS
		grp = mn.Node( mc.group( n = baseName + '_JNT_GRP', em = True ) )
		locgrp = mn.Node( mc.group( n = baseName + '_LOC_GRP', em = True ) )
		locs = []
		if skipTips:
			verteces = verteces[1: len( verteces ) - 1 ]
		for i,v in enumerate( verteces ):
			grp()
			baseJnt = mn.Node( mc.joint( n = baseName + "%i"%i + '_JNT', p = self.center ) )
			jnt = mn.Node( mc.joint( n = baseName + "%i"%i + '_SKN', p = v ) )
			mc.joint( baseJnt.name, e=True, zso=True, oj='xyz' )
			#create locator for AIM
			loc = mn.Node( mc.spaceLocator( n = baseName + "%i"%i + '_LOC' )[0] )
			loc.a.t.v = v
			loc.shape.a.localScale.v = [self.SCALE/6.0]*3
			loc.parent = locgrp
			locs.append( loc )
			mc.aimConstraint( loc.name, baseJnt.name, weight = 1, mo = True, aimVector = [1,0,0], upVector = [0,1,0], worldUpType = "object", wuo = upVecLoc.name )
		grp.parent = baseGrp
		locgrp.parent = baseGrp
		return locs

	def createCurves(self, verteces, locs, baseName ):
		"""create the curves to controls the locators"""
		grp = mn.Node( mc.group( n = baseName + '_CRV_GRP', em = True ) )
		tmp = mn.Node( mc.curve( n = baseName + "High" + '_CRV', d = 1, p = verteces, k = [ i for i in range( len( verteces ) ) ] ) )
		tmp.name = baseName + "High" + '_CRV'
		highCurve = crv.Curve( tmp.shape.name )
		highCurve.parent = grp
		#attach locs to curve
		for l in locs:
			pos = mc.xform( l.name, q = True, ws = 1, t = 1 )
			u = highCurve.uParam( pos )
			pci = mn.createNode( "pointOnCurveInfo" )
			pci.name = l.name.replace( '_LOC', '_PCI' )
			highCurve.a.worldSpace >> pci.a.inputCurve
			pci.a.parameter.v = u
			pci.a.position >> l.a.t
		lowCurve = highCurve.rebuild( keep = True )
		lowCurve.name = tmp.name.replace( 'High', 'Low' )
		lowCurve.parent = grp
		wir = mn.Node( mc.wire( tmp.name, gw = False, en = 1.000000, ce = 0.000000, li = 0.000000, w = lowCurve.name )[0] )
		wir.name = tmp.name.replace( '_CRV', '_WR' )
		return crv.Curve( lowCurve.name ), grp

	def createControls(self, curv, baseName ):
		"""create the controls for the eyelids"""
		grp = mn.Node( mc.group( n = baseName + '_CTL_GRP', em = True ) )
		controls = []
		for i,cvPos in enumerate( curv.cvsPosition ):
			clus = mn.Node( mc.cluster( curv.name + '.cv[ %i'%i + ' ]', n = curv.name.replace( '_CRV', '_CLU' ) )[1] )
			control = crv.Curve( baseName + '%i'%i + '_CTL' )
			control = control.create( 'sphere' )
			control.a.t.v = cvPos
			control.a.s.v = [self.SCALE/20.0]*3
			mc.makeIdentity( control.name, apply = True, t = 1, r = 1, s = 1, n = 2 )
			clus.parent = control
			clus.a.v.v = 0
			clus.a.v.locked = True
			control.parent = grp
			controls.append( control )
		return controls, grp

	def negativeXPoint(self, pnt):
		"""docstring for negativeXPoint"""
		return (pnt[0]*-1),pnt[1],pnt[2]
