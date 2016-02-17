import os
import general.ui.pySideHelper as uiH
reload( uiH )

from Qt import QtGui,QtCore

import pipe.project.project   as prj
import pipe.sequence.sequence as seq
import pipe.shot.shot as sh
reload( prj )
import pipe.settings.settings as sti
reload( sti )

PYFILEDIR = os.path.dirname( os.path.abspath( __file__ ) )

uifile = PYFILEDIR + '/shot.ui'
fom, base = uiH.loadUiType( uifile )

class ShotCreator(base, fom):
	"""docstring for ProjectCreator"""
	def __init__(self, currentProj, currentSeq, parent = None ):
		if uiH.USEPYQT:
			super(base, self).__init__(parent)
		else:
			super(ShotCreator, self).__init__(parent)
		self.setupUi(self)
		self._curProj = currentProj
		self._curSeq  = currentSeq
		self.connect(self.buttonBox, QtCore.SIGNAL("accepted()"), self.createShot)
		self.settings = sti.Settings()
		self.loadProjectsPath()
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

	def loadProjectsPath(self):
		"""docstring for loadProjectsPath"""
		gen = self.settings.General
		if gen:
			basePath = gen[ "basepath" ]
			if basePath:
				if basePath.endswith( '\\' ):
					basePath = basePath[:-1]
				prj.BASE_PATH = basePath.replace( '\\', '/' )

	def fillProjectsCMB(self):
		"""fill combo box with projects"""
		self.projects_cmb.clear()
		self.projects_cmb.addItems( prj.projects( prj.BASE_PATH ) )

	def fillSequencesCMB(self):
		"""fill combo box with sequences"""
		self.sequences_cmb.clear()
		projName =  str( self.curProj )
		self.sequences_cmb.addItems( [ s.name for s in prj.Project( projName, prj.BASE_PATH ).sequences ] )
		index = self.sequences_cmb.findText( self.curSeq )
		self.sequences_cmb.setCurrentIndex( index )

	def createShot(self):
		"""create New Asset Based on new project name"""
		projName =  str( self.projects_cmb.currentText() )
		seqName =  str( self.sequences_cmb.currentText() )
		assetName = str( self.shot_le.text() )
		se = seq.Sequence( seqName, prj.Project( projName, prj.BASE_PATH ) )
		shotsCount = self.shotsCount_sp.value()
		for s in range(1, shotsCount + 1 ):
			#get last s number
			shots = se.shots
			lastShotNumber = 0
			if len(shots):
				lastShot = shots[-1].name
				lastShotNumber = int( lastShot.split( '_' )[0][1:] )
			if '#' in assetName:
				finalAssetName = assetName.replace( '#'*assetName.count('#'), str( s ).zfill( assetName.count( '#' ) ))
			else:
				finalAssetName = assetName
			newAsset = sh.Shot( 's' + str(lastShotNumber + 1 ).zfill( 3 ) + '_' + seqName + '_'  + finalAssetName ,  se )
			if not newAsset.exists:
				newAsset.create()
				print 'New Shot Created : ', newAsset.name, ' for ',  projName

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

