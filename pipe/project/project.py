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

import sqlite3 as lite
import sys
import os
import pipe.asset.asset       as ass
reload( ass )
import pipe.sets.sets         as sets
reload( sets )
import pipe.sequence.sequence as seq
reload( seq )
import pipe.shot.shot as sh
reload( sh )
import pipe.settings.settings as sti
reload( sti )

BASE_PATH = 'P:/'
USE_MAYA_SUBFOLDER = True

def shotOrAssetFromFile(mayaFile):
	"""return from maya File if there is an asset, a shot or what"""
	setti = sti.Settings()
	gen = setti.General
	if gen:
		basePath = gen[ "basepath" ]
		if basePath:
			BASE_PATH = basePath.replace( '\\', '/' )
		usemayasubfolder = gen[ "usemayasubfolder" ]
	split = mayaFile.path.replace( BASE_PATH, '' ).split( '/' )
	print split
	if 'Assets' in mayaFile.path:
		#P:\Sprite_Gallo\Maya\Assets\Gallo\Gallo_Final.ma
		area = split[-1].split( '.' )[0][ split[-1].rindex( '_' )+1:]
		index = [ass.AREAS.index(i) for i in ass.AREAS if i.lower() in area.lower()]
		print index, 'index', area, 'area'
		if usemayasubfolder == 'True':
			assName = split[3]
		else:
			assName = split[2]
		return ass.Asset( assName, Project(split[0], BASE_PATH), index[0] )
	elif 'Shots' in mayaFile.path:
		#P:\Sprite_Gallo\Maya\Sequences\Entrevista\Shots\s001_T01\Anim\s001_T01_ANIM.ma
		if usemayasubfolder == 'True':
			area    = split[7]
			seqName = split[4]
			shotName = split[6]
		else:
		#P:\Sprite_Gallo\Sequences\Entrevista\Shots\s001_T01\Anim\s001_T01_ANIM.ma
			area = split[6]
			seqName = split[3]
			shotName = split[5]
		index = [sh.AREAS.index(i) for i in sh.AREAS if i.lower() in area.lower()]
		print shotName, seqName, split[0], index[0]
		return sh.Shot( shotName, seq.Sequence( seqName, Project( split[0],BASE_PATH ) ), index[0] )
	else:
		return None

def projects( basePath = BASE_PATH):
	"""return all the projects in the basePath"""
	if os.path.exists( basePath ):
		return sorted([ a for a in os.listdir( basePath ) if os.path.isdir( basePath + '/' + a )])
	return []

class Project(object):
	"""project class"""
	def __init__(self, name, basePath = BASE_PATH ):
		self._name = name
		self._basePath = basePath

	@property
	def name(self):
		"""return the name of the project"""
		return self._name

	@property
	def path(self):
		"""return the path of the Project"""
		base = self._basePath
		if base.endswith( '/' ):
			base = base[:-1]
		if USE_MAYA_SUBFOLDER:
			return base + '/' + self.name + '/Maya'
		else:
			return base + '/' + self.name

	@property
	def assetsPath(self):
		"""return the assets base path"""
		return self.path + '/Assets/'

	@property
	def sequencesPath(self):
		"""return the sequences base path"""
		return self.path + '/Sequences/'

	@property
	def setsPath(self):
		"""return the sets base path"""
		return self.path + '/Sets/'

	@property
	def exists(self):
		"""check if the project exists"""
		return os.path.exists( self.path )

	@property
	def assets(self):
		"""return the assets in the project"""
		if os.path.exists( self.assetsPath ):
			return [ ass.Asset( a, self ) for a in sorted(os.listdir( self.assetsPath )) if os.path.isdir( self.assetsPath + '/' + a ) ]
		else:
			return []

	@property
	def sets(self):
		"""return the sets in the project"""
		if os.path.exists( self.setsPath ):
			return [ sets.Set( s, self ) for s in sorted(os.listdir( self.setsPath )) ]
		else:
			return []

	@property
	def sequences(self):
		"""return the sequences in the project"""
		if os.path.exists( self.sequencesPath ):
			return [ seq.Sequence( s, self ) for s in sorted(os.listdir( self.sequencesPath )) if os.path.isdir( self.sequencesPath + s )  ]
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

	@property
	def databasePath(self):
		"""return the database path"""
		return self.path + '/' + self.name + '.db'

	@property
	def database(self):
		"""return the database to work with"""
		return lite.connect( self.databasePath )

	def getAssetPath(self, name, area):
		"""docstring for getAsset"""
		if area == '':
			return None
		if area == 'Model':
			areaNumber = 0
		elif area == 'Shading':
			areaNumber = 1
		elif area == 'Hrs':
			areaNumber = 2
		elif area == 'Rig':
			areaNumber = 3
		elif area == 'Final':
			areaNumber = 4
		return ass.Asset( name, self ).areaPath( areaNumber )

	def getShotPath(self, sequ, name, area):
		"""docstring for getShot"""
		if area == '':
			return None
		return sh.Shot( name, seq.Sequence( sequ, self ) ).areaPath( area )

	def sequence(self, seqName):
		"""return sequence object"""
		return seq.Sequence( seqName, self )

	def asset(self, assName):
		"""return asset object"""
		return ass.Asset( assName, self )
