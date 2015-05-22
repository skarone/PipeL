import general.mayaNode.mayaNode as mn
import pipe.textureFile.textureFile as tfl
import pipe.settings.settings as sti
reload( sti )


class Manager(object):
	"""
	manage textures in current scene
	"""
	def __init__(self):
		pass

	@property
	def textures(self):
		"""
		return the textures in the scene
		"""
		fils = mn.ls( typ = 'file' )
		aiImage = mn.ls( typ = 'aiImage' )
		if aiImage:
			fils.extend( aiImage )
		return fils

	def toTx(self, textures, autoCreate = True):
		"""
		convert and change path to toTx
		"""
		for n in textures:
			if n.type == 'aiImage':
				attr = "filename"
			else:
				attr = "ftn"
			f = tfl.textureFile( n.attr( attr ).v )
			if not f.exists:
				continue
			if not f.hasTx:
				f.makeTx( True )
			toTx = f.toTx()
			n.attr( attr ).v = toTx.path

	def createTx(self, textures):
		"""create tx version"""
		for n in textures:
			if n.type == 'aiImage':
				attr = "filename"
			else:
				attr = "ftn"
			f = tfl.textureFile( n.attr( attr ).v )
			if not f.exists:
				continue
			f.makeTx( True )

	def allToTx(self):
		"""
		convert all the textures to Tx
		"""
		self.toTx( self.textures )

	def toPng(self, textures ):
		"""
		convert and change path to toPng
		"""
		for n in textures:
			if n.type == 'aiImage':
				attr = "filename"
			else:
				attr = "ftn"
			f = tfl.textureFile( n.attr( attr ).v )
			if f.hasPng:
				toPng = f.toPng()
				n.attr( attr ).v = toPng.path

	def allToPng(self):
		"""
		convert all the textures to Png
		"""
		self.toPng( self.textures )

	def moveToFolder(self, textures, folderPath):
		"""
		Move the textures to a folder
		"""
		for n in textures:
			if n.type == 'aiImage':
				attr = "filename"
			else:
				attr = "ftn"
			f = tfl.textureFile( n.attr( attr ).v )
			newFile = tfl.textureFile( folderPath + '/' + f.fullName )
			if f.exists:
				newFile = f.copy( folderPath )
			n.attr( attr ).v = newFile.path

	def replacePath(self, textures, searchAndReplace = ['','']):
		"""
		change the path of the texture, search and replace are optional
		"""
		for n in textures:
			if n.type == 'aiImage':
				attr = "filename"
			else:
				attr = "ftn"
			n.attr( attr ).v = n.attr( attr ).v.replace( searchAndReplace[0], searchAndReplace[1] )

	def renameTexture(self, texture, newName):
		"""docstring for renameTextures"""
		if texture.type == 'aiImage':
			attr = "filename"
		else:
			attr = "ftn"
		f = tfl.textureFile( texture.attr( attr ).v )
		f.rename( newName + f.extension )
		texture.attr( attr ).v = f.path
		if f.hasTx():
			txVer = f.toTx()
			txVer.rename( newName + txVer.extension )

	def createVersions(self, textures):
		"""docstring for createVersions"""
		for n in textures:
			if n.type == 'aiImage':
				attr = "filename"
			else:
				attr = "ftn"
			f = tfl.textureFile( n.attr( attr ).v )
			f.createVersions()

	def toLow(self, textures):
		"""docstring for toLow"""
		for n in textures:
			if n.type == 'aiImage':
				attr = "filename"
			else:
				attr = "ftn"
			f = tfl.textureFile( n.attr( attr ).v )
			if not f.hasLow:
				low = f.makeLow()
				low.makeTx()
			toPng = f.toLow()
			n.attr( attr ).v = toPng.path

	def toHigh(self, textures):
		"""docstring for toHigh"""
		for n in textures:
			if n.type == 'aiImage':
				attr = "filename"
			else:
				attr = "ftn"
			f = tfl.textureFile( n.attr( attr ).v )
			if f.hasHigh:
				toPng = f.toHigh()
				n.attr( attr ).v = toPng.path

	def toMid(self, textures):
		"""docstring for toMid"""
		for n in textures:
			if n.type == 'aiImage':
				attr = "filename"
			else:
				attr = "ftn"
			f = tfl.textureFile( n.attr( attr ).v )
			if not f.hasMid:
				mid = f.makeMid()
				mid.makeTx()
			toPng = f.toMid()
			n.attr( attr ).v = toPng.path

	def texturesNotInServerPath(self):
		"""return all the textures that are not pointing to serverPath"""
		serverPath = sti.Settings().General[ "serverpath" ]
		texturesNotInServer = []
		for n in self.textures:
			if n.type == 'aiImage':
				attr = "filename"
			else:
				attr = "ftn"
			if not n.attr( attr ).v.startswith( serverPath ):
				texturesNotInServer.append( n )
		return texturesNotInServer
