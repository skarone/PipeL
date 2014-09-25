import pipe.textureFile.textureFile as tfl

class sequenceFile(tfl.textureFile):
	"""main class to handle sequences of files"""
	def __init__(self, path):
		"""init sequence path, base path"""
		super( sequenceFile ).__init__( path )

	@property
	def path(self):
		"""return the path of the sequence"""
		return self.getFileSeq()[0]

	@property
	def start(self):
		"""return start Frame"""
		firstString = re.findall( r'\d+', self.files[0] )[-1]
		return int( firstString )

	@property
	def end(self):
		"""return end Frame"""
		return int( re.findall( r'\d+', self.files[-1] )[-1] )

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
		firstString = re.findall( r'\d+', self.files[0] )[-1]
		# GET THE PADDING FROM THE AMOUNT OF DIGITS
		return len( firstString )

	@property
	def files(self):
		"""return all the files in the sequence"""
		return [ tfl.textureFile( a ) for a in sorted(glob( os.path.join( self.dirPath, '%s.*.%s' % ( self.name, self.extension ) ) ))]

	@property
	def seqPath():
		'''Return file sequence. Very loose example!!'''
		fileName = '%s.%%%sd%s' % ( self.name, str(self.padding).zfill(2), self.files[0].extension )
		# RETURN FULL PATH AS SEQUENCE NOTATION
		return os.path.join( self.dirPath, fileName )
