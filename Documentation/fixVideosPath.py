import pipe.file.file as fl
import re
from functools import partial

def main():
	fils = fl.filesInDir( 'D:/PipeL/docs' , True )
	for f in fils:
		if not f.extension == '.htm':
			continue
		#search for video in file
		data = f.data
		expr = '(?:")(?P<Path>.+)(?:\.mp4")'
		file_str = re.sub( expr, partial( _replaceTexture, './Videos/' ), f.data )
		f.write( file_str )

def _replaceTexture( newDir, matchobj ):
	"""docstring for _replaceTexture"""
	path = matchobj.group( "Path" )
	fileName = path.split( '/' )[-1]
	print fileName
	return matchobj.group(0).replace(path, newDir + fileName )


if __name__ == '__main__':
	main()
