from PySide import QtGui, QtCore
from PySide.phonon import Phonon

class Window(QtGui.QWidget):
	def __init__(self, parent = None):
		QtGui.QWidget.__init__(self, parent)
		self.media = Phonon.MediaObject(self)
		self.media.stateChanged.connect(self.handleStateChanged)
		self.video = Phonon.VideoWidget(self)
		self.video.setMinimumSize(400, 400)
		self.audio = Phonon.AudioOutput(Phonon.VideoCategory, self)
		Phonon.createPath(self.media, self.audio)
		Phonon.createPath(self.media, self.video)
		self.button = QtGui.QPushButton('Choose File', self)
		self.buttonPlay = QtGui.QPushButton('Play', self)
		self.buttonPlay.clicked.connect(self.play)
		self.button.clicked.connect(self.handleButton)
		self.list = QtGui.QListWidget(self)
		self.list.addItems(Phonon.BackendCapabilities.availableMimeTypes())
		layout = QtGui.QVBoxLayout(self)
		layout.addWidget(self.video, 1)
		layout.addWidget(self.button)
		layout.addWidget(self.buttonPlay)
		layout.addWidget(self.list)

	def handleButton(self):
		if self.media.state() == Phonon.PlayingState:
			self.media.stop()
		else:
			path = QtGui.QFileDialog.getOpenFileName(self, self.button.text())
			if path:
				path = path[0]
				print path
				self.media.setCurrentSource(Phonon.MediaSource(path))
				self.media.play()

	def play(self):
		"""docstring for play"""
		self.media.play()

	def handleStateChanged(self, newstate, oldstate):
		if newstate == Phonon.PlayingState:
			self.button.setText('Stop')
		elif (newstate != Phonon.LoadingState and
			  newstate != Phonon.BufferingState):
			self.button.setText('Choose File')
			if newstate == Phonon.ErrorState:
				source = self.media.currentSource().fileName()
				print ('ERROR: could not play:', source.toLocal8Bit().data())
				print ('  %s' % self.media.errorString().toLocal8Bit().data())

def main():
	"""docstring for main"""
	import sys
	global win
	win = QtGui.QMainWindow()
	PyForm=Window()
	win.setCentralWidget(PyForm)
	win.show()


if __name__ == '__main__':

	import sys
	app = QtGui.QApplication(sys.argv)
	app.setApplicationName('Phonon Player')
	window = Window()
	window.show()
	sys.exit(app.exec_())
