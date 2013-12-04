'''
File: project.py
Author: Ignacio Urruty
Description: 
	Project object( system level ):
		-Create folders and files for the project
		-Query information about project
'''
import os
import pipe.asset.asset       as ass
reload( ass )
import pipe.sets.sets         as sets
reload( sets )
import pipe.sequence.sequence as seq
reload( seq )

BASE_PATH = 'D:/Projects/'

def projects():
	"""return all the projects in the BASE_PATH"""
	return os.listdir( BASE_PATH )

class Project(object):
	"""project class"""
	def __init__(self, name):
		self._name = name
	
	@property
	def name(self):
		"""return the name of the project"""
		return self._name

	@property
	def path(self):
		"""return the path of the Project"""
		return BASE_PATH + self.name

	def exists(self):
		"""check if the project exists"""
		return os.path.exists( self.path )

	@property
	def assets(self):
		"""return the assets in the project"""
		return [ ass.Asset( a, self ) for a in os.listdir( self.path + '/Assets/' ) ]

	@property
	def sets(self):
		"""return the sets in the project"""
		return [ sets.Set( s, self ) for s in os.listdir( self.path + '/Sets/' ) ]

	@property
	def sequences(self):
		"""return the sequences in the project"""
		return [ seq.Sequence( s, self ) for s in os.listdir( self.path + '/Sequences/' ) ]

	def create(self):
		"""create folder structure for the project"""
		struc = [
				'/Assets',
				'/Data',
				'/Sequences',
				'/Sets'
				]
		for s in struc:
			s = self.path + s + '/'
			os.makedirs( s )

	def addAsset(self, assetName ):
		"""add an asset name to the project"""
		asset = ass.Asset( assetName, self )
		if not asset.exists():
			asset.create()
		return asset

	def addSet(self, setName):
		"""add a set to the project"""
		st = sets.Set( setName, self )
		if not st.exists():
			st.create()
		return st

	def addSequence(self, seqName):
		"""add a sequence to the project"""
		sq = seq.Sequence( seqName, self )
		if not sq.exists():
			sq.create()
		return sq


