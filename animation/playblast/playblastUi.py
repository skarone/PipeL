import os
import pipe.mayaFile.mayaFile as mfl
import pipe.file.file as fl
import general.ui.pySideHelper as uiH
try:
	import render.deadline.deadline as dl
except:
	pass
reload( dl )
reload( uiH )
uiH.set_qt_bindings()
from Qt import QtGui,QtCore

PYFILEDIR = os.path.dirname(os.path.abspath(__file__))

uifile = PYFILEDIR + '/playblast.ui'
fom, base = uiH.loadUiType( uifile )

INMAYA = False
try:
	import animation.playblast.playblast as plb
	reload(plb)
	import maya.cmds as mc
	INMAYA = True
	import render.renderOcc.renderOcc as renOcc
	reload( renOcc )
except:
	pass
INHOU = False
try:
	import general.houdini.utils as hut
	reload( hut )
	import pipe.houdiniFile.houdiniFile as hfl
	reload( hfl )
	INHOU = True
except:
	pass

import pipe.settings.settings as sti
reload( sti )
import pipe.project.project as prj
import pipe.mail.mail as ml
reload( ml )

class PlayblastUi(base,fom):
	"""manager ui class"""
	def __init__(self, parent = None ):
		if INMAYA:
			if uiH.USEPYQT:
				super(base, self).__init__(uiH.getMayaWindow())
			else:
				super(PlayblastUi, self).__init__(uiH.getMayaWindow())
		else:
			if uiH.USEPYQT:
				super(base, self).__init__(parent)
			else:
				super(PlayblastUi, self).__init__(parent)
		self.setupUi(self)
		self._makeConnections()
		self.setObjectName( 'PlayblastUi' )
		if INMAYA:
			dead = dl.Deadline()
			self.group_cmb.addItems( dead.groups )
			#set settings icon
			settIcon = QtGui.QIcon(  ':/cmdWndIcon.png' )
			self.settings_btn.setIcon(settIcon)

	def _makeConnections(self):
		"""docstring for _makeConnections"""
		self.connect( self.playblast_btn , QtCore.SIGNAL("clicked()") , self.playblast )
		self.connect( self.renderOcc_btn , QtCore.SIGNAL("clicked()") , self.renderOcc )
		self.connect( self.publish_btn , QtCore.SIGNAL("clicked()") , self.publish )
		self.connect( self.settings_btn , QtCore.SIGNAL("clicked()") , self.setRenderPath )

	def renderOcc(self):
		"""render occ for current camera"""
		renOcc.renderOcc( self.motionBlur_chb.isChecked(), str( self.group_cmb.currentText() ) )

	def playblast(self):
		"""docstring for playblast"""
		if INMAYA:
			plb.playblastCurrentFile()
		elif INHOU:
			hut.playblastCurrentFile()

	def publish(self):
		"""docstring for publish"""
		if INMAYA:
			fil = mfl.currentFile()
			if not fil:
				print 'Please Save File To create Playblast'
				return
			movFil = fl.File( fil.versionPath + fil.name + '_v' + str( fil.version ).zfill( 3 ) + '.mov' )
		elif INHOU:
			fil = hfl.currentFile()
			if not fil:
				print 'Please Save File To create Playblast'
				return
			movFil = fl.File( fil.versionPath + fil.name + '_v' + str( fil.version ).zfill( 3 ) + '.mov' )
		if movFil.exists:
			movFil.copy( fil.dirPath + fil.name + '.mov' )
			settings = sti.Settings()
			gen = settings.General
			if gen:
				self.sendMail = gen[ "sendmail" ]
				self.mailServer = gen[ "mailserver" ]
				self.mailPort = gen[ "mailport" ]
				self.mailsPath = gen[ "departmentspath" ]
				AssOrShot = prj.shotOrAssetFromFile( movFil )
				ml.mailFromTool( 'new_playblast',
					{ '<ProjectName>': AssOrShot.project.name,
					'<SequenceName>': AssOrShot.sequence.name,
					'<ShotName>': AssOrShot.name,
					'<UserName>': os.getenv('username'),
					'<Path>':fil.dirPath + fil.name + '.mov'},
					os.getenv('username') + '@bitt.com',
					self.mailsPath , self.mailServer, self.mailPort  )


	def setRenderPath(self):
		"""docstring for setRenderPath"""
		renderPath = 'R:/'
		settings = sti.Settings()
		gen = settings.General
		if gen:
			renderPath = gen[ "renderpath" ]
			if not renderPath.endswith( '/' ):
				renderPath += '/'
		if gen.has_key( 'greypath' ):
			basePath = '<RenderPath>/' + gen[ "greypath" ]
		else:
			basePath =  '<RenderPath>/<project>' + '/' + '<sequence>' + '/' + '<shot>' + '/Grey/' + '<RenderLayerVersion>' + '/Grey'
		text, ok = QtGui.QInputDialog.getText(self, 'Render Path', 'Set Render Path', QtGui.QLineEdit.Normal, basePath )
		if ok:
			settings.write( 'General', 'greypath', text.replace( '<RenderPath>/', '' ) )


def main():
	try:
		if mc.window( 'PlayblastUi', q = 1, ex = 1 ):
			mc.deleteUI( 'PlayblastUi' )
	except:
		pass
	global PyForm
	PyForm=PlayblastUi(parent=QtGui.QApplication.activeWindow())
	PyForm.show()
