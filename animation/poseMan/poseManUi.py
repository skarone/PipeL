import os
import general.ui.pySideHelper as uiH
reload( uiH )
uiH.set_qt_bindings()
from Qt import QtGui,QtCore

import maya.cmds as mc

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


class PoseThumbnailCreatorUi(base, fom):
	def __init__(self, projectName, parent  = uiH.getMayaWindow() ):
		if uiH.USEPYQT:
			super(base, self).__init__(parent)
		else:
			super(PoseThumbnailCreatorUi, self).__init__(parent)
		self.setupUi(self)
		self.projectName = projectName
		self.executer = mc.modelPanel( mbv = False, camera = 'Capture_Pose')
		mc.modelEditor(self.executer, e = True, grid = 0, da = "smoothShaded", allObjects = 0, nurbsSurfaces = 1, polymeshes = 1, subdivSurfaces = 1 )
		self.viewport_lay.addWidget( uiH.toQtObject( self.executer ) )
		self.setObjectName( 'PoseThumbnailCreatorUi' )
		self._makeConnections()
		self.saveCameraPreset = 0 #READ, 1.. WRITE
		self.fillSections()

	def _makeConnections(self):
		"""create connections for UI"""
		self.connect( self.cameraPreset_1_btn, QtCore.SIGNAL("clicked()") , lambda cameraNumber = 1 : self.cameraPreset( cameraNumber ) )
		self.connect( self.cameraPreset_2_btn, QtCore.SIGNAL("clicked()") , lambda cameraNumber = 2 : self.cameraPreset( cameraNumber ) )
		self.connect( self.cameraPreset_3_btn, QtCore.SIGNAL("clicked()") , lambda cameraNumber = 3 : self.cameraPreset( cameraNumber ) )
		self.connect( self.cameraPreset_4_btn, QtCore.SIGNAL("clicked()") , lambda cameraNumber = 4 : self.cameraPreset( cameraNumber ) )
		self.connect( self.cameraPreset_5_btn, QtCore.SIGNAL("clicked()") , lambda cameraNumber = 5 : self.cameraPreset( cameraNumber ) )
		self.connect( self.readWriteCameraPreset_btn, QtCore.SIGNAL("clicked()") , self.changeCameraPresetsButtonSystem )
		self.connect( self.createPose_btn, QtCore.SIGNAL("clicked()") , self.createPose )

	def fillSections(self):
		"""docstring for fillSections"""
		pass

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

	def cameraPreset(self, cameraNumber):
		"""set or save camera preset on corresponding number"""
		if self.saveCameraPreset:# save camera preset for current button
			pass
		else: #read camera preset for current button
			pass

	def createPose(self):
		"""docstring for createPose"""
		pass

	def saveThumbnail(self):
		"""save current Thumbnail"""
		pass

class PoseThumbnailUi(baseThum, fomThum):
	def __init__(self, project, section, pose, parent  = uiH.getMayaWindow() ):
		if uiH.USEPYQT:
			super(baseThum, self).__init__(parent)
		else:
			super(PoseThumbnailUi, self).__init__(parent)
		self.setupUi(self)
		self.project = project
		self.section = section
		self.pose    = pose
		self.setContextMenuPolicy(QtCore.Qt.CustomContextMenu)
		self.customContextMenuRequested.connect(self.showMenu)
		self.pose_btn.setText( self.pose )
		self.setObjectName( 'PoseThumbnailUi' )
		myIcon = QtGui.QIcon( 'D:/dasdsasd.jpg' )
		self.pose_btn.setIcon(myIcon)

	def applyPose(self):
		"""docstring for self.applyPose"""
		print 'asdasdsada'

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
		print 'in selectControlsProperties'
		pass
		
	def deletePoseProperties(self):
		"""docstring for deletePoseProperties"""
		print 'in deletePoseProperties'
		pass

	def sliderPoseProperties(self):
		"""docstring for sliderPoseProperties"""
		print 'in sliderPoseProperties'
		pass

	def updatePoseProperties(self):
		"""docstring for updatePoseProperties"""
		print 'in updatePoseProperties'
		pass

	def updateThumbProperties(self):
		"""docstring for upda"""
		print 'in updateThumbProperties'
		pass

class PoseManUi(baseBase, fomBase):
	def __init__(self, project, section, pose, parent  = uiH.getMayaWindow() ):
		if uiH.USEPYQT:
			super(baseBase, self).__init__(parent)
		else:
			super(PoseManUi, self).__init__(parent)
		self.setupUi(self)
		self.setObjectName( 'PoseManUi' )


def main( project, section, pose ):
	"""use this to create project in maya"""
	if mc.window( 'PoseThumbnailUi', q = 1, ex = 1 ):
		mc.deleteUI( 'PoseThumbnailUi' )
	PyForm=PoseThumbnailUi( project, section, pose )
	PyForm.show()
