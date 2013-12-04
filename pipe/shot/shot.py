
import os
import json
import pipe.mayaFile.mayaFile as mfl
import pipe.file.file as fl
import pipe.dependency.dependency as dp
reload( dp )

class Shot(object):
	"""main shot object"""
	def __init__(self, name, seq):
		self._name  = name
		self._sequence   = seq

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
		return fl.File( self.path + '/Comp/' + self.name + '_COMP.nk' )

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
			-1 : not updated
			0  : 0k file or not exists
			1  : updated"""
		depFiles = [ 
				[dp.Node( self.layPath   ),[]],
				[dp.Node( self.animPath  ),[ 0 ]],
				[dp.Node( self.hrsPath   ),[ 1 ]],
				[dp.Node( self.vfxPath   ),[ 1 ]],
				[dp.Node( self.simPath   ),[ 1 ]],
				[dp.Node( self.litPath   ),[ 1, 2, 3, 4 ]],
				[dp.Node( self.compPath  ),[ 5 ]]
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

	@property
	def exists(self):
		"""return if the shot exists"""
		return os.path.exists( self.path )

	def create(self):
		"""create folder structure"""
		struc = [
				'/' + self.name + '.breakdown',
				#ANIM
				'/Anim',
				'/Anim/Versions',
				'/Anim/Data',
				'/Anim/' + self.name + '_ANIM.avi',
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

		
