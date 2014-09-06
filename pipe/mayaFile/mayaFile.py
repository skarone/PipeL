import pipe.file.file            as fl
reload( fl )
try:
	import maya.cmds as mc
except:
	pass
import general.mayaNode.mayaNode as mn
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

#CHANGE ALL PATHS
import pipe.mayaFile.mayaFile as mfl
reload( mfl )

fil = mfl.mayaFile( r'C:/Users/iurruty/Documents/maya/projects/default/scenes/testCambioRutas.ma' )
fil.changePaths( srchAndRep = ['D:/Projects/','C:/Mierda/'] )

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
		if self.exists:
			super(mayaFile, self).newVersion()
		
	def save(self):
		"""save current file"""
		mc.file( rename = self.path )
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

	def changePathsBrutForce(self, srchAndRep = []):
		"""change all Paths in file but with brut force, instead of search textures or caches, just search paths to replace"""
		file_str = self.data.replace( srchAndRep[0].replace( '\\', '/' ), srchAndRep[1].replace( '\\', '/' ) )
		self.write( file_str )
		
	def changePaths(self,newDir = '', srchAndRep = []):
		"""change textures, references, and caches to new path"""
		#TEXTURES
		file_str = re.sub( '(?:.+".ftn" -type "string" ")(?P<Path>.+)(?:")', partial( self._changeTexture, newDir, '', '', srchAndRep ), self.data )
		#REFERENCES
		file_str = re.sub( '(:?file -r[d]*[i]*\s*[12]* .+[\n]?[\t]* (-shd )?")(?P<Path>.+)";', partial( self._changeReferences, newDir, srchAndRep ), file_str )
		#CACHES
		file_str = re.sub( '(:?.+".fn" .+[\n]?[\t]* ")(?P<Path>.+abc)";', partial( self._changeCache, newDir, srchAndRep ), file_str )
		self.write( file_str )

	def changeTextures(self, newDir = '', newRes = '', newExtension = '', srchAndRep = []):
		"""change texture path or resolution or extension.."""
		file_str = re.sub( '(?:.+".ftn" -type "string" ")(?P<Path>.+)(?:")', partial( self._changeTexture, newDir, newRes, newExtension, srchAndRep ), self.data )
		# do stuff with file_str
		self.write( file_str )

	def _changeTexture( self, newDir, newRes, newExtension, srchAndRep, matchobj):
		"""change matched texture path based on new information"""
		path = matchobj.group( "Path" )
		newPath = path
		if not newRes == '':
			newPath = self.setRes( newRes, newPath )
		if not newDir == '':
			newPath = newDir + fl.File( newPath ).basename
		if not newExtension == '':
			newPath = newPath.replace( fl.File( newPath ).extension, newExtension )
		if srchAndRep:
			newPath = newPath.replace( srchAndRep[0], srchAndRep[1] )
		return matchobj.group( 0 ).replace( path, newPath )

	def changeReferences(self,newDir = '', srchAndRep = []):
		"""change References Paths"""
		file_str = re.sub( '(?:file -r[d]*[i]*\s*[12]* .+[\n]?[\t]* (?:-shd )?")(?P<Path>.+)";', partial( self._changeReferences, newDir, srchAndRep ), self.data )
		# do stuff with file_str
		self.write( file_str )

	def _changeReferences(self,newDir, srchAndRep, matchobj ):
		"""docstring for _changeReferences"""
		path = matchobj.group( "Path" )
		newPath = path
		if not newDir == '':
			newPath = newDir + fl.File( newPath ).basename
		if srchAndRep:
			newPath = newPath.replace( srchAndRep[0], srchAndRep[1] )
		return matchobj.group( 0 ).replace( path, newPath )

	@property
	def references(self):
		"""return the references in the scene"""
		references = []
		refsPaths = []
		match =  re.findall( '(:?file -r[d]*[i]*\s*[12]* .+[\n]?[\t]* ")(?P<Path>\S+ma)";', self.data )
		for m in match:
			if m[-1] in refsPaths:
				continue
			refsPaths.append( m[-1])
			references.append( mayaFile( m[-1] ) )
		return references

	def allReferences(self):
		"""return all references in a recursive way
		import pipe.mayaFile.mayaFile as mfl
		fi = mfl.mayaFile( r'D:\Projects\Pony_Halloween_Fantasmas\Maya\Sequences\Terror\Shots\s007_T07\Lit\s007_T07_LIT.ma' )
		print fi.allReferences()"""
		allreferences = []
		for f in self.references:
			allreferences.append( f )
			allreferences.extend( f.allReferences() )
		return allreferences

	def allTextures(self):
		"""return all the textures from file and references"""
		textures = self.textures
		for r in self.allReferences():
			textures.extend( r.textures )
		return textures

	def changeCaches(self,newDir = '', srchAndRep = []):
		"""change References Paths"""
		file_str = re.sub( '(:?.+".fn" .+[\n]?[\t]* ")(?P<Path>.+abc)";', partial( self._changeCache, newDir, srchAndRep ), self.data )
		# do stuff with file_str
		self.write( file_str )

	def _changeCache(self,newDir, srchAndRep, matchobj ):
		"""docstring for _changeReferences"""
		path = matchobj.group( "Path" )
		newPath = path
		if not newDir == '':
			newPath = newDir + fl.File( newPath ).basename
		if srchAndRep:
			newPath = newPath.replace( srchAndRep[0], srchAndRep[1] )
		return matchobj.group( 0 ).replace( path, newPath )

	def copyAll( self, newPath, changePaths = True ):
		"""custom copy"""
		newPathFile = mayaFile( newPath )
		newPathFile.newVersion()
		super( mayaFile, self ).copy( newPath )
		print 'copiando ', self.path, newPath
		#COPY TEXTURES AND FILES
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
		self.copyDependences( newPathFile, BasePath, finalBasePath )
		if changePaths:
			newPathFile.changePathsBrutForce( srchAndRep = [BasePath, finalBasePath] )

	def copyDependences( self, newPathFile, BasePath, finalBasePath ):
		"""copy all the dependences of the newPathFile... it will read from newFile instead of original"""
		self.copyTextures( newPathFile, BasePath, finalBasePath )
		self.copyCaches( newPathFile, BasePath, finalBasePath )
		self.copyReferences( newPathFile, BasePath, finalBasePath )

	def copyTextures( self, newPathFile, BasePath, finalBasePath ):
		"""docstring for copyTextures"""
		for t in newPathFile.textures:
			origTexture = tfl.textureFile( t.path.replace( BasePath, finalBasePath ) )
			if not t.exists:
				continue
			if origTexture.exists:
				if not origTexture.isOlderThan( t ):
					continue
			print 'copiando ', t.path, origTexture.path
			t.copy( origTexture.path )
			#AUTO CREATE TX TODO!
			origTexture.makeTx( True )

	def copyReferences(self, newPathFile, BasePath, finalBasePath ):
		"""copy references from file, recursive"""
		for r in newPathFile.references:
			origRef = mayaFile( r.path.replace( BasePath, finalBasePath ) )
			if not r.exists:
				continue
			if origRef.exists:
				if not origRef.isOlderThan( r ):
					continue
			print 'copiando ', r.path, origRef.path
			r.copyAll( origRef.path )

	@property
	def caches(self):
		"""return the caches in the scene"""
		caches = []
		match =  re.findall( '(:?.+".fn" .+[\n]?[\t]* ")(?P<Path>\S+abc)";', self.data )
		for m in match:
			caches.append( fl.File( m[-1] ) )
		return caches

	def copyCaches(self, newPathFile, BasePath, finalBasePath ):
		"""copy all the caches in the file"""
		for r in newPathFile.caches:
			origRef = mayaFile( r.path.replace( BasePath, finalBasePath ) )
			if not r.exists:
				continue
			if origRef.exists:
				if not origRef.isOlderThan( r ):
					continue
			print 'copiando ', r.path, origRef.path
			origRef.newVersion()
			r.copy( origRef.path )

	def setRes(self, newRes, path ):
		tex = tfl.textureFile( path )
		if newRes == 'LOW':
			return tex.toLow().path
		elif newRes == 'MID':
			return tex.toMid().path
		elif newRes == 'HIGH':
			return tex.toHigh().path

	def imp(self, customNamespace = None):
		"""import file into scene"""
		if customNamespace:
			nodes = mc.file( self.path, i = True, type = "mayaAscii", mergeNamespacesOnClash = False,rnn = True, namespace = customNamespace, options = "v=0;", pr =True, loadReferenceDepth = "all" )
		else:
			nodes = mc.file( self.path, i = True, type = "mayaAscii", mergeNamespacesOnClash = False,rnn = True, options = "v=0;", pr =True, loadReferenceDepth = "all" )
		return mn.Nodes( nodes )

	def reference(self, customNamespace = None):
		"""reference current file"""
		if customNamespace:
			namespa = customNamespace
		else:
			namespa = self.name
		nodes = mc.file( self.path, r = True, type = "mayaAscii", gl = True, loadReferenceDepth = "all",rnn = True, shd = ["renderLayersByName", "shadingNetworks"] , mergeNamespacesOnClash = False, namespace = namespa, options = "v=0;" )
		return mn.Nodes(nodes)

	@property
	def time(self):
		"""return time setted in the file"""
		t =  re.search( '(:?currentUnit -l )(?P<Linear>.+)(:? -a )(?P<Angle>.+)(:? -t )(?P<Time>.+);', self.data )
		if t:
			lin = str( t.group('Linear') )
			angle = str( t.group('Angle') )
			tim = str( t.group('Time') )
		m =  re.search( '(:?.+playbackOptions -min )(?P<Min>.+)(:? -max )(?P<Max>.+)(:? -ast )(?P<Ast>.+)(:? -aet )(?P<Aet>.+) ";', self.data )
		if m:
			amin = int( m.group('Min') )
			amax = int( m.group('Max') )
			aast = int( m.group('Ast') )
			aaet = int( m.group('Aet') )
			return {'min':amin,'max':amax,'ast':aast,'aet':aaet, 'lin':lin,'angle':angle,'tim':tim}
		return {'lin':lin,'angle':angle,'tim':tim}
		

	def open(self):
		"""open file in current maya"""
		mc.file( self.path, f = True, options = "v=0;", typ = "mayaAscii", o = True )
