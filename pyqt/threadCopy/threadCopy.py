class ProgressDialog(QtGui.QDialog):

    def __init__(self, parent, source, destination):
        QtGui.QDialog.__init__(self, parent)
        self.parent = parent
        self.source = source
        self.destination = destination
        self.add_diag = progress_diag.Ui_Dialog()
        self.add_diag.setupUi(self)

        self.add_diag.infoLabel.setText("Copying: %s" % (self.source))

        self.add_diag.progressBar.setMinimum(0)
        self.add_diag.progressBar.setMaximum(100)
        self.add_diag.progressBar.setValue(0)

        self.show()
        self.copy()

    def copy(self):

        copy_thread = CopyThread(self, self.source, self.destination)
        copy_thread.procPartDone.connect(self.update_progress)
        copy_thread.procDone.connect(self.finished_copy)
        copy_thread.start()

    def update_progress(self, progress):
        self.add_diag.progressBar.setValue(progress)

    def finished_copy(self, state):
        self.close()

class CopyThread(QtCore.QThread):

    procDone = QtCore.pyqtSignal(bool)
    procPartDone = QtCore.pyqtSignal(int)

    def __init__(self, parent, source, destination):
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
