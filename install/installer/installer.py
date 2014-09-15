import os
from PyQt4 import QtGui,QtCore, uic
import pyregistry as rg
from xml.etree.ElementTree import parse, SubElement

PYFILEDIR = os.path.dirname( os.path.abspath( __file__ ) )

uifile = QtCore.QFile("ui/install.ui")
print 'asd',uifile.fileName(), uifile.exists()
fom, base = uic.loadUiType( uifile.fileName() )

class InstallerUI(base, fom):
	"""docstring for ProjectCreator"""
	procStart = QtCore.pyqtSignal(str)
	def __init__(self, parent  = None ):
		super(base, self).__init__(parent)
		self.setWindowFlags(QtCore.Qt.FramelessWindowHint)
		self.setupUi(self)
		self._makeConnections()

	def _makeConnections(self):
		"""docstring for _makeConnections"""
		self.connect( self.serverSet_btn    , QtCore.SIGNAL("clicked()") , self.fillServerPath )
		self.connect( self.serverInstall_btn, QtCore.SIGNAL("clicked()") , self.serverInstall )
		self.connect( self.clientInstall_btn, QtCore.SIGNAL("clicked()") , self.clientInstall )
		self.connect( self.close_btn, QtCore.SIGNAL("clicked()") , self.close )

	@QtCore.pyqtSlot()
	def close(self):
		"""docstring for close"""
		self.procStart.emit( 'Close' )

	@property
	def serverPath(self):
		"""return serverPath"""
		return str( self.server_le.text() )

	@QtCore.pyqtSlot()
	def serverInstall(self):
		"""copy PipeL files to serverPath and try to do client Install in this machine"""
		if not self.serverPath or self.serverPath == 'Please Fill ME!':
			self.server_le.setText( 'Please Fill ME!' )
			return
		copyanything( PYFILEDIR + '/dist', self.serverPath + '/PipeL' )
		self.procStart.emit( 'Installed' )
		"""
		msg = QtGui.QMessageBox( self )
		msg.setText( 'PipeL Installed' )
		msg.setWindowTitle( 'PipeL installation' )
		msg.open()
		"""

	@QtCore.pyqtSlot()
	def clientInstall(self):
		"""add userSetup in maya 2014/2015, add menu in nuke, set PYTHONPATH environment variable to serverPath"""
		if not self.serverPath or self.serverPath == 'Please Fill ME!':
			self.server_le.setText( 'Please Fill ME!' )
			return
		res14  = self.setupMaya( '2014' )
		res15  = self.setupMaya( '2015' )
		resNuk = self.setupNuke()
		if res14 or res15 or resNuk: 
			#ADD REGISTER
			rg.set_reg( 'HKCU', r'Software\Pipel', 'key', '1561532593' )
			#SET PYTHONPATH
			path = self.serverPath + ';'
			pyPath = ''
			try:
				pyPath = pr.queryValue('HKLM', r'SYSTEM\CurrentControlSet\Control\Session Manager\Environment', 'PYTHONPATH')
			except:
				pass
			if self.serverPath in pyPath:
				#ALLREADY INSTALLED
				return
			rg.set_reg( 'HKLM', r'SYSTEM\CurrentControlSet\Control\Session Manager\Environment', 'PYTHONPATH', path + pyPath )
			self.procStart.emit( 'Installed' )
			
	
	def setupMaya(self, version = '2014'):
		"""create userSetup.mel or if exists check if there is pipel installed if not add lines to it"""
		userDir      = os.path.expanduser( '~' )
		mayaPath = userDir + '\\Documents\\maya\\' + version + '-x64\\scripts'
		if os.path.exists( mayaPath ): #is maya installed
			setupFile = mayaPath + '\\userSetup.mel'
			if os.path.exists( setupFile ):#SETUP FILE EXISTS.. WE NEED TO CHECK IF PIPEL IS INSTALLED
				with open( setupFile, 'r+' ) as fil:
					data = fil.read()
					if 'install.pipelMenu' in data:
						#PIPEL is installed
						return
					data += '\npython( "import install.pipelMenu;print \'Pipel Loaded\'" );'
					fil.write( data )
			else:
				with open( setupFile, 'w' ) as fil:
					data = 'python( "import install.pipelMenu;print \'Pipel Loaded\'" );'
					fil.write( data )
			return True
		return False

	def setupNuke(self):
		"""add PipeL menu if not installed"""
		userDir      = os.path.expanduser( '~' )
		nukePath     = userDir + '\\.nuke'
		if os.path.exists( nukePath ): #is nuke installed 
			menuFile = nukePath + '\\menu.py'
			if os.path.exists( menuFile ):#SETUP FILE EXISTS.. WE NEED TO CHECK IF PIPEL IS INSTALLED
				with open( setupFile, 'r+' ) as fil:
					data = fil.read()
					if 'install.pipelNukeMenu' in data:
						#PIPEL is installed
						return
					data += 'import install.pipelNukeMenu'
					fil.write( data )
			else:
				with open( setupFile, 'w' ) as fil:
					data = 'import install.pipelNukeMenu'
					fil.write( data )
			return True
		return False

	def fillServerPath(self):
		"""docstring for fillServerPath"""
		fil = str(QtGui.QFileDialog.getExistingDirectory(self, "Select Directory"))
		if fil:
			self.server_le.setText( fil )

import shutil

def copyanything(src, dst):
	for src_dir, dirs, files in os.walk(src):
		dst_dir = src_dir.replace(src, dst)
		if not os.path.exists(dst_dir):
			os.mkdir(dst_dir)
		for file_ in files:
			src_file = os.path.join(src_dir, file_)
			dst_file = os.path.join(dst_dir, file_)
			if os.path.exists(dst_file):
				os.remove(dst_file)
			shutil.copy(src_file, dst_dir)


if __name__=="__main__":
	import sys
	a = QtGui.QApplication(sys.argv)
	global PyForm
	PyForm=InstallerUI()
	PyForm.show()
	sys.exit(a.exec_())
