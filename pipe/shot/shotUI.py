import os
from PyQt4 import QtGui,QtCore, uic
import pipe.project.project   as prj
import pipe.sequence.sequence as seq
import pipe.shot.shot as sh
reload( prj )

PYFILEDIR = os.path.dirname( os.path.abspath( __file__ ) )

uifile = PYFILEDIR + '/shot.ui'
fom, base = uic.loadUiType( uifile )

class ShotCreator(base, fom):
	"""docstring for ProjectCreator"""
	def __init__(self, currentProj, currentSeq ):
		super(base, self).__init__()
		self.setupUi(self)
		self._curProj = currentProj
		self._curSeq  = currentSeq
		self.connect(self.buttonBox, QtCore.SIGNAL("accepted()"), self.createShot)
		self.fillProjectsCMB()
		self.fillSequencesCMB()
		self.shot_le.setFocus()

	@property
	def curProj(self):
		"""docstring for curProj"""
		return self._curProj

	@property
	def curSeq(self):
		"""docstring for curSeq"""
		return self._curSeq

	def fillProjectsCMB(self):
		"""fill combo box with projects"""
		self.projects_cmb.clear()
		self.projects_cmb.addItems( prj.projects() )
	
	def fillSequencesCMB(self):
		"""fill combo box with sequences"""
		self.sequences_cmb.clear()
		projName =  str( self.curProj )
		self.sequences_cmb.addItems( [ s.name for s in prj.Project( projName ).sequences ] )
		index = self.sequences_cmb.findText( self.curSeq )
		self.sequences_cmb.setCurrentIndex( index )

	def createShot(self):
		"""create New Asset Based on new project name"""
		projName =  str( self.projects_cmb.currentText() )
		seqName =  str( self.sequences_cmb.currentText() )
		assetName = self.shot_le.text()
		se = seq.Sequence( seqName, prj.Project( projName ) )
		newAsset = sh.Shot( 's' + str(len( se.shots ) + 1 ).zfill( 3 ) + '_' +  str( assetName ),  se )
		if not newAsset.exists:
			newAsset.create()
			print 'New Shot Created : ', newAsset.name, ' for ',  projName
			QtGui.QDialog.accept(self)
		else:
			QtGui.QDialog.reject(self)

class Window(QtGui.QMainWindow):
	def __init__(self):
		QtGui.QMainWindow.__init__(self)
		dia = ShotCreator()
		dia.exec_()
	
def main():
	"""use this to create project in maya"""
	pass


if __name__=="__main__":
	import sys
	a = QtGui.QApplication(sys.argv)
	global PyForm
	a.setStyle('plastique')
	PyForm=Window()
	PyForm.show()
	sys.exit(a.exec_())

