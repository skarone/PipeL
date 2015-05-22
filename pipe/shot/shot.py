
import os
import json
import pipe.mayaFile.mayaFile as mfl
reload( mfl )
import pipe.file.file as fl
import pipe.dependency.dependency as dp
import pipe.cacheFile.cacheFile as cfl
import pipe.nukeFile.nukeFile   as nfl
reload( nfl )
reload(cfl)
reload( dp )

AREAS = [ 'Lay',
			'Anim',
			'Hrs',
			'Vfx',
			'Sim',
			'SkinFix',
			'Lit',
			'Comp'
		]

class Shot(object):
	"""main shot object"""
	def __init__(self, name, seq, area = 0):
		self._name  = name
		self._sequence   = seq
		self._area = AREAS[0]

	@property
	def type(self):
		"""return shot type"""
		return 'shot'

	@property
	def name(self):
		"""return name of the shot"""
		return self._name
	
	@property
	def sequence(self):
		"""return sequence of the shot"""
		return self._sequence

	@property
	def project(self):
		"""docstring for project"""
		return self.sequence.project

	@property
	def path(self):
		"""return the path of the shot"""
		return self.sequence.path + '/Shots/' +  self.name

	@property
	def layPath(self):
		"""return the anim file"""
		return mfl.mayaFile( self.path + '/Lay/' + self.name + '_LAY.ma' )

	@property
	def hasLay(self):
		"""return if there is layout file"""
		return os.path.getsize( self.layPath.path ) != 0

	@property
	def animPath(self):
		"""return the anim file"""
		return mfl.mayaFile( self.path + '/Anim/' + self.name + '_ANIM.ma' )

	@property
	def skinfixPath(self):
		"""return the skin fix file"""
		return mfl.mayaFile( self.path + '/SkinFix/' + self.name + '_SKINFIX.ma' )

	@property
	def hasSkinFix(self):
		"""docstring for hasSkinFix"""
		return os.path.getsize( self.skinfixPath.path ) != 0

	@property
	def hasAnim(self):
		"""return if there is layout file"""
		return os.path.getsize( self.animPath.path ) != 0

	@property
	def litPath(self):
		"""return the anim file"""
		return mfl.mayaFile( self.path + '/Lit/' + self.name + '_LIT.ma' )

	@property
	def hasLit(self):
		"""return if there is layout file"""
		return os.path.getsize( self.litPath.path ) != 0

	@property
	def compPath(self):
		"""return the anim file"""
		return nfl.nukeFile( self.path + '/Comp/' + self.name + '_COMP.nk' )

	@property
	def hasComp(self):
		"""return if there is layout file"""
		return os.path.getsize( self.compPath.path ) != 0

	@property
	def simPath(self):
		"""return the anim file"""
		return mfl.mayaFile( self.path + '/Sim/' + self.name + '_SIM.ma' )

	@property
	def hasSim(self):
		"""return if there is layout file"""
		return os.path.getsize( self.simPath.path ) != 0

	@property
	def hrsPath(self):
		"""return the anim file"""
		return mfl.mayaFile( self.path + '/Hrs/' + self.name + '_HRS.ma' )

	@property
	def hasHrs(self):
		"""return if there is layout file"""
		return os.path.getsize( self.hrsPath.path ) != 0

	@property
	def vfxPath(self):
		"""return the anim file"""
		return mfl.mayaFile( self.path + '/Vfx/' + self.name + '_VFX.ma' )

	@property
	def hasVfx(self):
		"""return if there is layout file"""
		return os.path.getsize( self.vfxPath.path ) != 0

	@property
	def status(self):
		"""return an array with the status of the files in the shot,
		return:
			0  : 0k file
			1  : updated
			2  : not Updated
			3  : not exists"""
		depFiles = [ 
				[dp.Node( self.layPath      ),[]],
				[dp.Node( self.animPath     ),[ 0 ]],
				[dp.Node( self.skinFixPath  ),[ 1 ]],
				[dp.Node( self.hrsPath      ),[ 1 ]],
				[dp.Node( self.vfxPath      ),[ 1 ]],
				[dp.Node( self.simPath      ),[ 1 ]],
				[dp.Node( self.litPath      ),[ 1, 2, 3, 4, 5 ]],
				[dp.Node( self.compPath     ),[ 6 ]]
				]
		res = dp.dep_resolvedArray( depFiles )
		result = []
		for i,f in enumerate( depFiles ):
			value = 1
			if not f[0].name.exists:
				value = 3
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
						value = 2
						break
			result.append( value )
		return result

	@property
	def exists(self):
		"""return if the shot exists"""
		return os.path.exists( self.path )

	@property
	def skinFixPath(self):
		"""docstring for skinFixPath"""
		return mfl.mayaFile( self.path + '/SkinFix/' + self.name + '_SKIN.ma' )

	@property
	def hasSkin(self):
		"""docstring for hasSkin"""
		return os.path.getsize( self.skinFixPath.path ) != 0
	
	def renderedLayersPath(self, basePath):
		path = basePath + '/' + self.project.name + '/' + self.sequence.name + '/' + self.name + '/'
		return path

	def renderedLayers(self, basePath):
		"""return the rendered layers for this shot, based on render path"""
		path = self.renderedLayersPath( basePath )
		if os.path.exists( path ):
			return [ a for a in os.listdir( path ) if os.path.isdir( path + a ) ]
		return []

	def renderedLayerVersions(self, basePath, layerName ):
		"""return the versions in the render layer"""
		path = self.renderedLayersPath( basePath ) + '/' + layerName
		if os.path.exists( path ):
			return sorted([ a for a in os.listdir( path ) if os.path.isdir( path + '/' + a ) ])
		return []

	def renderedLayerVersionPath(self, basePath, layerName, versionName ):
		"""return the path for the rendered layer for specific version"""
		path = self.renderedLayersPath( basePath ) + layerName + '/' + versionName + '/'
		return path

	@property
	def animCachesPath(self):
		"""docstring for animCachesDir"""
		return self.path + '/Pool/Anim/'

	@property
	def simCachesPath(self):
		"""docstring for animCachesDir"""
		return self.path + '/Pool/Sim/'

	@property
	def skinFixCachesPath(self):
		"""docstring for animCachesDir"""
		return self.path + '/Pool/SkinFix/'

	@property
	def vfxCachesPath(self):
		"""docstring for vfxCachesPath"""
		return self.path + '/Pool/Vfx/'

	@property
	def caches(self):
		"""return the caches in the scene"""
		animCaches = self._cachesInPath( self.animCachesPath )
		simCaches  = self._cachesInPath( self.simCachesPath )
		skinFixCaches  = self._cachesInPath( self.skinFixCachesPath )
		vfxCaches  = self._cachesInPath( self.skinFixCachesPath )
		return {'anim':animCaches, 'sim':simCaches, 'skin':skinFixCaches, 'vfx':vfxCaches }

	@property
	def cachesPriorities(self):
		"""return the cache ordered by priority"""
		return [ 'vfx', 'sim', 'skin', 'anim' ]

	def _cachesInPath(self, path ):
		"""return caches in path"""
		if os.path.exists( path ):
			return [ cfl.CacheFile( path + a ) for a in os.listdir( path ) if '.abc' in a]
		return []

	def create(self):
		"""create folder structure"""
		struc = [
				'/' + self.name + '.breakdown',
				'/Assets',
				#ANIM
				'/Anim',
				'/Anim/Versions',
				'/Anim/Data',
				'/Anim/' + self.name + '_ANIM.mov',
				'/Anim/' + self.name + '_ANIM.ma',
				#ASSETS
				'/Assets',
				#COMP
				'/Comp',
				'/Comp/Versions',
				'/Comp/Data',
				'/Comp/' + self.name + '_COMP.nk',
				#HRS
				'/Hrs',
				'/Hrs/Versions',
				'/Hrs/Data',
				'/Hrs/' + self.name + '_HRS.ma',
				#LAY
				'/Lay',
				'/Lay/Versions',
				'/Lay/Data',
				'/Lay/' + self.name + '_LAY.ma',
				#LIT
				'/Lit',
				'/Lit/Versions',
				'/Lit/Data',
				'/Lit/' + self.name + '_LIT.ma',
				#SKINFIX
				'/SkinFix',
				'/SkinFix/Versions',
				'/SkinFix/Data',
				'/SkinFix/' + self.name + '_SKIN.ma',
				#POOL
				'/Pool',
				'/Pool/Anim',
				'/Pool/Anim/Versions',
				'/Pool/Cam',
				'/Pool/Cam/Versions',
				'/Pool/Cam/' + self.name + '_CAM.ma',
				'/Pool/Hrs',
				'/Pool/Hrs/Versions',
				'/Pool/Sim',
				'/Pool/Sim/Versions',
				'/Pool/Vfx',
				'/Pool/Vfx/Versions',
				'/Pool/Sets',
				'/Pool/Sets/Versions',
				#SIM
				'/Sim',
				'/Sim/Versions',
				'/Sim/Data',
				'/Sim/' + self.name + '_SIM.ma',
				#VFX
				'/Vfx',
				'/Vfx/Versions',
				'/Vfx/Data',
				'/Vfx/' + self.name + '_VFX.ma',
				#CROWD
				'/Crowd',
				'/Crowd/Versions',
				'/Crowd/Data',
				'/Crowd/' + self.name + '_CROWD.ma'
				]
		for s in struc:
			s = self.path + s
			basedir = os.path.dirname( s )
			if not os.path.exists(basedir):
				os.makedirs(basedir)
			if '.' in s:
				open(s, 'a').close()

	@property
	def setsPath(self):
		"""return sets path of the pool"""
		return self.path + '/Pool/Sets/'

	@property
	def sets(self):
		"""return the sets exported in the pool"""
		if os.path.exists( self.setsPath ):
			return [ mfl.mayaFile( self.setsPath + o ) for o in os.listdir( self.setsPath ) if '.ma' in o ]
		return []

	@property
	def assetsPath(self):
		"""return assets paths"""
		return self.path + '/Assets/'

	@property
	def assets(self):
		"""return all the assets in the shot"""
		return [ a for a in os.listdir( self.assetsPath ) if os.path.isdir( self.assetsPath + a )]

	@property
	def breakdownPath(self):
		"""return the path of the breakdown"""
		return self.path + '/' + self.name + '.breakdown'

	@property
	def breakdown(self):
		"""docstring for breakdown"""
		data = []
		with open(self.breakdownPath) as data_file:    
			data = json.load(data_file)
		return data

	@breakdown.setter
	def breakdown(self, breakdown):
		"""save breakdown file"""
		with open( self.breakdownPath, 'w') as outfile:
			json.dump( breakdown, outfile, sort_keys=True, indent=4, separators=(',', ': ') )

	def areaState(self, area):
		"""return the current state of the asset in the area, for example In Progress, o pending"""
		pass

	def setAreaState(self, area, state):
		"""set the state of the asset in the area"""
		pass

	def areaNotes(self, area):
		"""return the notes for the asset in the area"""
		pass

	def addAreaNote(self, note, area):
		"""add a note to an asset in the specific area"""
		pass

	def assignUserToArea(self, user, area):
		"""assign a user to for the asset to a specific area"""
		pass

	def assignedUserInArea(self, area):
		"""return the assigned used for this asset in the specific area"""
		pass

	@property
	def poolCamPath(self):
		""""""
		return self.path + '/Pool/Cam/' + self.name + '_CAM.ma'

	@property
	def poolCam(self):
		"""return pool camera file"""
		return mfl.mayaFile( self.poolCamPath )

	def areaPath(self, area):
		"""docstring for areaPath"""
		if area == '':
			return None
		if area == 'Lay':
			return self.layPath
		elif area == 'Anim':
			return self.animPath
		elif area == 'Hrs':
			return self.hrsPath
		elif area == 'Vfx':
			return self.vfxPath
		elif area == 'Sim':
			return self.simPath
		elif area == 'SkinFix':
			return self.skinFixPath
		elif area == 'Lit':
			return self.litPath
		elif area == 'Comp':
			return self.compPath
