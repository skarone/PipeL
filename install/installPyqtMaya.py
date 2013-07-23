import shutil
import os
import distutils

def movePyqtForMayaToMayaFolder():
	PYFILEDIR = os.path.dirname( os.path.abspath( __file__ ) )
	distutils.dir_util.copy_tree( PYFILEDIR + '/libs/pyqt_4.9_qt_maya/PyQt4', 'C:/Program Files/Autodesk/Maya2013/Python/Lib/site-packages/PyQt4'  )
	shutil.copy( PYFILEDIR + '/libs/pyqt_4.9_qt_maya/sip.pyd', 'C:/Program Files/Autodesk/Maya2013/Python/Lib/site-packages/sip.pyd' )

movePyqtForMayaToMayaFolder()
