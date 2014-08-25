import compileall
import pipe.file.file as fl

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

