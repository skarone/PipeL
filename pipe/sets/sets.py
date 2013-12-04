'''
File: sets.py
Author: Ignacio Urruty
Description:
	Manage Set
	-Create folders
	-Read Breakdown
	-Generate Maya file
	Generate Set based on set.breakdown file
'''
import os
import json
import pipe.mayaFile.mayaFile as mfl
reload( mfl )
import pipe.dependency.dependency as dp
reload( dp )

class Set(object):
	"""class to handle sets"""
	def __init__(self, name, project):
		self._name    = name
		self._project = project
		
	@property
	def name(self):
		"""return the name of the Set"""
		return self._name

	@property
	def project(self):
		"""return the project object"""
		return self._project

	@property
	def path(self):
		"""return the path of the Set"""
		return self.project.path + '/Sets/' + self.name

	@property
	def exists(self):
		"""check if the Set exists"""
		return os.path.exists( self.path )

	def create(self):
		"""create Set Folder structure"""
		struc = [
				'/Assets',
				'/Versions',
				'/Model',
				'/Model/Data',
				'/Model/Versions',
				'/Model/' + self.name + '_MODEL.ma',
				'/' + self.name + '.breadown',
				'/' + self.name + '_FINAL.avi',
				'/' + self.name + '_FINAL.ma',
				'/' + self.name + '_FINAL.png'
				]
		for s in struc:
			s = self.path + s
			basedir = os.path.dirname( s )
			if not os.path.exists(basedir):
				os.makedirs(basedir)
			if '.' in s:
				open(s, 'a').close()

	@property
	def modelPath(self):
		"""return the path of the model"""
		return mfl.mayaFile( self.path + '/Model/' + self.name + "_MODEL.ma" )

	@property
	def hasModel(self):
		"""return if the asset has a model"""
		return os.path.getsize( self.modelPath.path ) != 0

	@property
	def finalPath(self):
		"""return the FINAL path for the MA file"""
		return mfl.mayaFile( self.path + '/' + self.name + "_FINAL.ma" )

	@property
	def hasFinal(self):
		"""return if the asset has a final ma"""
		return os.path.getsize( self.finalPath.path ) != 0

	def createBreakdown(self):
		"""create base file for breakdown"""
		data = {}
		data['Assets'] = {}
		self.breakdown = data

	@property
	def assets(self):
		"""return the assets that are in the breakdown file"""
		return self.breakdown[ 'Assets' ].keys()

	def saveAsset(self, assetName, coords):
		"""save coords for asset in the set.breakdown"""
		breakdown = self.breakdown
		print 'coords',coords
		breakdown[ 'Assets' ].update( { assetName:coords } )
		self.breakdown = breakdown

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

	@property
	def status(self):
		"""return an array with the status of the files in the asset,
		return:
			-1 : not updated
			0  : 0k file or not exists
			1  : updated"""
		depFiles = [ 
				[dp.Node( self.modelPath   ),[]],
				[dp.Node( self.finalPath   ),[ 0 ]]
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
