import rigging.utils.SoftModCluster.SoftModCluster as sf
reload( sf )
import rigging.utils.pointOnCurve.pointOnCurve as pCrv
import pipe.mayaFile.mayaFile as mfl
import os
import modeling.curve.curve as crv
reload( crv )

PYFILEDIR = os.path.dirname( os.path.abspath( __file__ ) )
lipsBaseFile = mfl.mayaFile( PYFILEDIR + '/lipsBase.ma' )
"""
1-Import file into the scene
2-Move the controls to modify the curves to match with the geometry lips
3-Build the system with the amount of controls that you want
Default is 3 controls, 3 UP, 3 DOWN and there is allways 1 for each lip corner.

"""

class Lips(object):
	"""basic rig for lips based on 2 curves
	it will create sticky joint controls with a default weight from a softMod"""
	def __init__(self):
		pass

	def create(self):
		"""this will import the face lips helpers curves"""
		lipsBaseFile.imp()
	
	def buildBase(self, shape, controlCount = 3):
		"""buid the system with the controul count"""
		#controls for bottom curve
		baseParam = 1.0 / ( controlCount + 1 )
		param = 0
		for c in range( controlCount ):
			param += baseParam 
			#BOTTOM
			pcurve = pCrv.PointOnCurve( 'bottom_base_mouth_crvShape' )
			pcurveNode = pcurve.nodeAt( param )
			pcurveNode.a.turnOnPercentage.v = 1
			curv = crv.Curve( 'bottom_lip_base_%i'%c + '_CRV' )
			curv.create( "sphere" )
			pcurveNode.attr( "result.position" ) >> curv.a.t

	def buildSystem(self):
		"""build the system with the softMods"""
		softMod = sf.SoftModCluster( 'bottom_lip_%i'%c + '_SFM', shape )
		softMod.create( pcurveNode.a.position.v[0] )
			
