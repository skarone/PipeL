import os
import general.ui.pySideHelper as uiH
reload( uiH )
uiH.set_qt_bindings()
from Qt import QtGui,QtCore
import shiboken

import maya.OpenMayaUI as mui

import maya.cmds as mc
import pipe.file.file as fl
import general.mayaNode.mayaNode as mn
reload( mn )

import pipe.settings.settings as sti
reload( sti )
import pipe.project.project as prj

import cPickle as pickle

import pyqt.accordionwidget.accordionwidget as cgroup
import pyqt.flowlayout.flowlayout as flowlayout
reload( flowlayout )
import shutil

"""
import animation.poseMan.poseManUi as posUi
reload( posUi )

posUi.main()
"""

PYFILEDIR = os.path.dirname( os.path.abspath( __file__ ) )

uifile = PYFILEDIR + '/poseThumbnailCreatorUi.ui'
fom, base = uiH.loadUiType( uifile )

uifile = PYFILEDIR + '/poseThumbnailUi.ui'
fomThum, baseThum = uiH.loadUiType( uifile )

uifile = PYFILEDIR + '/poseManUi.ui'
fomBase, baseBase = uiH.loadUiType( uifile )

uifile = PYFILEDIR + '/sectionUi.ui'
fomSec, baseSec = uiH.loadUiType( uifile )

uifile = PYFILEDIR + '/poseSlider.ui'
fomSlid, baseSlid = uiH.loadUiType( uifile )


class PoseThumbnailCreatorUi(base, fom):
	poseCreated = QtCore.Signal(bool)
	sectionCreated = QtCore.Signal(bool)
	def __init__(self, project, pose = None, parent  = uiH.getMayaWindow() ):
		if uiH.USEPYQT:
			super(base, self).__init__(parent)
		else:
			super(PoseThumbnailCreatorUi, self).__init__(parent)
		self.setupUi(self)
		self.project = project
		self.pose = pose
		layout = mui.MQtUtil.fullName(long(shiboken.getCppPointer(self.viewport_lay)[0]))
		self.cam = mn.Node( 'Capture_Pose' )
		if not self.cam.exists:
			self.camShape = mn.createNode( 'camera', ss = True )
			self.camShape.parent.name = 'Capture_Pose'
			mc.viewSet( self.cam.name, p = True )
			self.cam.shape.a.focalLength.v = 100
			self.cam.a.v.v = 0
		self.executer = mc.modelPanel( mbv = False, camera = self.cam.name, p = layout )
		mc.modelEditor(self.executer, e = True, grid = 0, da = "smoothShaded", allObjects = 0, nurbsSurfaces = 1, polymeshes = 1, subdivSurfaces = 1 )
		#self.viewport_lay.addWidget( uiH.toQtObject( self.executer ) )
		self.setObjectName( 'PoseThumbnailCreatorUi' )
		self._makeConnections()
		self.saveCameraPreset = 0 #READ, 1.. WRITE
		self.settings = sti.Settings()
		gen = self.settings.General
		skin = gen[ "skin" ]
		if skin:
			uiH.loadSkin( self, skin )
		if pose:
			self.poseName_le.setText( pose.name )
		self.fillSections()

	def _makeConnections(self):
		"""create connections for UI"""
		self.connect( self.cameraPreset_1_btn, QtCore.SIGNAL("clicked()") , lambda cameraNumber = 1 : self.cameraPreset( cameraNumber ) )
		self.connect( self.cameraPreset_2_btn, QtCore.SIGNAL("clicked()") , lambda cameraNumber = 2 : self.cameraPreset( cameraNumber ) )
		self.connect( self.cameraPreset_3_btn, QtCore.SIGNAL("clicked()") , lambda cameraNumber = 3 : self.cameraPreset( cameraNumber ) )
		self.connect( self.cameraPreset_4_btn, QtCore.SIGNAL("clicked()") , lambda cameraNumber = 4 : self.cameraPreset( cameraNumber ) )
		self.connect( self.cameraPreset_5_btn, QtCore.SIGNAL("clicked()") , lambda cameraNumber = 5 : self.cameraPreset( cameraNumber ) )
		self.connect( self.newSection_btn, QtCore.SIGNAL("clicked()") , self.newSection )
		self.connect( self.readWriteCameraPreset_btn, QtCore.SIGNAL("clicked()") , self.changeCameraPresetsButtonSystem )
		self.connect( self.createPose_btn, QtCore.SIGNAL("clicked()") , self.createPose )

	def fillSections(self):
		"""fill sections"""
		poseManPath = self.project.path + '/poseMan/'
		if not os.path.exists( poseManPath ):
			return []
		sections = [ a for a in os.listdir( poseManPath ) if os.path.isdir( poseManPath + a )]
		self.sections_cmb.clear()
		self.sections_cmb.addItems( sections )
		if self.pose:
			index = self.sections_cmb.findText( self.pose.section )
			if not index == -1:
				self.sections_cmb.setCurrentIndex(index)

	def newSection(self):
		"""docstring for newSection"""
		self.fillSections()
		self.sectionCreated.emit( True )

	def changeCameraPresetsButtonSystem(self):
		"""switch state for save or read camera Presets"""
		if self.saveCameraPreset:
			self.saveCameraPreset = 0
			self.readWriteCameraPreset_btn.setText( 'Read >>' )
			self.readWriteCameraPreset_btn.setStyleSheet("background-color: green")
		else:
			self.saveCameraPreset = 1
			self.readWriteCameraPreset_btn.setText( '<< Write' )
			self.readWriteCameraPreset_btn.setStyleSheet("background-color: red")

	def cameraPreset(self, presetNumber ):
		"""set or save camera preset on corresponding number"""
		if self.saveCameraPreset:# save camera preset for current button
			if not os.path.exists(self.cameraPosePath):
				os.makedirs( self.cameraPosePath )
			data = {}
			data[self.cam.a.t] = self.cam.a.t.v
			data[self.cam.a.r] = self.cam.a.r.v
			pickle.dump( data, open( self.cameraPosePath + 'camera' + str( presetNumber ) + '.pose' , "wb" ) )
		else: #read camera preset for current button
			data = pickle.load( open( self.cameraPosePath + 'camera' + str( presetNumber ) + '.pose', "rb") )
			for d in data.keys():
				d.v = data[d][0]
	
	@property
	def cameraPosePath(self):
		"""camerasPosePath"""
		return self.project.path + '/poseMan/' 

	@property
	def poseName(self):
		"""docstring for poseName"""
		return str( self.poseName_le.text() )

	@property
	def selectedSection(self):
		"""return selected section"""
		return str(self.sections_cmb.currentText())

	def createPose(self):
		"""docstring for createPose"""
		p = Pose( self.project, self.selectedSection, self.poseName )
		p.save()
		self.saveThumbnail( p )
		self.poseCreated.emit( True )

	def saveThumbnail( self, pose ):
		"""save current Thumbnail"""
		mc.setAttr( "defaultRenderGlobals.imageFormat", 20 )
		currentTime = mc.currentTime( q = True )
		mc.playblast( v = False, p = 100, frame = currentTime, w = 160, h = 160, orn = 0, cf = pose.poseThumbPath ,fmt = "image" )
		
	def closeEvent(self, evnt):
		if self.cam.exists:
			self.cam.delete()
		mc.deleteUI( self.executer, control=True )

class PoseSliderUi(baseSlid, fomSlid):
	def __init__(self, pose, parent  = uiH.getMayaWindow() ):
		if uiH.USEPYQT:
			super(baseSlid, self).__init__(parent)
		else:
			super(PoseSliderUi, self).__init__(parent)
		self.setupUi(self)
		self.poseTargetData = pose.controlsDataFromFile
		pose.controls.select()
		basePose = Pose( pose.project, pose.section, pose.name + 'base' )
		self.poseName_lbl.setText( pose.section + ' ' + pose.name )
		self.basePoseData = basePose.controlsData
		self.connect( self.poseSlider_sld, QtCore.SIGNAL("valueChanged(int)") , self.mixPose )

	def mixPose(self, val):
		"""mix values of slider"""
		for o in self.basePoseData.keys():
			for a in self.basePoseData[o].keys():
				mixedValue = (self.poseTargetData[o][a]*float( val )/100.0) + (self.basePoseData[o][a]*(1-float( val )/100.0));
				finalA = mn.NodeAttribute( mn.Node( Pose.NAMESPACE + o.name ), a.name  )
				finalA.v = mixedValue

class PoseThumbnailUi(baseThum, fomThum):
	poseDeleted = QtCore.Signal(bool)
	updateThumb = QtCore.Signal(object)
	def __init__(self, pose, parent  = uiH.getMayaWindow() ):
		if uiH.USEPYQT:
			super(baseThum, self).__init__(parent)
		else:
			super(PoseThumbnailUi, self).__init__(parent)
		self.setupUi(self)
		self.pose    = pose
		self.setContextMenuPolicy(QtCore.Qt.CustomContextMenu)
		self.customContextMenuRequested.connect(self.showMenu)
		self.pose_btn.setText( self.pose.name )
		self.connect( self.pose_btn, QtCore.SIGNAL("clicked()") , self.applyPose )
		self.setObjectName( 'PoseThumbnailUi' )
		myIcon = QtGui.QIcon( self.pose.poseThumbPath )
		self.pose_btn.setIcon(myIcon)

	def applyPose( self ):
		"""docstring for self.applyPose"""
		self.pose.load( )

	def showMenu(self, pos):
		"""show menu options for pose"""
		menu=QtGui.QMenu(self)
		selectControlsProperties = QtGui.QAction( "Select Controls", menu)
		deletePoseProperties  = QtGui.QAction( "Delete Pose", menu)
		sliderPoseProperties  = QtGui.QAction( "Create Slider", menu)
		updatePoseProperties  = QtGui.QAction( "Update Pose", menu)
		updateThumbProperties = QtGui.QAction( "Update Thumbnail Pose", menu)
		self.connect( selectControlsProperties, QtCore.SIGNAL( "triggered()" ), self.selectControlsProperties )
		self.connect( deletePoseProperties, QtCore.SIGNAL( "triggered()" ), self.deletePoseProperties )
		self.connect( sliderPoseProperties, QtCore.SIGNAL( "triggered()" ), self.sliderPoseProperties )
		self.connect( updatePoseProperties, QtCore.SIGNAL( "triggered()" ), self.updatePoseProperties )
		self.connect( updateThumbProperties, QtCore.SIGNAL( "triggered()" ), self.updateThumbProperties )
		menu.addAction( selectControlsProperties )
		menu.addAction( deletePoseProperties )
		menu.addAction( sliderPoseProperties )
		menu.addAction( updatePoseProperties )
		menu.addAction( updateThumbProperties )
		menu.popup(self.mapToGlobal(pos))

	def selectControlsProperties(self):
		"""docstring for selectControlsProperties"""
		self.pose.controls.select()
		
	def deletePoseProperties(self):
		"""docstring for deletePoseProperties"""
		self.pose.delete()
		self.poseDeleted.emit(True)

	def sliderPoseProperties(self):
		"""docstring for sliderPoseProperties"""
		slid = PoseSliderUi( self.pose )
		slid.show()

	def updatePoseProperties(self):
		"""docstring for updatePoseProperties"""
		self.pose.save()

	def updateThumbProperties(self):
		"""docstring for upda"""
		self.updateThumb.emit(self.pose)

class PoseManUi(baseBase, fomBase):
	def __init__(self, parent  = uiH.getMayaWindow() ):
		if uiH.USEPYQT:
			super(baseBase, self).__init__(parent)
		else:
			super(PoseManUi, self).__init__(parent)
		self.setupUi(self)
		self.setObjectName( 'PoseManUi' )
		self.settings = sti.Settings()
		self.loadSettings()
		self.fillProjects()
		self.loadLastProject()
		self.catLayout = cgroup.AccordionWidget(None)
		self.library_lay.addWidget( self.catLayout )
		self._makeConnections()
		self.fillSections()
		self.poses = []

	def _makeConnections(self):
		"""docstring for _makeConnections"""
		self.connect( self.newPose_btn, QtCore.SIGNAL("clicked()") , self.newPose )
		self.connect( self.newSection_btn, QtCore.SIGNAL("clicked()") , self.newSection )
		self.connect( self.deleteSection_btn, QtCore.SIGNAL("clicked()") , self.deleteSection )
		self.connect( self.setNameSpace_btn, QtCore.SIGNAL("clicked()") , self.setNameSpace )
		self.catLayout.itemMenuRequested.connect( self.showSectionMenu )

	def showSectionMenu(self, item):
		"""display menu on selected item"""
		menu=QtGui.QMenu(self)
		selectControlsProperties = QtGui.QAction( "Delete Section", menu)
		self.connect( selectControlsProperties, QtCore.SIGNAL( "triggered()" ), lambda pose = item : self.deleteSection( pose ) )
		menu.addAction( selectControlsProperties )
		menu.popup(self.mapToGlobal(self.mapFromGlobal(QtGui.QCursor.pos())) )

	def deleteSection(self, item):
		"""docstring for deleteSection"""
		sectionName = self.selectedProject.path + '/poseMan/' + item.title()
		shutil.rmtree( sectionName )
		self.fillSections()

	@property
	def selectedProject(self):
		"""return selected Project"""
		return prj.Project( str(self.projects_cmb.currentText()), self.serverPath )

	def newPose(self, pose = None ):
		"""docstring for newPose"""
		poseThumbCreator = PoseThumbnailCreatorUi( self.selectedProject, pose )
		poseThumbCreator.poseCreated.connect( self.fillSections )
		poseThumbCreator.sectionCreated.connect( self.fillSections )
		poseThumbCreator.show()

	def newSection(self):
		"""docstring for newSection"""
		dia = NewSection( self.selectedProject, self )
		dia.show()
		res = dia.exec_()
		if res:
			self.fillSections()

	def setNameSpace(self):
		"""docstring for setNameSpace"""
		sel = mn.ls( sl = True )
		if sel:
			self.namespace_lbl.setText( sel[0].namespace.name )
			Pose.NAMESPACE = sel[0].namespace.name
		else:
			self.namespace_lbl.setText( ':' )
			Pose.NAMESPACE = ':'
	
	def loadLastProject(self):
		"""docstring for loadLastProject"""
		his = self.settings.History
		if his:
			if 'lastproject' in his:
				lastProject = his[ "lastproject" ]
				if lastProject:
					index = self.projects_cmb.findText( lastProject )
					if not index == -1:
						self.projects_cmb.setCurrentIndex(index)

	def loadSettings(self):
		"""docstring for loadSettings"""
		gen = self.settings.General
		self.serverPath = ''
		serverPath = gen[ "serverpath" ]
		if serverPath:
			self.serverPath = serverPath
		skin = gen[ "skin" ]
		if skin:
			uiH.loadSkin( self, skin )

	def fillProjects(self):
		"""docstring for fillProjects"""
		self.projects_cmb.clear()
		projects = prj.projects( self.serverPath )
		self.projects_cmb.addItems( projects )
	
	def fillSections(self):
		"""get sections from project"""
		self.catLayout.clear()
		poseManPath = self.selectedProject.path + '/poseMan/'
		if not os.path.exists( poseManPath ):
			return []
		sections = [ a for a in os.listdir( poseManPath ) if os.path.isdir( poseManPath + a )]
		for s in sections:
			grid = flowlayout.FlowLayout()
			self.fillPoses( s, grid )
			wid = QtGui.QWidget()
			wid.setLayout( grid )
			self.catLayout.addItem( s, wid, False )

	def fillPoses(self, section, sectionWidget):
		"""fill poses for section"""
		poseManPath = self.selectedProject.path + '/poseMan/' + section
		poses = [ Pose( self.selectedProject, section, a.replace( '.pose', '' ) ) for a in os.listdir( poseManPath ) if a.endswith( '.pose' ) ]
		for p in poses:
			poseUi = PoseThumbnailUi( p )
			poseUi.poseDeleted.connect( self.fillSections )
			poseUi.updateThumb.connect( lambda pose = p : self.newPose( pose ) )
			sectionWidget.addWidget( poseUi )

class Pose(object):
	NAMESPACE = ''
	"""handle pose information, saving and loading"""
	def __init__(self, project, section, name):
		self.project = project
		self.section = section
		self.name    = name
	
	def __str__(self):
		return str(self.__dict__)

	def __cmp__(self, other): 
		return self.__dict__ == other.__dict__

	@property
	def posePath(self):
		"""docstring for posePath"""
		return self.project.path + '/poseMan/' + self.section + '/' + self.name + '.pose'

	@property
	def poseThumbPath(self):
		"""docstring for poseThumbPath"""
		return self.project.path + '/poseMan/' + self.section + '/' + self.name + '.bmp'

	@property
	def controlsData(self):
		"""returns controls data from current pose"""
		objs = mn.ls( sl = True )
		data = {}
		for o in objs:
			data[ o ] = {}
			for a in o.listAttr( k = True ):
				data[ o ][ a ] = a.v
		return data

	def save(self):
		"""save pose file"""
		pickle.dump( self.controlsData, open( self.posePath, "wb" ) )

	@property
	def controlsDataFromFile(self):
		"""docstring for controlsDataFromFile"""
		data = pickle.load( open( self.posePath, "rb") )
		return data

	def load(self):
		"""docstring for load"""
		data = self.controlsDataFromFile
		for o in data.keys():
			if not o.exists:
				continue
			for a in data[o].keys():
				finalA = mn.NodeAttribute( mn.Node( Pose.NAMESPACE + o.name ), a.name  )
				if finalA.exists:
					finalA.v = data[o][a]

	@property
	def controls(self):
		"""return controls of pose"""
		data = pickle.load( open( self.posePath, "rb") )
		return mn.Nodes( [Pose.NAMESPACE + o.name for o in data.keys() if mn.Node( Pose.NAMESPACE + o.name ).exists] )

	def delete(self):
		"""docstring for delete"""
		fl.File( self.posePath ).delete()
		fl.File( self.poseThumbPath ).delete()

class NewSection(baseSec, fomSec):
	def __init__(self, project, parent  = uiH.getMayaWindow() ):
		if uiH.USEPYQT:
			super(baseSec, self).__init__(parent)
		else:
			super(NewSection, self).__init__(parent)
		self.setupUi(self)
		self.connect(self.buttonBox, QtCore.SIGNAL("accepted()"), self.create)
		self.project = project

	def create(self):
		"""docstring for create"""
		sectionName = str( self.asset_le.text() )
		poseManPath = self.project.path + '/poseMan/'
		if os.path.exists( poseManPath + sectionName ):
			QtGui.QDialog.reject(self)
		else:
			os.makedirs( poseManPath + sectionName )
			QtGui.QDialog.accept(self)
		

def main( project, section, pose ):
	"""use this to create project in maya"""
	if mc.window( 'PoseManUi', q = 1, ex = 1 ):
		mc.deleteUI( 'PoseManUi' )
	PyForm=PoseManUi(  )
	PyForm.show()
