import os
import general.ui.pySideHelper as uiH

from Qt import QtGui,QtCore
from PySide.phonon import Phonon
#load UI FILE
try:
    PYFILEDIR = os.path.dirname(os.path.abspath(__file__))
except NameError:  # We are the main py2exe script, not a module
    import sys
    PYFILEDIR = os.path.dirname(os.path.abspath(sys.argv[0]))
uifile = PYFILEDIR + '/botonera.ui'
fom, base = uiH.loadUiType( uifile )
import pyqt.flowlayout.flowlayout as flowlayout
reload(flowlayout)
import random as rand

class Botonera(base,fom):
	"""main class to handle botonera ui"""
	def __init__(self, parent = None ):
		super(Botonera, self).__init__(parent)
		self.audio_output = Phonon.AudioOutput(Phonon.MusicCategory, self)
		self.media_obj = Phonon.MediaObject(self)
		self.setObjectName( 'Botonera' )
		self.grid = flowlayout.FlowLayout()
		self.fillUi( PYFILEDIR + '/sounds' )
		self.setupUi(self)
		wid = QtGui.QWidget()
		wid.setLayout( self.grid )
		self.buttons_lay.addWidget( wid )
		QtCore.QObject.connect( self.actionOpen_Folder, QtCore.SIGNAL( "triggered()" ), self.openFolder )

	def openFolder(self):
		"""docstring for openFolder"""
		dlg=QtGui.QFileDialog( self ).getExistingDirectory()
		if dlg:
			for i in reversed(range(self.grid.count())):
				self.grid.itemAt(i).widget().setParent(None)
			self.fillUi( dlg )


	def fillUi(self, path):
		"""load files in path"""
		sounds = [QtGui.QSound( os.path.join( path, a ) ) for a in os.listdir( path ) if any( a.endswith( ext ) for ext in [ '.mp3', '.wav' ] ) ]
		for s in sounds:
			butt = QtGui.QToolButton()
			butt.setToolButtonStyle(QtCore.Qt.ToolButtonTextUnderIcon)
			butt.setStyleSheet( "border: none;")
			butt.setText(os.path.basename( s.fileName() ) )
			temp = QtGui.QPixmap(PYFILEDIR + '/button_grey.png')
			msk = temp.alphaChannel()
			color = QtGui.QColor(rand.randint(0,255),
								rand.randint(0,255),
								rand.randint(0,255),255)
			painter = QtGui.QPainter(temp)
			painter.setCompositionMode(painter.CompositionMode_Overlay)
			painter.fillRect(temp.rect(), color)
			painter.end()
			temp.setAlphaChannel( msk )
			ButtonIcon = QtGui.QIcon(temp)
			butt.setIcon(ButtonIcon);
			butt.setIconSize(temp.rect().size());
			QtCore.QObject.connect( butt, QtCore.SIGNAL( "clicked()" ), lambda sound = s : self.play( sound ) )
			self.grid.addWidget( butt )


	def play(self, sound):
		"""docstring for play"""
		Phonon.createPath(self.media_obj, self.audio_output)
		self.media_obj.stop()
		self.media_obj.setCurrentSource(Phonon.MediaSource(sound.fileName()))
		self.media_obj.play()


if __name__ == '__main__':
	import sys
	a = QtGui.QApplication(sys.argv)
	a.setStyle('plastique')
	PyForm=Botonera()
	PyForm.show()
	sys.exit(a.exec_())


