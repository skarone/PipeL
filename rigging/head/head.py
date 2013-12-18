"""
create a head toon control, to deform head in a toon way
"""
import maya.cmds as mc
import general.mayaNode.mayaNode as mn
import modeling.curve.curve as crv

class ToonHead(object):
	"""create toon head class"""
	def __init__(self, objs = [], vertices = []):
		self.objs = objs
		self.vertices = vertices
		#lattice  -divisions 2 3 2 -objectCentered true  -ol 1;
		#mc.select( self.objs, self.vertices )
		#CREATION
		grp = mn.Node( mc.group( n = "head_toon_GRP", em = True ) )
		deGrp = mn.Node( mc.group( n = "head_toon_deformer_GRP", em = True ) )
		deGrp.parent = grp
		deGrp.a.v.v = False
		deGrp.a.v.locked = True
		latNods = mc.lattice( self.objs, self.vertices, divisions = [ 2,3,2], objectCentered = True, ol = 1, n = 'head_toon_LAT' )
		latBase = mn.Node( latNods[2] )
		latBase.parent = deGrp
		lat = mn.Node( latNods[1] )
		lat.parent = deGrp
		#mc.select( lat + ".pt[0:1][2][0]", lat + ".pt[0:1][2][1]" )
		topClus = mn.Node( mc.cluster(  lat.shape.name + ".pt[0:1][2][0]", lat.shape.name + ".pt[0:1][2][1]", n = 'top_face_toon_CLU' )[1] )
		topClus.a.v.v = False
		topClus.a.v.locked = True
		#mc.select( lat + ".pt[0:1][1][0]", lat + ".pt[0:1][1][1]" )
		midClus = mn.Node( mc.cluster(  lat.shape.name + ".pt[0:1][1][0]", lat.shape.name + ".pt[0:1][1][1]", n = 'mid_face_toon_CLU' )[1] )
		#mc.select( lat + ".pt[0:1][0][0]", lat + ".pt[0:1][0][1]" )
		lowClus = mn.Node( mc.cluster(  lat.shape.name + ".pt[0:1][0][0]", lat.shape.name + ".pt[0:1][0][1]", n = 'low_face_toon_CLU' )[1] )
		ctl = crv.Curve( "head_toon_CTL" )
		ctl = ctl.create( "sphere" )
		ctl.a.t.v = topClus.worldPosition
		mc.makeIdentity( ctl.name, apply = True, t = 1, r = 1, s = 1, n = 2 )
		topClus.parent = ctl
		midClus.parent = deGrp
		lowClus.parent = deGrp
		ctl.parent = grp
		#CONSTRAINS
		midClus.a.r >> topClus.a.r
		mc.pointConstraint( topClus.name, lowClus.name, midClus.name, mo = True )
		#SCALE FOR MID CLUSTER
		dist = mn.createNode( 'distanceBetween', n = 'head_toon_DIS' )
		ctl.a.worldMatrix >> dist.a.inMatrix1
		ctl.a.rp >> dist.a.point1
		lowClus.a.worldMatrix >> dist.a.inMatrix2
		lowClus.a.rp >> dist.a.point2
		mul = mn.createNode( 'multiplyDivide', n = 'head_toon_scale_MUL' )
		mul.a.input1.v = [dist.a.distance.v]*3
		mul.a.operation.v = 2
		dist.a.distance >> mul.a.input2X
		dist.a.distance >> mul.a.input2Y
		dist.a.distance >> mul.a.input2Z
		mul.a.output >> midClus.a.s
		#AIM CONSTRAINT
		upLocGrp = mn.Node( mc.group( n = "head_upVector_GRP", em = True ) )
		upLocGrp.a.t.v = midClus.worldPosition
		mc.makeIdentity( upLocGrp.name, apply = True, t = 1, r = 1, s = 1, n = 2 )
		upLocGrp.parent = deGrp
		mc.orientConstraint( ctl.name, lowClus.name, upLocGrp.name, mo = True )
		upLoc = mn.Node( mc.spaceLocator( n = 'head_upVector_LOC' )[0] )
		upLoc.a.t.v = midClus.worldPosition
		upLoc.a.tz.v = upLoc.a.tz.v + 5
		mc.aimConstraint( topClus.name, midClus.name, mo = True, weight = 1, aimVector = [1, 0, 0], upVector = [0, 1, 0], worldUpType = "object", worldUpObject = upLoc.name )
		upLoc.parent = upLocGrp
		mc.pointConstraint( topClus.name, lowClus.name, upLoc.name, mo = True )
		

