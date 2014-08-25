'''
File: asset.py
Author: Ignacio Urruty
Description: 
	Asset object( system level ):
		-Create folders and files structure inside a project
		-Query states of production
'''
import os
import pipe.mayaFile.mayaFile as mfl
reload( mfl )
import pipe.textureFile.textureFile as tfl
reload( tfl )
import pipe.dependency.dependency as dp
reload( dp )
try:
	import general.mayaNode.mayaNode as mn
except:
	pass

AREAS = [
		'Model',
		'Shading',
		'Hrs',
		'Rig',
		'Final'
		]

def getAssetsFromSelection( project ):
	"""return the assets from selection, also return the index of the area (Shading, Modeling, Rigging...)"""
	sel = mn.ls( sl = True )
	assets = []
	if sel:
		for s in sel:
			ass = getAssetFromNode(s, project)
			if not ass in assets:
				assets.append( ass )
	return assets

def getAssetFromNode(s, project):
	"""return the asset from a selected Node based on node name"""
	assetName = s.namespace.firstParent.name[1:]
	area = assetName[ assetName.rindex( '_' ):]
	index = [AREAS.index(i) for i in AREAS if i in area]
	if not index:
		index.append(0)
	return Asset( assetName[ :assetName.rindex( '_' )], project, index[0] ) 

class Asset(object):
	"""asset production object in the system, files and folders"""
	def __init__(self, name, project, area = 0):
		self._name    = name
		self._project = project
		self._area = AREAS[ area ]

	@property
	def type(self):
		"""return type"""
		return 'asset'

	@property
	def name(self):
		"""return the name of the asset"""
		return self._name
	
	@property
	def project(self):
		"""get the project of the asset"""
		return self._project

	@property
	def exists(self):
		"""check if the asset exists in the project"""
		return os.path.exists( self.path )

	@property
	def path(self):
		"""return the path of the asset"""
		return self.project.assetsPath + self.name

	def create(self):
		"""create folders and file structure"""
		if self.exists:
			raise 'This asset allready ' + self.name + 'exist in the project'
		struc = [
			"/" + self.name + "_" + AREAS[ 4 ] + ".mov",
			"/" + self.name + "_" + AREAS[ 4 ] + ".ma",
			"/" + self.name + "_" + AREAS[ 4 ] + ".png",
			"/" + self.name + "_" + AREAS[ 4 ] + ".ass",
			#HRS
			"/" + AREAS[ 2 ] + "/",
			"/" + AREAS[ 2 ] + "/" + self.name + "_" + AREAS[ 2 ] + ".ma",
			"/" + AREAS[ 2 ] + "/Data/",
			"/" + AREAS[ 2 ] + "/Versions/",
			#MODEL
			"/" + AREAS[ 0 ] + "/",
			"/" + AREAS[ 0 ] + "/" + self.name + "_" + AREAS[ 0 ] + ".ma",
			"/" + AREAS[ 0 ] + "/Data/",
			"/" + AREAS[ 0 ] + "/Data/" + self.name + "_Front_Blueprint.jpg",
			"/" + AREAS[ 0 ] + "/Data/" + self.name + "_Left_Blueprint.jpg",
			"/" + AREAS[ 0 ] + "/Data/" + self.name + "_Top_Blueprint.jpg",
			"/" + AREAS[ 0 ] + "/Versions/",
			"/" + AREAS[ 0 ] + "/Zbrush/",
			"/" + AREAS[ 0 ] + "/Zbrush/" + self.name + "_Zbrush.ztl",
			"/" + AREAS[ 0 ] + "/Zbrush/Data/",
			"/" + AREAS[ 0 ] + "/Zbrush/Versions/",
			#RIG
			"/" + AREAS[ 3 ] + "/",
			"/" + AREAS[ 3 ] + "/" + self.name + "_" + AREAS[ 3 ] + ".ma",
			"/" + AREAS[ 3 ] + "/Data/",
			"/" + AREAS[ 3 ] + "/Versions/",
			#SHADING
			"/" + AREAS[ 1 ] + "/",
			"/" + AREAS[ 1 ] + "/Data/",
			"/" + AREAS[ 1 ] + "/Mary/",
			"/" + AREAS[ 1 ] + "/Mary/" + self.name + "_MARY.mr",
			"/" + AREAS[ 1 ] + "/Mary/Data/",
			"/" + AREAS[ 1 ] + "/Mary/Versions/",
			"/" + AREAS[ 1 ] + "/Maya/",
			"/" + AREAS[ 1 ] + "/Maya/" + self.name + "_" + AREAS[ 1 ] + ".ma",
			"/" + AREAS[ 1 ] + "/Maya/Data/",
			"/" + AREAS[ 1 ] + "/Maya/Versions/",
			"/" + AREAS[ 1 ] + "/Zbrush/",
			"/" + AREAS[ 1 ] + "/Zbrush/" + self.name + "_Zbrush.ztl",
			"/" + AREAS[ 1 ] + "/Zbrush/Data/",
			"/" + AREAS[ 1 ] + "/Zbrush/Versions/",
			#TEXTURES
			"/Textures/",
			"/Textures/Data/",
			"/Textures/Versions/",
			"/Versions/",
			#ANIMATION
			"/Animation/",
			"/Animation/" + self.name + '_ANIM.ma',
			"/Animation/" + self.name + '_ANIM.ass',
			"/Animation/Versions/",
			]
		for s in struc:
			s = self.path + s
			basedir = os.path.dirname( s )
			if not os.path.exists(basedir):
				os.makedirs(basedir)
			if '.' in s:
				open(s, 'a').close()
		#Add asset to database

	def addToDatabase(self):
		"""add asset to database"""
		with self.project.database:
			c = conn.cursor()
			sql = 'CREATE TABLE Friends(Id INTEGER PRIMARY KEY, Name TEXT);'
			c.execute(sql)
			sql = "INSERT INTO Assets(Name) VALUES ('" + self.name + "');"
			cur.execute(sql)

	@property
	def rigPath(self):
		"""return the path of the rig"""
		return mfl.mayaFile( self.path + '/Rig/' + self.name + "_RIG.ma" )

	@property
	def hasRig(self):
		"""return if the asset has a rig"""
		return os.path.getsize( self.rigPath.path ) != 0

	@property
	def modelPath(self):
		"""return the path of the model"""
		return mfl.mayaFile( self.path + '/' + AREAS[ 0 ] + '/' + self.name + "_" + AREAS[ 0 ] + ".ma" )

	@property
	def hasModel(self):
		"""return if the asset has a model"""
		return os.path.getsize( self.modelPath.path ) != 0

	@property
	def hairPath(self):
		"""return hair path of the asset"""
		return mfl.mayaFile( self.path + '/' + AREAS[ 2 ] + '/' + self.name + "_" + AREAS[ 2 ] + ".ma" )

	@property
	def hasHair(self):
		"""return if the asset has a Hair file"""
		return os.path.getsize( self.hairPath.path ) != 0

	@property
	def shadingPath(self):
		"""return shading path of the asset"""
		return mfl.mayaFile( self.path + '/' + AREAS[ 1 ] + '/Maya/' + self.name + "_" + AREAS[ 1 ] + ".ma" )

	@property
	def hasShading(self):
		"""return if the asset has a shading maya file"""
		return os.path.getsize( self.shadingPath.path ) != 0

	@property
	def texturesPath(self):
		"""return textures path for the asset"""
		return self.path + '/Textures/'

	@property
	def textures(self):
		"""return the textures of the asset"""
		return [ tfl.textureFile( self.texturesPath + a ) for a in os.listdir( self.texturesPath ) if os.path.isfile( self.texturesPath + a ) ] 

	@property
	def finalPath(self):
		"""return the FINAL path for the MA file"""
		return mfl.mayaFile( self.path + '/' + self.name + "_" + AREAS[ 4 ] + ".ma" )

	@property
	def hasFinal(self):
		"""return if the asset has a final ma"""
		return os.path.getsize( self.finalPath.path ) != 0

	def imp(self, referenced = True):
		"""import asset to current scene, also can be referenced"""
		if not referenced:#IMPORT
			nodes = mc.file( self.finalPath, i = True, rnn = True, namespace=self.name )
		else:#REFERENCE
			nodes = mc.file( self.finalPath, reference=True,rnn = True , namespace=self.name )
		return mn.Nodes( nodes )

	@property
	def status(self):
		"""return an array with the status of the files in the asset,
		return:
			-1 : not updated
			0  : 0k file or not exists
			1  : updated"""
		depFiles = [ 
				[dp.Node( self.modelPath   ),[]],
				[dp.Node( self.shadingPath ),[ 0 ]],
				[dp.Node( self.rigPath     ),[ 1, 3 ]],
				[dp.Node( self.hairPath    ),[ 0 ]],
				[dp.Node( self.finalPath   ),[ 2, 3 ]]
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

	def areaState(self, area):
		"""return the current state of the asset in the area, for example In Progress, o pending"""
		pass

	def setAreaState(self, area, state):
		"""set the state of the asset in the area"""
		pass

	def areaNotes(self, area):
		"""return the notes for the asset in the area"""
		pass

	def addAreaNote(self, note, area):
		"""add a note to an asset in the specific area"""
		pass

	def assignUserToArea(self, user, area):
		"""assign a user to for the asset to a specific area"""
		pass

	def assignedUserInArea(self, area):
		"""return the assigned used for this asset in the specific area"""
		pass
