import pipe.file.file as fl
import os

def getZeroFilesInFolder( path = '' ):
	"""return all the files that has zero zise in folders and subfolders"""
	return [ os.path.join(dp, f) for dp, dn, fn in os.walk(os.path.expanduser(path)) for f in fn if fl.File( os.path.join(dp, f) ).size == 0 ]


