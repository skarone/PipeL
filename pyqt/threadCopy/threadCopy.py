import os
import general.ui.pySideHelper as uiH
reload( uiH )
uiH.set_qt_bindings()
from Qt import QtGui,QtCore

PYFILEDIR = os.path.dirname( os.path.abspath( __file__ ) )

uifile = PYFILEDIR + '/progressBar.ui'
fom, base = uiH.loadUiType( uifile )

class ProgressDialog(QtGui.QProgressDialog):

	def __init__(self, source, destination, parent = None):
		QtGui.QProgressDialog.__init__(self, uiH.getMayaWindow())
		self.parent = parent
		self.source = source
		self.destination = destination

		self.setLabelText("Copying: %s" % (self.source))

		self.setMinimum(0)
		self.setMaximum(100)
		self.setValue(0)

		self.show()
		self.copy()

	def copy(self):

		copy_thread = CopyThread(self, self.source, self.destination)
		copy_thread.procPartDone.connect(self.update_progress)
		copy_thread.procDone.connect(self.finished_copy)
		copy_thread.start()

	def update_progress(self, progress):
		self.setValue(progress)

	def finished_copy(self, state):
		self.close()

class CopyThread(QtCore.QThread):

	procDone = QtCore.Signal(bool)
	procPartDone = QtCore.Signal(int)

	def __init__(self, parent, source, destination ):
		QtCore.QThread.__init__(self, parent)
		self.source = source
		self.destination = destination

	def run(self):
		self.copy()
		self.procDone.emit(True)

	def copy(self):
		source_size = os.stat(self.source).st_size
		copied = 0
		source = open(self.source, "rb")
		target = open(self.destination, "wb")

		while True:
			chunk = source.read(1024)
			if not chunk:
				break
			target.write(chunk)
			copied += len(chunk)
			self.procPartDone.emit(copied * 100 / source_size)

		source.close()
		target.close()

class MultiProgressDialog(base, fom):

	def __init__(self, sources, basePath, finalPath, parent):
		if uiH.USEPYQT:
			super(base, self).__init__(parent)
		else:
			super(MultiProgressDialog, self).__init__(parent)
		self.setupUi(self)
		
		self.parent = parent
		self.sources = source
		self.basePath = basePath
		self.finalPath = finalPath

		self.copy()

	def copy(self):
		copy_thread = MultiCopyThread(self, self.parent, self.sources, self.basePath, self.finalPath )
		copy_thread.procPartDone.connect(self.update_progressFile)
		copy_thread.procFileDone.connect(self.update_progressFiles)
		copy_thread.procDone.connect(self.finished_copy)
		copy_thread.start()

	def update_progressFile(self, progress):
		self.file_pb.setValue(progress)

	def update_progressFiles(self, progress):
		self.files_pb.setValue(progress)

	def finished_copy(self, state):
		self.close()

class MultiCopyThread(QtCore.QThread):

	procDone = QtCore.Signal(bool)
	procPartDone = QtCore.Signal(int)
	procFileDone = QtCore.Signal(int)

	def __init__(self, parent, sources, basePath, finalPath ):
		QtCore.QThread.__init__(self, parent)
		self.sources = sources
		self.basePath = basePath
		self.finalPath = finalPath

	def run(self):
		self.copy()
		self.procDone.emit(True)

	def copy(self):
		lenSources = len(self.sources)
		count = 0
		for s in self.sources:
			if not os.path.exists(  os.path.dirname( s.replace( self.basePath, self.finalPath ) ) ):
				os.makedirs( os.path.dirname( s.replace( self.basePath, self.finalPath ) ) )
			source_size = os.stat(s).st_size
			copied = 0
			source = open(s, "rb")
			target = open(s.replace( self.basePath, self.finalPath ), "wb")

			while True:
				chunk = source.read(1024)
				if not chunk:
					break
				target.write(chunk)
				copied += len(chunk)
				self.procPartDone.emit(copied * 100 / source_size)

			source.close()
			target.close()
			self.procFileDone.emit(count * 100 / lenSources)
			count += 1




