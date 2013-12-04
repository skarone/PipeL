import pipe.file.file            as fl
reload( fl )
try:
	import maya.cmds as mc
except:
	print 'outside Maya'
import re
import pipe.textureFile.textureFile as tfl
reload( tfl )
import pipe.file.file as fl
from functools import partial
import difflib

"""
import pipe.mayaFile.mayaFile as mfl
curFile = mfl.currentFile()
curFile.newVersion()


import pipe.mayaFile.mayaFile as mfl
reload( mfl )

asd = mfl.mayaFile( r'D:\Projects\DogMendoncaAndPizzaBoy\Assets\Almanaque\Almanaque_FINAL.ma' )
asd.textures

"""

def currentFile():
	"""return the current working file"""
	return mayaFile( mc.file( q = True, sn = True  ) )

class mayaFile(fl.File):
	"""handle maya Files, interal and externally"""
	def __init__(self, path):
		super(mayaFile, self).__init__( path )

	def newVersion(self):
		"""create a new Version File"""
		super(mayaFile, self).newVersion()
		self.save()
		
	def save(self):
		"""save current file"""
		mc.file( s = True, type='mayaAscii' )
	
	@property
	def textures(self):
		"""return the textures on the maya File"""
		textures = []
		for l in self.lines:
			match =  re.search( '(:?.+".ftn" -type "string" ")(?P<Path>.+)"', l )
			if match:
				textures.append( tfl.textureFile( match.group("Path") ) )
		match =  re.findall( '(:?.+"fileTextureName".+[\n]?[\t]*" -type \\\\"string\\\\" \\\\")(?P<Path>.+)\\\\""', self.data )
		for m in match:
			textures.append( tfl.textureFile( m[-1] ) )
		return textures
		
	def changeTextures(self, newDir = '', newRes = '', newExtension = ''):
		"""change texture path or resolution or extension.."""
		file_str = re.sub( '(?:.+".ftn" -type "string" ")(?P<Path>.+)(?:")', partial( self._changeTexture, newDir, newRes, newExtension ), self.data )
		# do stuff with file_str

		with open(self.path, "w") as f:
			f.write(file_str)

	def _changeTexture( self, newDir, newRes, newExtension, matchobj):
		"""change matched texture path based on new information"""
		path = matchobj.group( "Path" )
		newPath = path
		if not newRes == '':
			newPath = self.setRes( newRes, newPath )
		if not newDir == '':
			newPath = newDir + fl.File( newPath ).basename
		if not newExtension == '':
			newPath = newPath.replace( fl.File( newPath ).extension, newExtension )
		return matchobj.group( 0 ).replace( path, newPath )

	@property
	def references(self):
		"""return the references in the scene"""
		references = []
		match =  re.findall( '(:?file -rdi [12] .+[\n]?[\t]* ")(?P<Path>.+)";', self.data )
		for m in match:
			references.append( mayaFile( m[-1] ) )
		return references

	def copy( self, newPath ):
		"""custom copy"""
		super( mayaFile, self ).copy( newPath )
		print 'copiando ', self.path, newPath
		#COPY TEXTURES AND FILES
		self.copyDependences( mayaFile( newPath ) )

	def copyDependences( self, newPathFile ):
		"""copy all the dependences of the newPathFile... it will read from newFile instead of original"""
		lon = 0
		base = 0
		s = difflib.SequenceMatcher( None, self.path, newPathFile.path )
		for block in s.get_matching_blocks():
			if block[2] > lon:
				lon = block[2]
				base = block[0]
				finalbase = block[1]
		BasePath = self.path[:base]
		finalBasePath = newPathFile.path[:finalbase]
		self.copyTextures( newPathFile, BasePath, finalBasePath )
		self.copyCaches( newPathFile, BasePath, finalBasePath )
		self.copyReferences( newPathFile, BasePath, finalBasePath )

	def copyTextures( self, newPathFile, BasePath, finalBasePath ):
		"""docstring for copyTextures"""
		for t in newPathFile.textures:
			origTexture = tfl.textureFile( t.path.replace( finalBasePath, BasePath ) )
			if not origTexture.exists:
				continue
			if t.exists:
				if not t.isOlderThan( origTexture ):
					continue
			print 'copiando ', origTexture.path, t.path
			origTexture.copy( t.path )

	def copyReferences(self, newPathFile, BasePath, finalBasePath ):
		"""copy references from file, recursive"""
		for r in newPathFile.references:
			origRef = mayaFile( r.path.replace( finalBasePath, BasePath ) )
			if not origRef.exists:
				continue
			if r.exists:
				if not r.isOlderThan( origRef ):
					continue
			print 'copiando ', origRef.path, r.path
			origRef.copy( r.path )

	@property
	def caches(self):
		"""return the caches in the scene"""
		caches = []
		match =  re.findall( '(:?.+".fn" .+[\n]?[\t]* ")(?P<Path>.+abc)";', self.data )
		for m in match:
			caches.append( fl.File( m[-1] ) )
		print caches
		return caches

	def copyCaches(self, newPathFile, BasePath, finalBasePath ):
		"""copy all the caches in the file"""
		for r in newPathFile.caches:
			origRef = mayaFile( r.path.replace( finalBasePath, BasePath ) )
			if not origRef.exists:
				continue
			if r.exists:
				if not r.isOlderThan( origRef ):
					continue
			print 'copiando ', origRef.path, r.path
			origRef.copy( r.path )

	def setRes(self, newRes, path ):
		tex = tfl.textureFile( path )
		if newRes == 'LOW':
			return tex.toLow().path
		elif newRes == 'MID':
			return tex.toMid().path
		elif newRes == 'HIGH':
			return tex.toHigh().path

	def imp(self):
		"""import file into scene"""
		mc.file( self.path, i = True, type = "mayaAscii", mergeNamespacesOnClash = False, rpr = self.name ,options = "v=0;", pr =True, loadReferenceDepth = "all" )
