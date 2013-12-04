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
