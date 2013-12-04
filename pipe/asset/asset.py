'''
File: asset.py
Author: Ignacio Urruty
Description: 
	Asset object( system level ):
		-Create folders and files structure inside a project
		-Query states of production
'''
import os
import pipe.mayaFile.mayaFile as mfl
reload( mfl )
import pipe.textureFile.textureFile as tfl
reload( tfl )
import pipe.dependency.dependency as dp
reload( dp )

class Asset(object):
	"""asset production object in the system, files and folders"""
	def __init__(self, name, project):
		self._name    = name
		self._project = project

	@property
	def name(self):
		"""return the name of the asset"""
		return self._name
	
	@property
	def project(self):
		"""get the project of the asset"""
		return self._project

	@property
	def exists(self):
		"""check if the asset exists in the project"""
		return os.path.exists( self.path )

	@property
	def path(self):
		"""return the path of the asset"""
		return self.project.path + '/Assets/' + self.name

	def create(self):
		"""create folders and file structure"""
		if self.exists:
			raise 'This asset allready ' + self.name + 'exist in the project'
		struc = [
			"/" + self.name + "_FINAL.avi",
			"/" + self.name + "_FINAL.ma",
			"/" + self.name + "_FINAL.png",
			"/" + self.name + "_FINAL.ass",
			#HRS
			"/Hrs/",
			"/Hrs/" + self.name + "_HRS.ma",
			"/Hrs/Data/",
			"/Hrs/Versions/",
			#MODEL
			"/Model/",
			"/Model/" + self.name + "_MODEL.ma",
			"/Model/Data/",
			"/Model/Data/" + self.name + "_Front_Blueprint.jpg",
			"/Model/Data/" + self.name + "_Left_Blueprint.jpg",
			"/Model/Data/" + self.name + "_Top_Blueprint.jpg",
			"/Model/Versions/",
			"/Model/Zbrush/",
			"/Model/Zbrush/" + self.name + "_Zbrush.ztl",
			"/Model/Zbrush/Data/",
			"/Model/Zbrush/Versions/",
			#RIG
			"/Rig/",
			"/Rig/" + self.name + "_RIG.ma",
			"/Rig/Data/",
			"/Rig/Versions/",
			#SHADING
			"/Shading/",
			"/Shading/Data/",
			"/Shading/Mary/",
			"/Shading/Mary/" + self.name + "_MARY.mr",
			"/Shading/Mary/Data/",
			"/Shading/Mary/Versions/",
			"/Shading/Maya/",
			"/Shading/Maya/" + self.name + "_SHA.ma",
			"/Shading/Maya/Data/",
			"/Shading/Maya/Versions/",
			"/Shading/Zbrush/",
			"/Shading/Zbrush/" + self.name + "_Zbrush.ztl",
			"/Shading/Zbrush/Data/",
			"/Shading/Zbrush/Versions/",
			#TEXTURES
			"/Textures/",
			"/Textures/Data/",
			"/Textures/Versions/",
			"/Versions/",
			#ANIMATION
			"/Animation/",
			"/Animation/" + self.name + '_ANIM.ma',
			"/Animation/" + self.name + '_ANIM.ass',
			"/Animation/Versions/",
			]
		for s in struc:
			s = self.path + s
			basedir = os.path.dirname( s )
			if not os.path.exists(basedir):
				os.makedirs(basedir)
			if '.' in s:
				open(s, 'a').close()

	@property
	def rigPath(self):
		"""return the path of the rig"""
		return mfl.mayaFile( self.path + '/Rig/' + self.name + "_RIG.ma" )

	@property
	def hasRig(self):
		"""return if the asset has a rig"""
		return os.path.getsize( self.rigPath.path ) != 0

	@property
	def modelPath(self):
		"""return the path of the model"""
		return mfl.mayaFile( self.path + '/Model/' + self.name + "_MODEL.ma" )

	@property
	def hasModel(self):
		"""return if the asset has a model"""
		return os.path.getsize( self.modelPath.path ) != 0

	@property
	def hairPath(self):
		"""return hair path of the asset"""
		return mfl.mayaFile( self.path + '/Hrs/' + self.name + "_HRS.ma" )

	@property
	def hasHair(self):
		"""return if the asset has a Hair file"""
		return os.path.getsize( self.hairPath.path ) != 0

	@property
	def shadingPath(self):
		"""return shading path of the asset"""
		return mfl.mayaFile( self.path + '/Shading/Maya/' + self.name + "_SHA.ma" )

	@property
	def hasShading(self):
		"""return if the asset has a shading maya file"""
		return os.path.getsize( self.shadingPath.path ) != 0

	@property
	def texturesPath(self):
		"""return textures path for the asset"""
		return self.path + '/Textures/'

	@property
	def textures(self):
		"""return the textures of the asset"""
		return [ tfl.textureFile( self.texturesPath + a ) for a in os.listdir( self.texturesPath ) if os.path.isfile( self.texturesPath + a ) ] 

	@property
	def finalPath(self):
		"""return the FINAL path for the MA file"""
		return mfl.mayaFile( self.path + '/' + self.name + "_FINAL.ma" )

	@property
	def hasFinal(self):
		"""return if the asset has a final ma"""
		return os.path.getsize( self.finalPath.path ) != 0

	def imp(self, referenced = True):
		"""import asset to current scene, also can be referenced"""
		if not referenced:#IMPORT
			mc.file( self.finalPath, i = True )
		else:#REFERENCE
			mc.file( self.finalPath, reference=True, namespace=self.name )

	@property
	def status(self):
		"""return an array with the status of the files in the asset,
		return:
			-1 : not updated
			0  : 0k file or not exists
			1  : updated"""
		depFiles = [ 
				[dp.Node( self.modelPath   ),[]],
				[dp.Node( self.shadingPath ),[ 0 ]],
				[dp.Node( self.rigPath     ),[ 1, 3 ]],
				[dp.Node( self.hairPath    ),[ 0 ]],
				[dp.Node( self.finalPath   ),[ 2, 3 ]]
				]
		res = dp.dep_resolvedArray( depFiles )
		result = []
		for i,f in enumerate( depFiles ):
			value = 1
			if not f[0].name.exists:
				value = 0
			elif f[0].name.isZero:
				value = 0
			else:
				for deps in res[i][1]:
					if not deps.name.exists:
						continue
					elif deps.name.isZero:
						continue
					isOlder = f[0].name.isOlderThan( deps.name )
					if isOlder:
						value = -1
						break
			result.append( value )

		return result
