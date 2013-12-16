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
import rigging.utils.sorting.sorting as sorting
reload( sorting )
import general.mayaNode.mayaNode as mn
import maya.cmds as mc
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
		self.topEyelidsVertexList = sorting.sortedByPosition( topEyelidsVertexList, "x" )
		self.lowEyelidsVertexList = sorting.sortedByPosition( lowEyelidsVertexList, "x" )
		self.centerPivot = centerPivot
		self.center = mc.xform( self.centerPivot, q = 1, ws = 1, rp = 1 )
		self.initialSide = initialSide
		self.createJoints()
		if mirror:
			#recreate EyeLids system but with the VertexList multiplied by -1 in X axis
			pass

	def createJoints(self):
		"""create the joints of the system"""
		#create Up Vector
		locs = self._createBaseJoints( self.topEyelidsVertexList, self.initialSide + "_topEyelid", skipTips = False ) #TOP
		self.createCurves( self.topEyelidsVertexList, locs, self.initialSide + "_topEyelid" )
		locs = self._createBaseJoints( self.lowEyelidsVertexList, self.initialSide + "_lowEyelid", skipTips = True ) #BOTTOM
		self.createCurves( self.lowEyelidsVertexList, locs, self.initialSide + "_lowEyelid" )

	def _createBaseJoints(self, verteces, baseName, skipTips = False ):
		"""create based joints with the verteces and name it all with baseName"""
		#Create UP vector Locator
		upVecLoc = mn.Node( mc.spaceLocator( n = baseName + '_UP_LOC' )[0] )
		upVecLoc.a.t.v = [ self.center[0], self.center[1] + 1, self.center[2] ]
		#GROUPS
		grp = mn.Node( mc.group( n = baseName + '_JNT_GRP', em = True ) )
		locgrp = mn.Node( mc.group( n = baseName + '_LOC_GRP', em = True ) )
		locs = []
		if skipTips:
			verteces = verteces[1: len( verteces ) - 1 ]
		for i,v in enumerate( verteces ):
			grp()
			vPos = mc.xform( v, q = 1, ws = 1, t = 1 )
			baseJnt = mn.Node( mc.joint( n = baseName + "%i"%i + '_JNT', p = self.center ) )
			jnt = mn.Node( mc.joint( n = baseName + "%i"%i + '_SKN', p = vPos ) )
			mc.joint( baseJnt.name, e=True, zso=True, oj='xyz' )
			#create locator for AIM
			loc = mn.Node( mc.spaceLocator( n = baseName + "%i"%i + '_LOC' )[0] )
			loc.a.t.v = vPos
			loc.parent = locgrp
			locs.append( loc )
			mc.aimConstraint( loc.name, baseJnt.name, weight = 1, mo = True, aimVector = [1,0,0], upVector = [0,1,0], worldUpType = "object", wuo = upVecLoc.name )
		return locs

	def createCurves(self, verteces, locs, baseName ):
		"""create the curves to controls the locators"""
		pos = [ mc.xform( v, q = 1, ws = 1, t = 1 ) for v in verteces ]
		highCurve = crv.Curve( mc.curve( n = baseName + "High" + '_CRV', d = 1, p = pos, k = [ i for i in range( len( verteces ) ) ] ) )
		#attach locs to curve
		for l in locs:
			pos = mc.xform( l.name, q = True, ws = 1, t = 1 )
			u = highCurve.uParam( pos )
			pci = mn.createNode( "pointOnCurveInfo" )
			pci.name = l.name.replace( '_LOC', '_PCI' )
			highCurve.a.worldSpace >> pci.a.inputCurve
			pci.a.parameter.v = u
			pci.a.position >> l.a.t
			
		

