import general.ui.pySideHelper as uiH
reload( uiH )
uiH.set_qt_bindings()
from Qt import QtGui,QtCore
import nuke
import os
import pipe.project.project as prj
import pipe.sequence.sequence as sq
import pipe.shot.shot as sht
import pipe.settings.settings as sti
import pipe.sequenceFile.sequenceFile as sqFil
reload( sti )
import nuk.general.read as rd


#load UI FILE
PYFILEDIR = os.path.dirname( os.path.abspath( __file__ ) )

uifile = PYFILEDIR + '/readAllLayers.ui'
fom, base = uiH.loadUiType( uifile )

class LoadReadsUi(base,fom):
	"""manager ui class"""
	def __init__(self):
		if uiH.USEPYQT:
			super(base, self).__init__()
		else:
			super(LoadReadsUi, self).__init__()
		self.setupUi(self)
		self.settings = sti.Settings()
		self.gen = self.settings.General
		self.his = self.settings.History
		self.loadSettings()
		self.updateUi()
		self.connect( self.load_btn, QtCore.SIGNAL("clicked()") , self.load )		
		QtCore.QObject.connect( self.projects_cmb, QtCore.SIGNAL( "activated( const QString& )" ), self.fillSequences )
		QtCore.QObject.connect( self.sequences_cmb, QtCore.SIGNAL( "activated( const QString& )" ), self.fillShots )

	def loadSettings(self):
		"""docstring for loadSettings"""
		skin = self.gen[ "skin" ]
		if skin:
			uiH.loadSkin( self, skin )
		basePath = self.gen[ "basepath" ]
		if basePath:
			if basePath.endswith( '\\' ):
				basePath = basePath[:-1]
			prj.BASE_PATH = basePath.replace( '\\', '/' )

	def updateUi(self):
		"""docstring for updateUi"""
		self.fillProjects()
		self.fillSequences()
		self.fillShots()

	def fillProjects(self):
		"""docstring for fillProjects"""
		projects = prj.projects( prj.BASE_PATH )
		self.projects_cmb.addItems( projects )
		root = nuke.root()
		if root.knob( 'pipPorject' ):
			index = self.projects_cmb.findText( root[ 'pipPorject' ].value() )
			if not index == -1:
				self.projects_cmb.setCurrentIndex(index)

	def fillSequences(self):
		"""docstring for fillSequences"""
		proj = prj.Project( str( self.projects_cmb.currentText() ), prj.BASE_PATH )
		self.sequences_cmb.clear()
		self.sequences_cmb.addItems( [a.name for a in proj.sequences] )
		root = nuke.root()
		if root.knob( 'pipSequence' ):
			index = self.sequences_cmb.findText( root[ 'pipSequence' ].value() )
			if not index == -1:
				self.sequences_cmb.setCurrentIndex(index)

	def fillShots(self):
		"""docstring for fillShot"""
		proj = prj.Project( str( self.projects_cmb.currentText() ), prj.BASE_PATH )
		seque = sq.Sequence( str( self.sequences_cmb.currentText() ), proj )
		self.shots_cmb.clear()
		self.shots_cmb.addItems( [a.name for a in seque.shots] )
		root = nuke.root()
		if root.knob( 'pipShot' ):
			index = self.shots_cmb.findText( root[ 'pipShot' ].value() )
			if not index == -1:
				self.shots_cmb.setCurrentIndex(index)

	def load(self):
		"""docstring for load"""
		proj = str( self.projects_cmb.currentText() )
		sequ = str( self.sequences_cmb.currentText() )
		sho  = str( self.shots_cmb.currentText() )
		curShot = sht.Shot( sho, sq.Sequence( sequ, prj.Project( proj )))
		renderPath = self.gen[ "renderpath" ]
		localNuke  = self.gen[ "localnukepath" ]
		layers = curShot.renderedLayers( renderPath )

		root = nuke.root()
		if not root.knob( 'pipPorject' ):
			pipProj = nuke.String_Knob( 'pipPorject', 'Project' )
			root.addKnob( pipProj ) 
		if not root.knob( 'pipSequence' ):
			pipSeq = nuke.String_Knob( 'pipSequence', 'Sequence' )
			root.addKnob( pipSeq ) 
		if not root.knob( 'pipShot' ):
			pipShot = nuke.String_Knob( 'pipShot', 'Shot' )
			root.addKnob( pipShot ) 
		root[ 'pipPorject' ].setValue( proj )
		root[ 'pipSequence' ].setValue( sequ )
		root[ 'pipShot' ].setValue( sho )

		for l in layers:
			l = str( l )
			node = nuke.createNode( 'Read' )
			if node:
				node['PipeL'].setFlag( 0 )
				node[ 'name' ].setValue( l )
				node[ 'projectSel' ].setValue( proj )
				node[ 'seqSel' ].setValue( sequ )
				node[ 'shotSel' ].setValue( sho )
				node[ 'layerSel' ].setValue( l )
				vers = curShot.renderedLayerVersions( renderPath, l )
				node[ '_version' ].setValue( vers[-1] )
				pat = curShot.renderedLayerVersionPath( renderPath, l, vers[-1] )
				seqNode = sqFil.sequenceFile( pat + l + '.*' )
				if self.copyLocal_chb.isChecked():
					newPath = self.pathFromStructure( localNuke, proj, sequ, sho, l )
					seqNode = seqNode.copy( newPath + vers[-1] + '/' )
				node['file'].setValue( seqNode.seqPath )
				node['first'].setValue( seqNode.start )
				node['last'].setValue( seqNode.end )

	def pathFromStructure( self, basePath, project, sequence, shot, layer ):
		"""
		basePath should be something like this...
		"D:/Projects/<project>/Sequences/<sequence>/Shots/<shot>/Renders/<layer>"
		X:/<project>/-Materiales-/3D/<sequence>/<shot>/<layer>
		"""
		basePath = basePath.replace( '<project>', project )
		basePath = basePath.replace( '<sequence>', sequence )
		basePath = basePath.replace( '<shot>', shot )
		return basePath.replace( '<layer>', layer ) + '/'
			

def main():
	global PyForm
	PyForm=LoadReadsUi()
	PyForm.show()
		
if __name__=="__main__":
	import sys
	a = QtGui.QApplication(sys.argv)
	global PyForm
	a.setStyle('plastique')
	PyForm=CacheManagerUI()
	PyForm.show()
	sys.exit(a.exec_())

			

