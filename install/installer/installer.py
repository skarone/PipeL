import os
from PyQt4 import QtGui,QtCore, uic


PYFILEDIR = os.path.dirname( os.path.abspath( __file__ ) )

uifile = PYFILEDIR + '/install.ui'
fom, base = uic.loadUiType( uifile )

class InstallerUI(base, fom):
	"""docstring for ProjectCreator"""
	def __init__(self, parent  = None, *args ):
		super(base, self).__init__(parent)
		self.setWindowFlags(QtCore.Qt.FramelessWindowHint)
		self.setupUi(self)
		self._makeConnections()

	def _makeConnections(self):
		"""docstring for _makeConnections"""
		self.connect( self.serverSet_btn    , QtCore.SIGNAL("clicked()") , self.fillServerPath )
		self.connect( self.serverInstall_btn, QtCore.SIGNAL("clicked()") , self.serverInstall )
		self.connect( self.clientInstall_btn, QtCore.SIGNAL("clicked()") , self.clientInstall )

	@property
	def serverPath(self):
		"""return serverPath"""
		return str( self.server_le.text() )

	def serverInstall(self):
		"""copy PipeL files to serverPath and try to do client Install in this machine"""
		if not self.serverPath or self.serverPath == 'Please Fill ME!':
			self.server_le.setText( 'Please Fill ME!' )
			return
		print 'installing server'
		copyanything( PYFILEDIR + '/dist', self.serverPath + '/PipeL' )
		msg = QtGui.QMessageBox( self )
		msg.setText( 'PipeL Installed' )
		msg.setWindowTitle( 'PipeL installation' )
		msg.open()
		

	def clientInstall(self):
		"""add userSetup in maya 2014/2015, add menu in nuke, set PYTHONPATH environment variable to serverPath"""
		if not self.serverPath or self.serverPath == 'Please Fill ME!':
			self.server_le.setText( 'Please Fill ME!' )
			return
		print 'installing client'

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
