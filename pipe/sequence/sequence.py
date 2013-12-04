'''
File: set.py
Author: Ignacio Urruty
Description:
	Manage Set
	-Create folders
	-Read Breakdown
	-Generate Maya file
	Generate Set based on set.breakdown file
'''
import pipe.shot.shot as sht
reload( sht )
import os

class Sequence(object):
	"""main sequence object"""
	def __init__(self, name, project):
		self._name = name
		self._project = project

	@property
	def name(self):
		"""return name of the sequence"""
		return self._name

	@property
	def project(self):
		"""return porject object"""
		return self._project

	@property
	def exists(self):
		"""return if the sequence exists"""
		return os.path.exists( self.path )

	@property
	def path(self):
		"""return the path of the sequence"""
		return self.project.path + '/Sequences/' + self.name

	def create(self):
		"""create folders structure for sequence"""
		struc = [
				'/Assets',
				'/Shots',
				'/Data'
				]
		for s in struc:
			s = self.path + s
			basedir = os.path.dirname( s )
			print s, basedir
			if not os.path.exists(s):
				if not '.' in s:
					os.makedirs(s)
			if '.' in s:
				open(s, 'a').close()

	def addShot(self, shotName):
		"""add shot to sequence"""
		sh = sht.Shot( shotName, self )
		sh.create()
		return sh
		
	@property
	def shots(self):
		"""return the shots in the sequence"""
		return [ sht.Shot( a, self ) for a in os.listdir( self.path + '/Shots/' ) ]
