import os
import pyregistry as rg
from PySide import QtGui,QtCore
import xml.etree.ElementTree as xml
from xml.etree.ElementTree import parse, SubElement
import general.ui.pysideuic as pysideuic
from cStringIO import StringIO

import client
import shutil

PYFILEDIR = os.path.dirname( os.path.abspath( __file__ ) )

uifile = QtCore.QFile("ui/install.ui")

def loadUiType(uiFile):
	parsed = xml.parse(uiFile)
	widget_class = parsed.find('widget').get('class')
	form_class = parsed.find('class').text

	with open(uiFile, 'r') as f:
		o = StringIO()
		frame = {}

		pysideuic.compileUi(f, o, indent=0)
		pyc = compile(o.getvalue(), '<string>', 'exec')
		exec pyc in frame

		#Fetch the base_class and form class based on their type in the xml from designer
		form_class = frame['Ui_%s'%form_class]
		base_class = eval('QtGui.%s'%widget_class)
	return form_class, base_class

fom, base = loadUiType( uifile.fileName() )

class InstallerUI(base, fom):
	"""docstring for ProjectCreator"""
	procStart = QtCore.Signal(str)
	def __init__(self, parent  = None ):
		super(InstallerUI, self).__init__(parent)
		self.setWindowFlags(QtCore.Qt.FramelessWindowHint)
		self.setupUi(self)
		self._makeConnections()

	def _makeConnections(self):
		"""docstring for _makeConnections"""
		self.connect( self.serverSet_btn    , QtCore.SIGNAL("clicked()") , self.fillServerPath )
		self.connect( self.serverInstall_btn, QtCore.SIGNAL("clicked()") , self.serverInstall )
		self.connect( self.clientInstall_btn, QtCore.SIGNAL("clicked()") , self.clientInstall )
		self.connect( self.close_btn, QtCore.SIGNAL("clicked()") , self.close )

	@QtCore.Slot()
	def close(self):
		"""docstring for close"""
		self.procStart.emit( 'Close' )
		super(InstallerUI,self).close()

	@property
	def serverPath(self):
		"""return serverPath"""
		return str( self.server_le.text() )

	@property
	def serial(self):
		"""return serial from ui"""
		return str( self.serial_le.text() )

	@QtCore.Slot()
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

	@QtCore.Slot()
	def clientInstall(self):
		"""add userSetup in maya 2014/2015, add menu in nuke, set PYTHONPATH environment variable to serverPath"""
		if not self.serverPath or self.serverPath == 'Please Fill ME!':
			self.server_le.setText( 'Please Fill ME!' )
			return
		"""
		if not self.serial or self.serial == 'Please Fill ME!':
			self.serial_le.setText( 'Please Fill ME!' )
			return
		#check with server is serial is OK
		newData = client.sendClientInfo( self.serial )
		if not newData:
			self.message_lbl.setText( 'Check Internet Connection!' )
			return
		if newData == 'wrong-serial':
			self.message_lbl.setText( 'Wrong SERIAL!' )
			return
		if newData == 'installations-reached':
			self.message_lbl.setText( 'Number of Installations reached!' )
			return
		"""
		versions = ['2014', '2015', '2016']
		for v in versions:
			res  = self.setupMaya( v )
		resNuk = self.setupNuke()
		self.message_lbl.setText( 'Installation Complete :)!' )
		#ADD REGISTER
		#rg.set_reg( 'HKCU', r'Software\Pipel', 'key', newData )
		#SET PYTHONPATH
		path = self.serverPath.replace( '\\', '/' ) + ';'
		pyPath = ''
		try:
			pyPath = rg.queryValue('HKLM', r'SYSTEM\CurrentControlSet\Control\Session Manager\Environment', 'PYTHONPATH')
		except:
			pass
		if not self.serverPath in pyPath:
			#ALLREADY INSTALLED
			rg.set_reg( 'HKLM', r'SYSTEM\CurrentControlSet\Control\Session Manager\Environment', 'PYTHONPATH', path + pyPath )
		self.procStart.emit( 'Installed' )
	
	def setupMaya(self, version = '2014'):
		"""create userSetup.mel or if exists check if there is pipel installed if not add lines to it"""
		userDir      = os.path.expanduser( '~' )
		sufix = '-x64'
		if version == '2016':
			sufix = ''
		mayaPath = userDir + '\\Documents\\maya\\' + version + sufix + '\\scripts'
		if os.path.exists( mayaPath ): #is maya installed
			setupFile = mayaPath + '\\userSetup.mel'
			if os.path.exists( setupFile ):#SETUP FILE EXISTS.. WE NEED TO CHECK IF PIPEL IS INSTALLED
				with open( setupFile, 'r' ) as fil:
					data = fil.read()
				if not 'install.pipelMenu' in data:
					with open( setupFile, 'w' ) as fil:
							data += '\npython( "import install.pipelMenu;print \'Pipel Loaded\'" );'
							fil.write( data )
			else:
				with open( setupFile, 'w' ) as fil:
					data = 'python( "import install.pipelMenu;print \'Pipel Loaded\'" );'
					fil.write( data )
			#install pipel plugins
			modPath =  PYFILEDIR + '/modules/PipeL' + version + '.mod'
			if os.path.exists( modPath ):
				if not os.path.exists( mayaPath.replace( 'scripts', 'modules' ) ):
					os.makedirs( mayaPath.replace( 'scripts', 'modules' ) )
				shutil.copy2( modPath, mayaPath.replace( 'scripts', 'modules' ) + '/PipeL' + version + '.mod'  )
			return True
		return False

	def setupNuke(self):
		"""add PipeL menu if not installed"""
		userDir      = os.path.expanduser( '~' )
		nukePath     = userDir + '\\.nuke'
		if os.path.exists( nukePath ): #is nuke installed 
			menuFile = nukePath + '\\menu.py'
			if os.path.exists( menuFile ):#SETUP FILE EXISTS.. WE NEED TO CHECK IF PIPEL IS INSTALLED
				with open( menuFile, 'r+' ) as fil:
					data = fil.read()
					if 'install.pipelNukeMenu' in data:
						#PIPEL is installed
						return True
					data += 'import install.pipelNukeMenu'
					fil.write( data )
			else:
				with open( menuFile, 'w' ) as fil:
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
