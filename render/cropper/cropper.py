import general.mayaNode.mayaNode as mn
import maya.OpenMaya as OpenMaya
import maya.cmds as mc

class Cropper(object):
	"""plane for cropping at render time"""
	def __init__(self, camera):
		self._camera = camera
		self._masks = []

	def create(self):
		"""create cropper plane"""
		with ns.set( camera.name + '_CRP' ):
			grp = mc.group( n = 'cropper_grp' )

	@property
	def camera(self):
		"""camera of the cropper"""
		return self._camera

	@property
	def frustumPoints(self):
		"""return the frustum points"""
		mat = OpenMaya.MMatrix( )
		OpenMaya.MScriptUtil.createMatrixFromList(self.camera.a.worldMatrix.v, mat)
		near_clip  = self.camera.a.nearClipPlane.v
		far_clip   = self.camera.a.farClipPlane.v
		h_aperture = self.camera.a.horizontalFilmAperture.v
		v_aperture = self.camera.a.verticalFilmAperture.v
		fl         = self.camera.a.focalLength.v
		orthwidth  = self.camera.a.orthographicWidth.v
		orth       = self.camera.a.orthographic.v
		h_fov      = h_aperture * 0.5 / ( fl * 0.03937 );
		v_fov      = v_aperture * 0.5 / ( fl * 0.03937 );
		fright     = far_clip * h_fov;
		ftop       = far_clip * v_fov;
		nright     = near_clip * h_fov;
		ntop       = near_clip * v_fov;
		if orth:
			fright = ftop = nright = ntop = orthwidth/2.0;
		corners = []
		corner_a = OpenMaya.MPoint(fright,ftop,-far_clip);
		corner_a *= mat;
		corners.append( corner_a )
		corner_b = OpenMaya.MPoint(-fright,ftop,-far_clip);
		corner_b *= mat;
		corners.append( corner_b )
		corner_c = OpenMaya.MPoint(-fright,-ftop,-far_clip);
		corner_c *= mat;
		corners.append( corner_c )
		corner_d = OpenMaya.MPoint(fright,-ftop,-far_clip);
		corner_d *= mat;
		corners.append( corner_d )
		corner_e = OpenMaya.MPoint(nright,ntop,-near_clip);
		corner_e *= mat;
		corners.append( corner_e )
		corner_f = OpenMaya.MPoint(-nright,ntop,-near_clip);
		corner_f *= mat;
		corners.append( corner_f )
		corner_g = OpenMaya.MPoint(-nright,-ntop,-near_clip);
		corner_g *= mat;
		corners.append( corner_g )
		corner_h = OpenMaya.MPoint(nright,-ntop,-near_clip);
		corner_h *= mat;
		corners.append( corner_h )
		return corners


	def addBox(self):
		"""add a mask of type box to the cropper"""
		
