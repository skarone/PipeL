from PyQt4 import QtCore, QtGui

class StackedWidget(QtGui.QStackedWidget):
	"""Handle the different widgets in the stack of tools dock."""
	def setCurrentIndex(self, index):
		"""Change the current widget being displayed with an animation."""
		self.fader_widget = FaderWidget(self.currentWidget(), self.widget(index))
		QtGui.QStackedWidget.setCurrentIndex(self, index)

class FaderWidget(QtGui.QWidget):
	def __init__(self, old_widget, new_widget):
		QtGui.QWidget.__init__(self, new_widget)
		self.old_pixmap = QtGui.QPixmap(new_widget.size())
		old_widget.render(self.old_pixmap)
		self.pixmap_opacity = 1.0

		self.timeline = QtCore.QTimeLine()
		self.timeline.valueChanged.connect(self.animate)
		self.timeline.finished.connect(self.close)
		self.timeline.setDuration(500)
		self.timeline.start()

		self.resize(new_widget.size())
		self.show()

	def paintEvent(self, event):
		painter = QtGui.QPainter()
		painter.begin(self)
		painter.setOpacity(self.pixmap_opacity)
		painter.drawPixmap(0, 0, self.old_pixmap)
		painter.end()

	def animate(self, value):
		self.pixmap_opacity = 1.0 - value
		self.repaint()
