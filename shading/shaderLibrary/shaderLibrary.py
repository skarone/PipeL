'''
File: shaderLibrary.py
Author: Ignacio Urruty
Description:
	work with shaders =)
	handle shaders library
	TODO:
		Save settings and libraries path
		Save preview image
		UI
'''

import general.mayaNode.mayaNode as mn
reload( mn )
import pipe.mayaFile.mayaFile as mfl
try:
	import maya.cmds as mc
	import maya.mel as mm
except:
	pass
import json
import datetime
import os
import shutil
import general.ui.progressRender.progressRender as prR


ARNOLD_SETTINGS = { 'defaultResolution.width' : 400,
					'defaultResolution.height' : 400,
					"defaultArnoldRenderOptions.AASamples" : 4,
					"defaultArnoldRenderOptions.GIDiffuseSamples" : 2,
					"defaultArnoldRenderOptions.GIGlossySamples" : 2,
					"defaultArnoldRenderOptions.GIRefractionSamples" : 2,
					"defaultArnoldRenderOptions.sssSampleFactor" : 4,
					"defaultArnoldRenderOptions.GITotalDepth" : 10
					}

def shaderFromObject( obj ):
	"""return the shaders from the object"""
	if isinstance( obj , str ):
		obj = mn.Node( obj )
	if obj.type == 'transform':
		obj = mc.listRelatives( obj.name, c = True, s = True )
		if obj:
			obj = mn.Node( obj[0] )
	shGrp = mc.listConnections( obj, type = 'shadingEngine')
	if not shGrp:
		return None
	mat   = mc.listConnections( shGrp[0] + '.surfaceShader' )
	return Shader( mat[0])

def shaderFromSelection():
	"""return the shaders from selected objects"""
	sel = mn.ls( sl = 1, dag = True, s = True, ni = True )
	shaders = []
	for s in sel:
		sh = shaderFromObject( s )
		if sh:
			shaders.append( sh )
	if not shaders == []:
		return sorted(set(shaders))
	return None

def shadersFromScene():
	"""return all the shaders in the scene"""
	sel = mn.ls( dag = True, s = True, ni = True )
	shaders = []
	for s in sel:
		sh = shaderFromObject( s )
		if sh:
			shaders.append( sh )
	if not shaders == []:
		return sorted(set(shaders))
	return None

class Shader(object):
	"""class to handle shaders in pipe"""
	def __init__( self, name, category = None, library = None ):
		self._name       = name
		self._category   = category
		self._library    = library
		self._data = None

	@property
	def name(self):
		"""return name of the shader"""
		return self._name

	@property
	def library(self):
		"""return the library that the shader is using"""
		return self._library

	@property
	def path(self):
		"""return the path of the shader in the library"""
		libPath = self._library.path
		_path = libPath +  self.category + '/'
		if self._library.isProps:
			_path += 'shaders/'
		_path += self.name + '/'
		return _path

	@property
	def category(self):
		"""return the category of the shader"""
		return self._category

	@property
	def data(self):
		"""return the data of the shader"""
		if not self._data:
			with open( self.datapath, 'r' ) as dataFile:
				self._data = json.load( dataFile )
		return self._data

	@data.setter
	def data(self, data):
		"""save data file"""
		with open( self.datapath, 'w' ) as dataFile:
			json.dump( data, dataFile, sort_keys=True, indent=4, separators=(',', ': ') )

	@property
	def datapath(self):
		"""return the data path"""
		return self.path + self.name + '.data'

	@property
	def datatextures(self):
		"""return the textures of the exported shader"""
		return self.data['textures']

	@property
	def datanodes(self):
		"""return the nodes of the exported shader"""
		return self.data['nodes']

	@property
	def assets(self):
		"""return the assets that the shader was assign"""
		pass

	@assets.setter
	def assets(self, asset):
		"""add an asset to the assigned list"""
		pass

	@property
	def version(self):
		"""return the version of the shader"""
		pass

	@property
	def notes(self):
		"""get notes of the shader"""
		return self._data['notes']

	@notes.setter
	def notes(self, notes):
		"""add notes to the shader"""
		self._changedata( {'notes':notes} )

	@property
	def tags(self):
		"""return the tags of the shader"""
		return self._data['tags']

	@tags.setter
	def tags(self, tags):
		"""set tags for the shader"""
		self._changedata( {'tags':tags} )

	@property
	def previewtime(self):
		"""return the time it takes to make the preview image"""
		return self._data['previewtime']

	@property
	def published(self):
		"""return if the shader exists"""
		return os.path.exists( self.path )

	def publish(self, makePreview = False, tags = '', notes = '' ):
		"""export shader to library"""
		shad = mn.Node( self.name )
		mc.select( shad.shader, ne = True )
		exportPath = self.path + self.name + '.ma'
		if self.published: #Make a bakup
			self.saveVersion()
			print 'make a fucking backup!'
		else:
			os.makedirs( self.path )
		self._savedata( tags, notes, None )
		n = mn.Node( self.name )
		"""
		if not n.a.id.exists:
			n.a.id.add()
			print self.id
			n.a.id.v = self.id
		if not n.a.category.exists:
			n.a.category.add()
			n.a.category = self.category
		if not n.a.path.exists:
			n.a.path.add()
			n.a.path.v = exportPath
		"""
		mc.file( exportPath , force = True, options = "v=0", typ = "mayaAscii", pr = True, es = True )
		self.settexturespath( self.path + 'Textures/', exportPath )
		previewtime = 0
		if makePreview:
			print 'creating preview'
			previewtime = self.preview()

	def settexturespath( self, newPath, mayaFile ):
		"""move textures to new path and set that path in the nodes"""
		if not os.path.exists( newPath ):
			os.makedirs( newPath )
		for t in self.textures:
			curPath = t.a.ftn.v
			finalPath = newPath + curPath.split( '/' )[-1]
			if curPath == finalPath:
				continue
			shutil.copy2( curPath, finalPath )
			mayFile = mfl.mayaFile( mayaFile )
			mayFile.changeTextures( newDir = newPath )

	def saveVersion(self):
		"""make backup"""
		#get all files in path and move it to a folder inside the folder versions with the name of the shader + _v000 in it
		files = [a for a in os.listdir( self.path ) if not 'Versions' == a ]
		if os.path.exists( self.path + 'Versions' ):
			versionsNum = len( os.listdir( self.path + 'Versions' ) ) + 1
		else:
			versionsNum = 1
		versionsFolder = self.path + 'Versions/' + self.name + '_v' + str( versionsNum ).zfill( 3 ) + '/'
		if not os.path.exists(versionsFolder):
			os.makedirs( versionsFolder )
		for f in files:
			fil = self.path + f
			if os.path.isdir( fil ):
				shutil.copytree( fil, versionsFolder + f )
			else:
				shutil.copy2( fil, versionsFolder + f )

	@property
	def date(self):
		"""return the creating time"""
		return self.data['date']

	@property
	def id(self):
		"""return the id of the shader"""
		return self.data['id']

	def _savedata( self, tags, notes, previewtime = None ):
		"""recollect the data from scene and save the data"""
		data = {}
		ti = datetime.datetime.now()
		data['nodes']         = [ n.name for n in self.nodes ]
		data['textures']      = [ t.a.ftn.v for t in self.textures ]
		data[ 'date' ]        = ti.strftime("%Y-%m-%d %H:%M")
		data[ 'id' ]          = ti.strftime('%Y%m%d%H%M%S%f')
		data[ 'tags' ]        = tags
		data[ 'notes' ]       = notes
		data[ 'previewtime' ] = previewtime
		self.data = data

	def _changedata( self, newdata ):
		"""change data with newone"""
		data = self.data
		data.update( newdata )
		self.data = data

	def importShader( self ):
		"""import shader to scene"""
		impPath = self.shaderPath
		namespace = self.name
		shadCount = ''
		if self.exists:
			shadCount = len( mc.ls( self.name + '*:' + self.name  ))
		mc.file( impPath, i = True, type = "mayaAscii", namespace = namespace, options = "v=0", pr = True, loadReferenceDepth = "all" )
		return shadCount

	@property
	def shaderPath(self):
		"""return the path of the shader"""
		return self.path + self.name + '.ma'

	def preview(self):
		"""render shader to create thumbnail"""
		self.createPreviewMayaFile()
		#render preview
		prR.runBar( self.path + self.name + 'Preview.ma' )

	def createPreviewMayaFile(self):
		"""docstring for createPreviewMayaFile"""
		createPrevScript = os.path.dirname(os.path.abspath(__file__)) + '/createPreview.py'
		cmd = 'C:/"Program Files"/Autodesk/Maya' + mc.about(v = True)  + '/bin/' + 'mayapy.exe ' + createPrevScript + ' ' + self.path + self.name + '.ma'
		print cmd
		#create preview scene
		os.popen( cmd )

	@property
	def previewpath(self):
		"""return the path of the preview image"""
		return self.path + self.name + '.png'

	@property
	def previewMayaFile(self):
		"""return the preview maya file"""
		return mfl.mayaFile( self.path + self.name + 'Preview' + '.ma' )

	def delete(self):
		"""delete shader from library"""
		if os.path.exists(self.path, self._library.path + 'Deleted/' + self.category + '/' + self.name):
			shutil.rmtree( self.path, self._library.path + 'Deleted/' + self.category + '/' + self.name )
		shutil.copytree( self.path, self._library.path + 'Deleted/' + self.category + '/' + self.name )
		shutil.rmtree(self.path)

	def assign(self):
		"""assign shader to selection"""
		sel = mn.ls( sl = True )
		if sel:
			#if not self.exists:
			shadCount = self.importShader()
			mc.select( sel )
			mc.hyperShade( a = self.name + str( shadCount ) + ':' + self.name )

	#SCENE Tools
	@property
	def exists(self):
		"""return if the shader exists in scene"""
		return mc.objExists( self.name + ':' + self.name )

	def remove(self):
		"""remove shader from scene"""
		mc.delete( self.name )

	@property
	def textures(self):
		"""return the textures of the shader if there is in the scene"""
		nods = self.nodes
		if nods:
			tex = [ t for t in nods if t.type == 'file' ]
			if tex:
				return tex
		return []

	@property
	def nodes(self):
		"""return the nodes of the shader if there is in the scene"""
		nodes = mc.hyperShade( lun = self.name )
		if nodes:
			return [ mn.Node(n) for n in nodes]
		return []

class ShaderLibrary( object ):
	"""handle the library of shaders"""
	def __init__(self, path, isProps = False ):
		"""init library with a sepecific path.."""
		path = path.replace( '\\', '/')
		if not path.endswith( '/' ):
			path += '/'
		self._path    = path
		self._isProps = isProps

	def allshaders( self, filter = { 'name' : None, 'tag' : None, 'category' : None } ):
		"""return the shaders in the library"""
		categories = self.categories
		shaders = []
		for c in categories:
			shaders.extend( self.shadersincategory( c ) )
		return shaders

	@property
	def categories(self):
		"""return the categories in the library"""
		cats = [a for a in os.listdir(self.path) if not a == 'Deleted' and os.path.isdir( self.path + a ) ]
		return cats

	def shadersincategory(self, category):
		"""return the shaders inside a category"""
		catPath = self.path + category + '/'
		if self._isProps:
			catPath += 'shaders/'
		shaders = [ Shader( a, category, self ) for a in os.listdir( catPath ) if os.path.isdir( catPath + a ) ]
		return shaders

	@property
	def isProps(self):
		"""return if the library es based on props folders"""
		return self._isProps

	@property
	def path(self):
		"""return the path of the library"""
		return self._path

	@property
	def exists(self):
		"""return if the library exists"""
		return os.path.exists( self.path )

	def create(self):
		"""create a library"""
		os.makedirs( self._path )

	def createCategory(self, newCatName):
		"""docstring for createCategory"""
		os.makedirs( self._path + '/' + newCatName )

	def delete(self):
		"""delete the library"""
		os.remove( self.path )

	def deleteCategory(self, category):
		"""docstring for deleteCategory"""
		shutil.copytree( self.path + category, self.path + 'Deleted/' + category )
		shutil.rmtree( self.path + category )

	def zip(self):
		"""zip library =)"""
		pass



