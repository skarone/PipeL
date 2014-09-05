import os
import general.ui.pySideHelper as uiH
reload( uiH )
uiH.set_qt_bindings()
from Qt import QtGui,QtCore

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

    procDone = QtCore.pyqtSignal(bool)
    procPartDone = QtCore.pyqtSignal(int)

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
