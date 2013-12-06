import rigging.utils.SoftModCluster.SoftModCluster as sf
reload( sf )
import pipe.mayaFile.mayaFile as mfl
import os
import modeling.curve.curve as crv
import general.curveScatter.curveScatter as crvScat
reload( crvScat )

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
		self._scatter = []

	def create(self):
		"""this will import the face lips helpers curves"""
		lipsBaseFile.imp()
	
	def buildBase(self):
		"""buid the system with the controul count"""
		#BOTTOM
		curv = crv.Curve( 'lip' + '_CRV' )
		curv.create( "sphere" )
		self._scatter.append( crvScat.CurveScatter( 
				curve = crv.Curve( 'bottom_base_mouth_crvShape' ), 
				objects = [curv],
				pointsCount = 5, 
				useTips = True, 
				keepConnected = True,
				tangent = 1,
				rand = 0 ) )
		self._scatter.append( crvScat.CurveScatter( 
				curve = crv.Curve( 'top_base_mouth_crvShape' ), 
				objects = [curv],
				pointsCount = 3, 
				useTips = False, 
				keepConnected = True,
				tangent = 1,
				rand = 0 ) )

	@property
	def scatters(self):
		"""return the scatters for the curves"""
		return self._scatter

	def buildSystem(self, shape ):
		"""build the system with the softMods"""
		for s in self.scatters:
			for i,n in enumerate( s._nodes ):
				softMod = sf.SoftModCluster( 'lip_' + '_%i'%i + '_SFM', shape )
				softMod.create( n.a.t.v[0] )
			
