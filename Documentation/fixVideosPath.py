import re
from functools import partial

import pipe.file.file as fl


def main():
	fils = fl.filesInDir( 'D:/PipeL/docs' , True )
	for f in fils:
		if not f.extension == '.htm':
			continue
		#search for video in file
		data = f.data
		expr = '(?:")(?P<Path>.+)(?:\.mp4")'
		file_str = re.sub( expr, partial( _replacePath, './Videos/' ), f.data )
		f.write( file_str )

def _replacePath( newDir, matchobj ):
	"""docstring for _replaceTexture"""
	path = matchobj.group( "Path" )
	fileName = path.split( '/' )[-1]
	print fileName
	return matchobj.group(0).replace(path, newDir + fileName )


if __name__ == '__main__':
	main()
