import pipe.textureFile.textureFile as tfl
import pipe.file.file as fl
import re
import os
from glob import glob

dirname, filename = os.path.split(os.path.abspath(__file__))
dirname = dirname.split( 'pipe' )[0]
IMAGEMAGICPATH = dirname + 'bin/ImageMagick/'

class sequenceFile(fl.File):
	"""main class to handle sequences of files"""
	def __init__(self, path):
		"""init sequence path, base path"""
		self.as_super = super(sequenceFile, self)
		self.as_super.__init__( str( path ).replace( '\\', '/' ) )

	@property
	def seqPath(self):
		"""return the path of the sequence"""
		return '%s.%%%sd%s' % ( self.dirPath + self.name, str(self.padding).zfill(2), self.files[0].extension )

	@property
	def start(self):
		"""return start Frame"""
		fil = self.files[0]
		firstString = re.findall( r'\d+', fil.path )[-1]
		return int( firstString )

	@property
	def end(self):
		"""return end Frame"""
		return int( re.findall( r'\d+', self.files[-1].path )[-1] )

	@property
	def frames(self):
		"""return the amount of frames of the sequences"""
		return self.end - self.start

	@property
	def zeroFiles(self):
		"""return the files in the sequence that has a zero size"""
		zeroFils = []
		for a in self.files:
			if a.isZero:
				zeroFils.append( a )
		return zeroFils

	@property
	def missingFiles(self):
		"""return what frames are missing in the frame range"""
		missingFils = []
		for a in range( self.start, self.end ):
			a = tfl.textureFile( self.dirPath + self.name + '.' + str(a).zfill(self.padding) + '.' + self.extension )
			if not a.exists:
				missingFils.append( a )
		return missingFils

	@property
	def padding(self):
		"""return the padding of this sequence"""
		firstString = re.findall( r'\d+', self.files[0].path )[-1]
		# GET THE PADDING FROM THE AMOUNT OF DIGITS
		return len( firstString )

	@property
	def files(self):
		"""return all the files in the sequence"""
		pa = os.path.join( self.dirPath, '%s.*%s' % ( self.name, self.extension ) )
		fils = sorted(glob( pa ))
		return [ tfl.textureFile( a ) for a in fils ]

	def copy(self, newPath ):
		"""copy all the files"""
		for f in self.files:
			f.copy( newPath )
		return sequenceFile( newPath + '/'  + self.basename )

	def insertFrameNumber( self, outdir = '', offset = 0 ):
		"""docstring for insertFrameNumber"""
		if not outdir == '':
			if not os.path.exists( outdir ):
				os.makedirs( outdir )
		for i,fi in enumerate( self.files ):
			if outdir == '':
				outdir = fi.path
			cmd = fi.path + " -scene " + str( i + offset ) + ' -gravity SouthEast -undercolor #00000080 -fill white -font Verdana -pointsize 24 -annotate 0 "%[scene]" ' + outdir + '/' + fi.fullName
			os.popen(  IMAGEMAGICPATH + 'convert.exe ' + cmd  )

