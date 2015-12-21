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
STUDIO_NAME = 'Bitt'

class Sequence(object):
	"""main sequence object"""
	def __init__(self, name, project):
		self._name = name
		self._project = project

	def __str__(self):
		"""docstring for __str__"""
		return self.name

	def __repr__(self):
		"""docstring for __rpr__"""
		return self.name

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
		return self.project.sequencesPath + self.name

	def create(self):
		"""create folders structure for sequence"""
		struc = [
				'/Assets',
				'/Shots',
				'/Data',
				'/Production',
				'/Production/Feedback',
				'/Production/Shooting',
				'/Production/Audio',
				'/Production/WS_Conforming',
				'/To_Client/WIPS',
				'/To_Client/Delivery',
				'/To_Client/Delivery/Versions',
				'/Materials/References',
				'/Materials/References/From_Client',
				'/Materials/References/From_' + STUDIO_NAME,
				'/Materials/References/From_' + STUDIO_NAME + '/Concepts',
				'/Materials/Offline',
				'/Materials/Story'
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
		if os.path.exists(self.path + '/Shots/'):
			return [ sht.Shot( a, self ) for a in sorted(os.listdir( self.path + '/Shots/' )) if os.path.isdir( self.path + '/Shots/' + a ) ]
		return []

	def shot(self, shtName):
		"""return shot object"""
		return sht.Shot( shtName, self)
