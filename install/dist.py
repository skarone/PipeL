import compileall
import pipe.file.file as fl
from time import sleep
import sys

def createDistVersion():
	basePath = 'D:/PipeL'
	compileall.compile_dir( basePath, force=True)
	fils = fl.filesInDir( 'D:/PipeL' )
	finalPath = 'D:/PipeL/dist'
	extensionToIgnore = [ '.py' ]
	foldersToSkip = [ '.git' ]
	for f in fils:
		if any( f.extension == n for n in extensionToIgnore ):
			continue
		if any( n in f.path for n in foldersToSkip ):
			continue
		f.copy( f.path.replace( basePath, finalPath ) )

def compileAndMove( path, newDir = 'Y:/PipeL', basePath = 'D:/PipeL' ):
	ret = compileall.compile_file( path, force=True )
	if ret:
		newFil = fl.File( path.replace( '\\','/' ) + 'c' )
		newFil.move( newFil.path.replace( basePath, newDir ) )

if __name__=='__main__':
	print sys.argv[1]
	compileAndMove( sys.argv[1] )
	sleep( 10 )
