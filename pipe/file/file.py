import os
import shutil
import time

#TODO -->
#	check os... methods
#

def filesInDir(root, scanSubFolders = True):
	"""return the files that are in the directory"""
	fils = []
	count = 0
	for path, subdirs, files in os.walk(root):
		if not scanSubFolders and count > 0:
			break
		for name in files:
			fils.append( File( os.path.join(path, name) ) )
		count += 1
	return fils

class File(object):
	versInFolds = True #the versions are collected in a folder
	paddingNum  = 3
	threshold = 1.0

	def __init__(self, path):
		"""init file node with full path"""
		self._path =  path
		self._data = None

	def __repr__(self):
		"""return the path"""
		return self._path

	def __str__(self):
		"""return path"""
		return self._path

	@property
	def path(self):
		"""return full path of the file"""
		return  self._path

	@property
	def exists(self):
		"""return if the file exists"""
		return os.path.exists( self.path )

	@property
	def date(self):
		"""return the modification date of the file"""
		return time.ctime(os.path.getmtime( self.path ))

	@property
	def dateNumber(self):
		"""return the modified date number"""
		return os.path.getmtime( self.path )

	@property
	def size(self):
		"""return the size of the file in bytes"""
		if not self.exists:
			return 0
		return os.path.getsize( self.path ) / ( 1024 * 1024.0 )#TODO check this method

	@property
	def basename(self):
		"""return the basename --> filename.ext"""
		return os.path.basename( self.path )

	@property
	def name(self):
		"""return file name without extension"""
		return os.path.splitext( self.basename )[0]#TODO check this method

	@property
	def fullName(self):
		"""return file name with extension"""
		return os.path.basename( self.path )

	@property
	def extension(self):
		"""return file extension without dot"""
		return os.path.splitext( self.basename )[1]#TODO check this method

	@property
	def dirPath(self):
		"""return directory path of the file"""
		return os.path.dirname( self.path ) + '/'

	@property
	def versionPath(self):
		"""return directory where the versions are"""
		if File.versInFolds:
			return self.dirPath + '/Versions/'
		else:
			return self.dirPath

	@property
	def version(self):
		"""return the number of version that the file is"""
		verPath = self.versionPath
		if not os.path.exists( verPath ):
			return 1
		verFils = [ a for a in os.listdir( verPath )
				if ( self.name in a
					and a.endswith( self.extension )
					and os.path.isfile( verPath + a )
				) ]
		return len( verFils ) + 1

	def create(self, path): #TODO
		"""method to create file if dosen't exists"""
		if not self.exists:
			print 'creating file in path', path
			return True
		else:
			print 'this file allready exists in', path
			return False

	"""
	def copy(self, newPath):
		newPath = newPath.replace( '//', '/' )
		if not os.path.exists(  os.path.dirname( newPath ) ):
			os.makedirs( os.path.dirname( newPath ) )
		trhC.ProgressDialog( self.path.replace( '//', '/' ), newPath )
		return File( newPath )

	"""

	def copy(self, newPath):
		"""copy file to new path,
		   newPath could be a directory path or a complete path and it will rename the file"""
		finalFile = ''
		if not os.path.exists( os.path.dirname( newPath ) ):
			os.makedirs( os.path.dirname( newPath ) )
		if os.path.isdir( newPath ):
			finalFile = File( str( newPath ) + '/' + str ( self.fullName ))
			if self.path == finalFile.path:
				return finalFile
			if finalFile.exists:
				finalFile.delete()
			shutil.copy2( self.path, finalFile.path )
			return finalFile
		else:
			finalFile = File( str( newPath ))
			if self.path == finalFile.path:
				return finalFile
			if finalFile.exists:
				finalFile.delete()
			shutil.copy2( self.path, finalFile.path )
		return finalFile

	def rename(self, newName):
		"""rename filename newName"""
		os.rename( self.path, self.dirPath + newName )
		self._path = self.dirPath + newName

	def newVersion(self):
		"""create a new Version of the file"""
		print self.versionPath + self.name + '_v' + str( self.version ).zfill( File.paddingNum ) + self.extension
		self.copy( self.versionPath + self.name + '_v' + str( self.version ).zfill( File.paddingNum ) + self.extension ) #TODO make correct padding for numbers

	def delete(self):
		"""delete file"""
		os.remove( self.path )

	def move(self, newPath):
		"""move file to newPath, same as copy but instead it will delete the original file"""
		self.copy( newPath )
		self.delete()

	def isOlderThan(self, fileToCompare):
		"""compare to File objects to see if the current one is older than"""
		fToCtime = round( os.path.getmtime(fileToCompare.path) )
		origFTime   = round( os.path.getmtime(self.path) )
		return fToCtime > origFTime

	def isBiggerThan(self, fileToCompare):
		"""compare File object size with another File object"""
		return self.size > fileToCompare.size

	@property
	def isZero(self):
		"""return if the file is a zero kbytes file"""
		return os.path.getsize( self.path ) == 0

	def replaceData(self, searchAndReplace = [] ):
		"""replace data in the file, by search and replace,
		searchAndReplace = [['string1','newString1'],['string2','newstring2']]"""
		filStr = self.data
		for s in searchAndReplace:
			filStr = filStr.replace( s[0], s[1] )
		self.write( filStr )

	@property
	def data(self):
		"""return the data if the file"""
		if not self._data:
			with open( self.path ) as f:
				self._data = f.read()
		return self._data

	def __eq__(self, other):
		return self.path == other.path

	@property
	def lines(self):
		"""return all the file in lines"""
		with open( self.path ) as f:
			file_str = f.readlines()
		return file_str

	def write(self, data):
		"""write data to file"""
		if not os.path.exists(self.dirPath):
			os.makedirs(self.dirPath)
		with open( self.path, "w" ) as f:
			f.write( data )
