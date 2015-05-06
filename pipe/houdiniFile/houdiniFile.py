import pipe.file.file            as fl
reload( fl )
import hou

def currentFile():
	"""docstring for currentFile"""
	return houdiniFile( hou.hipFile.path() )

class houdiniFile(fl.File):
	def __init__(self, path):
		super(houdiniFile, self).__init__( path )

	def save(self):
		"""save current file"""
		hou.hipFile.save( self.path )

	def newVersion(self):
		"""create a new Version File"""
		if self.exists:
			super(houdiniFile, self).newVersion()

	def open(self):
		"""open scene"""
		hou.hipFile.load( self.path )
