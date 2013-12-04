'''
File: project.py
Author: Ignacio Urruty
Description: 
	Project object( system level ):
		-Create folders and files for the project
		-Query information about project
'''

"""
import pipe.project.project as prj
reload( prj )
#checkear texturas en project
dog = prj.Project( 'DogMendoncaAndPizzaBoy' )

for a in dog.assets:
    for t in a.finalPath.textures:
        if not t.exists:
            print a.name, t.path, 'NO EXISTE!'
            continue
        if not t.hasTx:
            print t.path, 'no tiene tx!'
            t.createVersions()
            t.toTx().copy( r'D:/Projects/DogMendoncaFarm/Textures/' )   

"""

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
	return [ a for a in os.listdir( BASE_PATH ) if os.path.isdir( BASE_PATH + a )]

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

	@property
	def exists(self):
		"""check if the project exists"""
		return os.path.exists( self.path )

	@property
	def assets(self):
		"""return the assets in the project"""
		if os.path.exists( self.path + '/Assets/' ):
			return [ ass.Asset( a, self ) for a in os.listdir( self.path + '/Assets/' ) ]
		else:
			return []

	@property
	def sets(self):
		"""return the sets in the project"""
		if os.path.exists( self.path + '/Assets/' ):
			return [ sets.Set( s, self ) for s in os.listdir( self.path + '/Sets/' ) ]
		else:
			return []

	@property
	def sequences(self):
		"""return the sequences in the project"""
		if os.path.exists( self.path + '/Assets/' ):
			return [ seq.Sequence( s, self ) for s in os.listdir( self.path + '/Sequences/' ) ]
		else:
			return []

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
		if not asset.exists:
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


