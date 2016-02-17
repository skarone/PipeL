import os
import general.ui.pySideHelper as uiH
reload( uiH )

from Qt import QtGui,QtCore

class TitleFrame(QtGui.QFrame):
	def __init__(self, parent = None):
		QtGui.QFrame.__init__(self, parent = parent)
		self.setContentsMargins(0, 0, 0, 0)
		self.setMinimumHeight(24)
		self.setStyleSheet("QFrame {\
		background-color: QLinearGradient( x1: 0, y1: 0, x2: 0, y2: 1, stop: 0 #545454, stop: 1 #232323);\
		border-top: 1px solid rgba(192, 192, 192, 255);\
		border-left: 1px solid rgba(192, 192, 192, 255);\
		border-right: 1px solid rgba(64, 64, 64, 255);\
		border-bottom: 1px solid rgba(64, 64, 64, 255);\
		margin: 0px, 0px, 0px, 0px;\
		padding: 0px, 0px, 0px, 0px;\
		}\
		QFrame:hover {\
		background-color: QLinearGradient( x1: 0, y1: 0, x2: 0, y2: 1, stop: 0 #232323, stop: 1 #545454);\
		}")
		
	def mousePressEvent(self, *args, **kwargs):
		self.emit(QtCore.SIGNAL('clicked()'))
		return QtGui.QFrame.mousePressEvent(self, *args, **kwargs)     
		
		
		
class FrameLayout(QtGui.QFrame):
	def __init__(self, parent = None):
		QtGui.QFrame.__init__(self, parent = parent)
		
		self.isCollapsed = False
		self.mainLayout = None
		self.titleFrame = None
		self.contentFrame = None
		self.contentLayout = None
		
		self.initFrameLayout()
		
	def addWidget(self, widget):
		self.contentLayout.addWidget(widget)

	def initMainLayout(self):
		self.mainLayout = QtGui.QVBoxLayout()
		self.mainLayout.setContentsMargins(0, 0, 0, 0)
		self.mainLayout.setSpacing(0)
		self.setLayout(self.mainLayout)
		
	def initTitleFrame(self):
		self.titleFrame = TitleFrame()
		self.mainLayout.addWidget(self.titleFrame)
		
	def initContentFrame(self):
		self.contentFrame = QtGui.QFrame()
		self.contentFrame.setContentsMargins(0, 0, 0, 0)
		self.contentFrame.setStyleSheet("QFrame {\
		background-color: grey;\
		border-top: 1px solid rgba(64, 64, 64, 255);\
		border-left: 1px solid rgba(64, 64, 64, 255);\
		border-right: 1px solid rgba(192, 192, 192, 255);\
		border-bottom: 1px solid rgba(192, 192, 192, 255);\
		margin: 0px, 0px, 0px, 0px;\
		padding: 0px, 0px, 0px, 0px;\
		}")
		
		self.contentLayout = QtGui.QVBoxLayout()
		self.contentLayout.setContentsMargins(0, 0, 0, 0)
		self.contentLayout.setSpacing(0)
		self.contentFrame.setLayout(self.contentLayout)
		self.mainLayout.addWidget(self.contentFrame)
 
	def printSomething(self):
		self.contentFrame.setVisible(not self.isCollapsed)
		self.isCollapsed = not self.isCollapsed
		
	def initFrameLayout(self):
		self.setContentsMargins(0, 0, 0, 0)
		self.setStyleSheet("QFrame {\
		border: 0px solid;\
		margin: 0px, 0px, 0px, 0px;\
		padding: 0px, 0px, 0px, 0px;\
		}")
		
		self.initMainLayout()
		self.initTitleFrame()
		self.initContentFrame()
		
		#self.connect(self.titleFrame, QtCore.SIGNAL('clicked'), self.contentLayout, QtCore.SLOT('hide'))
		QtCore.QObject.connect(self.titleFrame, QtCore.SIGNAL('clicked()'), self.printSomething)
		
		self.addWidget(QtGui.QPushButton('a'))
		self.addWidget(QtGui.QPushButton('b'))
		self.addWidget(QtGui.QPushButton('c'))    
		
   
def main():
	global win
	win = QtGui.QMainWindow()
	win.setStyleSheet("QMainWindow {background-color: green;}")
	w = QtGui.QWidget()   
	win.setCentralWidget(w)
	l = QtGui.QVBoxLayout()
	w.setLayout(l)
	l.addStretch(0.2)
	l.addWidget(FrameLayout())
	l.addWidget(FrameLayout())
	win.show()
		
if __name__ == '__main__':
	import sys
	app = QtGui.QApplication(sys.argv)
	win = QtGui.QMainWindow()
	win.setStyleSheet("QMainWindow {background-color: green;}")
	w = QtGui.QWidget()   
	win.setCentralWidget(w)
	l = QtGui.QVBoxLayout()
	w.setLayout(l)
	l.addStretch(0.2)
	l.addWidget(FrameLayout())
	l.addWidget(FrameLayout())
	win.show()
	win.raise_()
	
	sys.exit(app.exec_())
