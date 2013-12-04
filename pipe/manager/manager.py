'''
File: manager.py
Author: Ignacio Urruty
Description: 
	With this module you can manage the entire project structure.
	-Add assets, sets, sequences
	-Query
	-Delete
'''

import pipe.project.project   as prj
reload( prj )
import pipe.asset.asset       as ass
reload( ass )
import pipe.sets.sets         as sets
reload( sets )
import pipe.sequence.sequence as seq
reload( seq )

class Manager(object):
	"""manager object to control the entire project"""
	def __init__(self, project, path = 'D:/Projects/'):
		self._path    = path
		self._project = prj.Project( project )
		self._project.BASE_PATH = path

	@property
	def path(self):
		"""return the path of the manager"""
		return self._path

	@property
	def projects(self):
		"""return the projects in the pipe"""
		return os.listdir( self.path )

	@property
	def project(self):
		"""return the current project"""
		return self._project

	def addAsset(self, assetName ):
		"""add an asset name to the project"""
		asset = ass.Asset( assetName, self.project )
		if not asset.exists():
			asset.create()

	def addSet(self, setName):
		"""add a set to the project"""
		st = sets.Set( setName, self.project )
		if not st.exists():
			st.create()

	def addSequence(self, seqName):
		"""add a sequence to the project"""
		sq = seq.Sequence( seqName, self.project )
		if not sq.exists():
			sq.create()

