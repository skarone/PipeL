
import os
import json

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

		
