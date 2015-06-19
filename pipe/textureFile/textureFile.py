
import pipe.file.file as fl
reload( fl )
try:
	import maya.cmds as mc
except:
	pass
import os
import pipe.settings.settings as sti
reload( sti )


#TODO... hasUdim Property


"""
import general.mayaNode.mayaNode as mn
import pipe.textureFile.textureFile as tfl
reload(tfl)
#all textures to tx
for n in mn.ls( typ = ['file', 'aiImage' ] ):
    if n.type == 'aiImage':
        attr = "filename"
    else:
        attr = "ftn"
    f = tfl.textureFile( n.attr( attr ).v )
    if f.hasTx:
        toTx = f.toTx()
        n.attr( attr ).v = toTx.path

#import pipe.project.project as prj
def projectToTx( proj = 'DogMendoncaAndPizzaBoy' ):
	proj = prj.Project( proj )
	for a in proj.assets:
		for t in a.textures:
			t.makeTx()
"""

dirname, filename = os.path.split(os.path.abspath(__file__))
dirname = dirname.split( 'pipe' )[0]
IMAGEMAGICPATH = dirname + 'bin/ImageMagick/'


class textureFile(fl.File):
	"""docstring for textureFile"""
	def __init__(self, path):
		self.as_super = super(textureFile, self)
		self.as_super.__init__( path )
	
	@property
	def hasUdim(self):
		"""check if the path has udim, so we can treat the texture has a group of textures"""
		return '<udim>' in self.path.lower()

	@property
	def udimPaths(self):
		"""return the textures that correspond to the udim path"""
		try:
			return [ textureFile( self.dirPath + a ) for a in os.listdir( self.dirPath ) if self.name + '.' in a ]
		except:
			return []
		
	@property
	def hasTx(self):
		"""return if there is a tx version"""
		if self.isTx:
			return True
		return textureFile( self.path.replace( self.extension, '.tx' ) ).exists

	@property
	def hasPng(self):
		"""return if there is a png version"""
		if self.isPng:
			return True
		return textureFile( self.path.replace( self.extension, '.png' ) ).exists

	@property
	def name(self):
		"""return the name of the texture"""
		nam = super( textureFile, self ).name
		if self.hasUdim:
			try:
				return nam[:nam.rindex( '.' )]
			except:
				return nam
		return nam

	@property
	def exists(self):
		"""override exists to support udim"""
		if self.hasUdim:
			return len( self.udimPaths ) != 0
		return super( textureFile, self ).exists

	def copy(self, newPath):
		"""override copy to support udim"""
		if self.hasUdim:
			for a in self.udimPaths:
				fi = a.copy( newPath )
			return fi
		else:
			return textureFile( super( textureFile, self ).copy( newPath ).path )

	def delete(self):
		"""override delete to support udim"""
		if self.hasUdim:
			for a in self.udimPaths:
				a.delete()
		else:
			super( textureFile, self ).delete()

	def move(self, newPath):
		"""override move to support udim"""
		if self.hasUdim:
			for a in self.udimPaths:
				a.move(newPath)
		else:
			super( textureFile, self ).move( newPath )

	@property
	def hasLow(self):
		"""return if the texture has low version"""
		return self.toLow().exists

	@property
	def hasMid(self):
		"""return if the texture has mid version"""
		return self.toMid().exists

	@property
	def hasHigh(self):
		"""return if the texture has high version"""
		return self.toHigh().exists
		
	@property
	def isTx(self):
		"""return true if the extension is tx"""
		return self.extension == '.tx'

	@property
	def resolution(self):
		"""return the resolution of the texture HIGH MID LOW"""
		if self.name.endswith( '_LOW' ):
			return 'LOW'
		elif self.name.endswith( '_MID' ):
			return 'MID'
		else:
			return 'HIGH'

	@property
	def isPng(self):
		"""
		return if the texture is in png
		"""
		return self.extension == '.png'

	@property
	def isHigh(self):
		"""return if the texture is in High"""
		return self.resolution == 'HIGH'

	@property
	def isMid(self):
		"""return if the texture is in Mid"""
		return self.resolution == 'MID'

	@property
	def isLow(self):
		"""return if the texture is in Low"""
		return self.resolution == 'LOW'

	def toLow(self):
		"""return low version textureFile"""
		if self.isLow:
			return self
		if self.isHigh:
			return textureFile( self.dirPath + self.name + '_LOW' + self.extension )
		elif self.isMid:
			return textureFile( self.path.replace( '_MID',  '_LOW' ) )

	def toMid(self):
		"""return mid version textureFile"""
		if self.isMid:
			return self
		if self.isHigh:
			return textureFile( self.dirPath + self.name + '_MID' + self.extension )
		elif self.isLow:
			return textureFile( self.path.replace( '_LOW',  '_MID' ) )

	def toHigh(self):
		"""return high version textureFile"""
		if self.isHigh:
			return self
		if self.isMid:
			return textureFile( self.path.replace( '_MID', '' ))
		if self.isLow:
			return textureFile( self.path.replace( '_LOW', '' ))

	def toTx(self):
		"""return tx version of textureFile"""
		if self.isTx:
			return self
		else:
			return textureFile( self.path.replace( self.extension, '.tx' ) )

	def toPng(self):
		"""
		return png version of textureFile
		"""
		if self.isPng:
			return self
		else:
			return textureFile( self.path.replace( self.extension, '.png' ) )

	@property
	def width(self):
		"""return the width of the texture"""
		pass

	@property
	def height(self):
		"""return the height of the texture"""
		pass

	def makeTx(self, force = False ):
		"""make Tx version of the texture"""
		if not self.exists:
			return False
		if self.isTx:
			return False
		if self.hasUdim:
			for a in self.udimPaths:
				a._makeTx()
		else:
			self._makeTx()

	def _makeTx(self, force = False):
		"""docstring for _makeTx"""
		if self.hasTx:
			if not self.toTx().isOlderThan( self ) and not force:
				return False
		print 'Converting >> ' + self.path + ' to TX!'
		MAKETXPATH     = 'C:/solidangle/mtoadeploy/2014/bin/maketx.exe'
		settings = sti.Settings()
		gen = settings.General
		maketxpath = gen[ "maketxpath" ]
		if maketxpath:
			MAKETXPATH = maketxpath
		finalCMD =  MAKETXPATH + ' "' + self.path + '"'
		os.popen( finalCMD ) 

	def makeMid(self, force = False):
		"""make Mid version of texture"""
		mid = self.reSize( 50, self.name + '_MID', force )
		return mid

	def makeLow(self, force = False):
		"""make Low version of texture"""
		low = self.reSize( 25, self.name + '_LOW', force )
		return low

	def reSize(self, percent = 50, newName = '', force = False):
		"""resize the texture to a specific percent"""
		newFile = textureFile( self.dirPath + newName + self.extension )
		cmd = '"' + self.path + '"  -resize ' + str( percent ) + '%  "' + newFile.path + '"'
		if force or not newFile.exists:
			os.popen(  IMAGEMAGICPATH + 'convert.exe ' + cmd  )
		return newFile

	def createVersions(self, force = False):
		"""create all the version for the file, LOW, MID and tx"""
		low = self.makeLow(force)
		low.makeTx(force)
		mid = self.makeMid(force)
		mid.makeTx(force)
		self.makeTx(force)
