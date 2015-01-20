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

uifile = PYFILEDIR + '/poseThumbnailUi.ui'
fom, base = uiH.loadUiType( uifile )

class PoseThumbnailUi(base, fom):
	def __init__(self, projectName, parent  = uiH.getMayaWindow() ):
		if uiH.USEPYQT:
			super(base, self).__init__(parent)
		else:
			super(PoseThumbnailUi, self).__init__(parent)
		self.setupUi(self)
		self.projectName = projectName
		self.executer = mc.modelPanel( mbv = False, camera = 'Capture_Pose')
		mc.modelEditor(self.executer, e = True, grid = 0, da = "smoothShaded", allObjects = 0, nurbsSurfaces = 1, polymeshes = 1, subdivSurfaces = 1 )
		self.viewport_lay.addWidget( uiH.toQtObject( self.executer ) )
		self.setObjectName( 'PoseThumbnailUi' )
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
		else:
			self.saveCameraPreset = 1
			self.readWriteCameraPreset_btn.setText( '<< Write' )

	def cameraPreset(self, cameraNumber):
		"""set or save camera preset on corresponding number"""
		if self.saveCameraPreset:# save camera preset for current button
			pass
		else: #read camera preset for current button
			pass

	def createPose(self):
		"""docstring for createPose"""
		pass



def main():
	"""use this to create project in maya"""
	if mc.window( 'PoseThumbnailUi', q = 1, ex = 1 ):
		mc.deleteUI( 'PoseThumbnailUi' )
	PyForm=PoseThumbnailUi()
	PyForm.show()
