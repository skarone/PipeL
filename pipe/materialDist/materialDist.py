import os
import general.ui.pySideHelper as uiH
uiH.set_qt_bindings()
from Qt import QtGui,QtCore
PYFILEDIR = os.path.dirname( os.path.abspath(__file__) )
uifile = PYFILEDIR + '/materialDist.ui'
fom, base = uiH.loadUiType( uifile )
import shutil

import pipe.project.project   as prj
reload( prj )
import pipe.project.projectUI as prjUi
reload( prjUi )
import pipe.asset.assetUI as assUi
reload( assUi )
import pipe.sets.setsUI as setUi
reload( setUi )
import pipe.shot.shotUI as shUI
reload( shUI )
import pipe.sequence.sequenceUI as sqUI
reload( sqUI )
import pipe.shot.shot as sh
reload( sh )
import pipe.sequence.sequence as sq
reload( sq )

class MaterailDist(base,fom):
	"""docstring for MaterailDist"""
	def __init__(self, parent = None ):
		super(MaterailDist, self).__init__(parent)
		self.setupUi(self)
		self.setObjectName( 'MaterailDist' )
		self._makeConnections()
		self.fillProjectsCombo()
		lineEdit_dragFile_injector(self.refClient_le)
		lineEdit_dragFile_injector(self.refStudio_le)
		lineEdit_dragFile_injector(self.offline_le)
		lineEdit_dragFile_injector(self.story_le)
		lineEdit_dragFile_injector(self.feedback_le)
		lineEdit_dragFile_injector(self.footHigh_le)
		lineEdit_dragFile_injector(self.footLow_le)
		lineEdit_dragFile_injector(self.elements_le)
		lineEdit_dragFile_injector(self.lipSync_le)
		lineEdit_dragFile_injector(self.art_le)

	def fillProjectsCombo(self):
		"""fill projects combo with projects in local disc"""
		self.projects_cmb.clear()
		projects = prj.projects( prj.BASE_PATH )
		self.projects_cmb.addItems( projects )

	def fillAssetsCombo(self):
		"""fill the table with the assets in the project"""
		proj = prj.Project( str( self.projects_cmb.currentText()), prj.BASE_PATH )
		self.assets_cmb.clear()
		if not proj.name:
			return
		assets = proj.assets
		self.assets_cmb.addItems( [a.name for a in assets ] )

	def fillSequenceCombo(self):
		"""fill list of sequence"""
		proj = prj.Project( str( self.projects_cmb.currentText() ), prj.BASE_PATH )
		if not proj.name:
			return
		self.sequences_cmb.clear()
		seqs = proj.sequences
		self.sequences_cmb.addItems([s.name for s in seqs] )

	def fillShotsCombo(self):
		"""fill the tables with the shots of the selected sequence"""
		proj = prj.Project( str( self.projects_cmb.currentText()), prj.BASE_PATH )
		sequence  = sq.Sequence( str( self.sequences_cmb.currentText() ), proj )
		self.shots_cmb.clear()
		shots = sequence.shots
		shots = sorted(shots, key=lambda s: s.name[s.name.index('_')+1:])
		self.shots_cmb.addItems( [s.name for s in shots ] )

	def updateUi(self):
		"""docstring for updateUi"""
		self.fillAssetsCombo()
		self.fillSequenceCombo()

	def _makeConnections(self):
		"""docstring for fname"""
		self.connect( self.transfer_btn, QtCore.SIGNAL("clicked()") , self.transfer )
		self.connect( self.newProj_btn, QtCore.SIGNAL("clicked()") , self._newProject )
		self.connect( self.newAsset_btn, QtCore.SIGNAL("clicked()") , self._newAsset )
		self.connect( self.newSeq_btn, QtCore.SIGNAL("clicked()") , self._newSequence )
		self.connect( self.newShot_btn, QtCore.SIGNAL("clicked()") , self._newShot )
		self.connect( self.addRefClient_btn, QtCore.SIGNAL( "clicked()" ), lambda val = self.refClient_le : self.addFiles(val) )
		self.connect( self.addRefStudio_btn, QtCore.SIGNAL( "clicked()" ), lambda val = self.refStudio_le : self.addFiles(val) )
		self.connect( self.addOffline_btn, QtCore.SIGNAL( "clicked()" ), lambda val = self.offline_le : self.addFiles(val) )
		self.connect( self.addStory_btn, QtCore.SIGNAL( "clicked()" ), lambda val = self.story_le : self.addFiles(val) )
		self.connect( self.addFeedback_btn, QtCore.SIGNAL( "clicked()" ), lambda val = self.feedback_le : self.addFiles(val) )
		self.connect( self.addFootHigh_btn, QtCore.SIGNAL( "clicked()" ), lambda val = self.footHigh_le : self.addFiles(val) )
		self.connect( self.addFootLow_btn, QtCore.SIGNAL( "clicked()" ), lambda val = self.footLow_le : self.addFiles(val) )
		self.connect( self.addElement_btn, QtCore.SIGNAL( "clicked()" ), lambda val = self.elements_le : self.addFiles(val) )
		self.connect( self.addLipSync_btn, QtCore.SIGNAL( "clicked()" ), lambda val = self.lipSync_le : self.addFiles(val) )
		self.connect( self.addArt_btn, QtCore.SIGNAL( "clicked()" ), lambda val = self.art_le : self.addFiles(val) )
		QtCore.QObject.connect( self.projects_cmb, QtCore.SIGNAL( "activated( const QString& )" ), self.updateUi )
		QtCore.QObject.connect( self.sequences_cmb, QtCore.SIGNAL( "activated( const QString& )" ), self.fillShotsCombo )

	def addFiles(self, le):
		"""add files or folders to specific line edit"""
		fil = QtGui.QFileDialog.getOpenFileNames(self, "Select Files")
		if fil:
			le.setText( ','.join( fil[0] ) )

	def _newProject(self):
		"""create new project ui"""
		dia = prjUi.ProjectCreator(self)
		res = dia.exec_()
		if res:
			self.fillProjectsCombo()

	def _newAsset(self):
		"""creates new Asset"""
		dia = assUi.AssetCreator( self )
		dia.show()
		index = dia.projects_cmb.findText( str( self.projects_cmb.currentText()) )
		if not index == -1:
			dia.projects_cmb.setCurrentIndex(index)
		res = dia.exec_()
		if res:
			self.fillAssetsCombo()

	def _newSequence(self):
		"""creates a new sequence"""
		dia = sqUI.SequenceCreator(self)
		dia.show()
		index = dia.projects_cmb.findText( str( self.projects_cmb.currentText()) )
		if not index == -1:
			dia.projects_cmb.setCurrentIndex(index)
		res = dia.exec_()
		if res:
			self.fillSequenceCombo()

	def _newShot(self):
		"""creates a new Shot"""
		dia = shUI.ShotCreator( self.projects_cmb.currentText(), self.sequences_cmb.currentText(), self )
		dia.show()
		index = dia.projects_cmb.findText( str( self.projects_cmb.currentText()) )
		if not index == -1:
			dia.projects_cmb.setCurrentIndex(index)
		res = dia.exec_()
		if res:
			self.fillShotsCombo()

	def transfer(self):
		"""docstring for transfer"""
		proj = prj.Project( str( self.projects_cmb.currentText()), prj.BASE_PATH )
		seq = sq.Sequence( str( self.sequences_cmb.currentText()), proj )
		sht = sh.Shot( str( self.shots_cmb.currentText()), seq )
		asset = ass.Asset( str( self.assets_cmb.currentText()), proj )
		les = {self.refClient_le: seq.clientRefPath,
				self.refStudio_le : seq.studioRefPath,
				self.offline_le : seq.offlinePath,
				self.story_le : seq.storyPath,
				self.feedback_le : seq.feedbackPath,
				self.footHigh_le : sht.footageHighPath,
				self.footLow_le : sht.footageLowPath,
				self.elements_le : sht.compElementsPath,
				self.lipSync_le : sht.lipSyncPath,
				self.art_le : asset.artPath}
		for l in les.keys():
			self.copyFiles( l, les[l] )

	def copyFiles( self, le, dst ):
		"""docstring for copyFiles"""
		for f in le.Text().split( ',' ):
			for item in os.listdir(f):
				s = os.path.join(f, item)
				d = os.path.join(dst, item)
				if os.path.exists(d):
					if os.path.exists( s ):
						if os.path.isdir(s):
							shutil.copytree(s, d)
						else:
							shutil.copy2(s, d)

class lineEdit_ = self.feedback_le :dragFile_injector():
	def __init_ = self.footHigh_le :_(self, lineEdit, auto_inject = True):
		self.li= self.footLow_le : sneEdit = lineEdit
		if auto= self.elements_le : _inject:
			sel= self.lipSync_le : sf.inject_dragFile()
               lf.art_le : self.addF
	def inject_dragFile( self ):
		self.lineEdit.setDragEnabled(True)
		self.lineEdit.dragEnterEvent = self._dragEnterEvent
		self.lineEdit.dragMoveEvent = self._dragMoveEvent
		self.lineEdit.dropEvent = self._dropEvent

	def _dragEnterEvent( self, event ):
		data = event.mimeData()
		urls = data.urls()
		if ( urls and urls[0].scheme() == 'file' ):
			event.acceptProposedAction()

	def _dragMoveEvent( self, event ):
		data = event.mimeData()
		urls = data.urls()
		if ( urls and urls[0].scheme() == 'file' ):
			event.acceptProposedAction()

	def _dropEvent( self, event ):
		data = event.mimeData()
		urls = data.urls()
		if ( urls and urls[0].scheme() == 'file' ):
			# for some reason, this doubles up the intro slash
			filepath = ','.join([ str(u.path())[1:] for u in urls] )
			self.lineEdit.setText(filepath)

def main():
	global MatDist
	MatDist=MaterailDist(QtGui.QApplication.activeWindow())
	MatDist.show()
