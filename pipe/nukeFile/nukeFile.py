import os
import nuke
import nukescripts
import pipe.file.file as fl

class nukeFile(fl.File):
	"""docstring for nukeFile"""
	def __init__(self, path):
		super(nukeFile, self).__init__(path)
		
	def save(self):
		"""docstring for save"""
		nuke.scriptSaveAs( self.path )

	def open(self):
		"""docstring for open"""
		nukescripts.utils.executeInMainThread(nuke.scriptOpen,(self.path,))
		#nuke.scriptOpen( self.path )
