from __future__ import division

"""
	New features
	-Move pose, copy/paste pose, duplicate section/group
	-hacer renders con las poses, usando coordenadas guardadas de la poseManCam. Seria 1 set la pose y 2 render y asi con todas
	-Hacer que funcionen los presets de camara en el create new pose
"""

"""
	New name convention

	tab = section
	frame inside tab = group (was subsection)
	
	
	todo:
	que el renamepose obtenga el layout desde la etiqueta no desde el propio nombre del layout, porque este no coincidira si se ha hecho un rename section o rename subsection
	con lo que hay que cambiar la def getPoseFrameLayout
	
	Duplicate seccion/group/pose
	
"""

"""
	
	PoseMan v2. The Pose Manager for Maya.
	
	Created by Francis Vega (c) 2010
	francis.vega@inartx.com

	Description:
	Tool to manage character poses

	Install:
	Use:

	Contact
	hisconer@gmail.com

	Web
	http://www.inartx.com/poseman/
	
"""
	
# maya mel module
import maya.cmds as cmds
import maya.mel as mel

# standar python modules
from functools import partial
import string
import os
import sys
import math
import xml.dom.minidom
import re
import shutil

# custom modules
# import PoseMan_XML as pmxml

# python settings
# sys.dont_write_bytecode = True
		
# ------------------
# PoseMan Main Class
# ------------------
class PoseMan_UI():
	def __init__(self, projectPath="", thumbSize="small"):
		"""
		Main PoseMan Class
		Global vars and main UI PoseMan Layouts
		
		Two ways to create a new PoseMan Class:		
		1 - Just opening an empty PoseMan UI
		UI = PoseMan_UI()
		
		2 - Opening PoseMan UI and one project passing the path of project file
		UI = PoseMan_UI("/film/shot1/characters/Boody")
		
		"""
		
		# DEBUGGING
		print "Welcome to PoseMan 2 beta"
		
		# project path to open a project with a new PoseMan Class instance
		self.projectPath = projectPath
		
		# ---------------
		# PoseMan Globals
		# ---------------		
		self.poseManUI = {}
		self.PoseManMenu = {}
		self.groupFrameLayoutHeights = {}
		self.poseConfigFile = "poses.xml"
		self.sectionConfigFile = "sections.xml"
		self.subSectionConfigFile = "sections.xml"
		self.defaultSubSectionName = "Default"
		self.defaultSectionName = "Default"
		self.subSectionsDic = {}
		
		# thumbnails management
		self.poseSize = {}
		self.poseSize["small"] = (80, 80, "small")
		self.poseSize["medium"] = (160, 160, "medium")
		self.poseSize["large"] = (320, 320, "large")
		
		self.poseThumbnailSize = self.poseSize[thumbSize]
		
		# set temporal size		
		
		# Sections, Groups and Pose Dict
		self.LYT = {}
		
		# namespace
		self.charNamespace = ""
		self.namespaces = {}
		self.namespaces.clear()
		
		# cameras
		self.camList = []
		
		self.poseManPoseExtension = ".pose"
		self.poseManCharacterExtension = ".char"
		self.poseManImageExtension = ".png"
		self.projectExtension = ".pman"
		self.poseManVersion = "2 (beta)"
	
		# PoseMan msgs english/spanish
		self.ERROR_poseNameExist_es = "Ya existe una pose con ese nombre"
		self.ERROR_poseNameExist = "Pose name exists"
		self.ERROR_poseNamaNotValid_es = "The name can't contain special characters"
		self.ERROR_poseNamaNotValid = "Pose name"
		
		# msg code: 001
		self.WARNING_selectAtLeastOneObject = "Create new pose: Selecciona al menos un objeto"
		
		# palette colors
		self.bgcRed 		= (1.0, 0.0, 0.0)
		self.bgcGreen		= (0.0, 1.0, 0.0)
		self.bgcBlue		= (0.0, 0.0, 1.0)
		
		# --------------------
		# PoseMan Maya Layouts
		# --------------------
		
		# Main Window
		self.poseManUI["poseManWin"] = cmds.window(title="PoseMan "+self.poseManVersion, menuBar=True, tlc=[0,0])
		cmds.showWindow(self.poseManUI["poseManWin"])
		
		
		# Main Layout
		self.poseManUI["mainForm"] = cmds.formLayout()
		
		# Main Top Layout
		# rowColumnLayout with 3 rows
		# 1 = logo,
		# 2 = action icons / buttons
		# 3 = tab (section) layout
		self.poseManUI["topInfo"] = cmds.rowColumnLayout(numberOfRows=3)
		
		cmds.separator(style="in", p=self.poseManUI["topInfo"]) ###
		
		# 1
		# poseMan logo
		
		""" project logo """
		"""
		self.poseManUI["poseManLogo"] = cmds.gridLayout(nr=1, nc=1, cwh=(640,186))
		self.poseManLogo = cmds.image(p=self.poseManUI["poseManLogo"], i="C:/Users/francis/Documents/My Dropbox/Poseman/Characters/HEAVY/logo.png")
		"""

		""" poseman (default) logo """
		self.poseManUI["poseManLogo"] = cmds.gridLayout(nr=1, nc=1, cwh=(300,60))
		#self.poseManLogo = cmds.image(p=self.poseManUI["poseManLogo"], i="C:/Users/francis/Documents/My Dropbox/Poseman/PMLogo.png")
		self.poseManLogo = cmds.image(p=self.poseManUI["poseManLogo"], i="PMLogo.png")

		
		# 2
		# actions icons
		self.poseManUI["actionButtons"] = cmds.rowColumnLayout(
			nc=15,
			cw=[(1,10),(2,25),(3,25),(4,10),(5,25),(6,25),(7,25),(8,10),(9,30),(10,160),(11,110),(12,10),(13,25),(14,25),(15,25)],
			cs=[(1,5),(2,2),(3,2),(4,5),(5,2),(6,2),(7,2),(8,5),(9,2),(10,5),(11,10),(12,10),(13,2),(14,2),(15,2)],			
			p=self.poseManUI["topInfo"]
		)
		
		# cmds.button(w=40, label="New", c=self.createNewCharacterFileBrowser)
		self.poseManUI["ob"]						= cmds.iconTextButton	(en=0, i="openBar")
		self.poseManUI["createNewProjectITB"]		= cmds.iconTextButton	(en=1, i="fileNew",				c=self.createNewProjectWindow)
		self.poseManUI["openProjectITB"]			= cmds.iconTextButton	(en=1, i="fileOpen",			c=self.openNewProjectWindow)
		
		self.poseManUI["cb"]						= cmds.iconTextButton	(en=0, i="closeBar")
		
		self.poseManUI["createNewSectionITB"]		= cmds.iconTextButton	(en=0, i="publishAttributes",	c=self.createNewSection_UI)
		self.poseManUI["createNewSubSectionITB"]	= cmds.iconTextButton	(en=0, i="layerEditor",			c=self.createNewSubSection_UI)	
		self.poseManUI["createNewPoseITB"]			= cmds.iconTextButton	(en=0, i="newShelf",			c=self.createNewPoseWindow)
		
		self.poseManUI["cb"]						= cmds.iconTextButton	(en=0, i="closeBar")
		
		self.poseManUI["getNamespaceFromSelection"] = cmds.iconTextButton	(en=0, i="colorPickIcon",		c=self.learnNamespace)	
		self.poseManUI["sectionNamespaceTF"]		= cmds.textField		(en=0, width=100, text="")
		self.poseManUI["setNamespaceBTN"]			= cmds.button			(en=0, label="Set Namespace",	c=self.setSectionNamespace)
		self.poseManUI["ob"]						= cmds.iconTextButton	(en=0, i="openBar")
		
		self.poseManUI["thumbSizeSmall"]			= cmds.button			(en=0, l="S",					c=partial(self.setThumbSize,"small"))
		self.poseManUI["thumbSizeMedium"]			= cmds.button			(en=0, l="M",					c=partial(self.setThumbSize,"medium"))
		self.poseManUI["thumbSizeLarge"]			= cmds.button			(en=0, l="L",					c=partial(self.setThumbSize,"large"))
		
		# 3
		# main tabs
		
		self.poseManUI["mainTabs"] = cmds.tabLayout(p=self.poseManUI["mainForm"], cc=self.refreshTabInfo)
		
		"""
		cmds.popupMenu()
		cmds.menuItem(label="Delete Section", c=self.deleteSection)
		cmds.menuItem(label="Rename Section", c=self.renameSection)
		#cmds.menuItem(label="Duplicate section", c=self.duplicateSectionUI)
		"""
			
		# layouting
		cmds.formLayout(
			self.poseManUI["mainForm"], e=True,
			attachForm=[
				(self.poseManUI["topInfo"], 'top', 0),
				(self.poseManUI["topInfo"], 'left', 0),
				(self.poseManUI["topInfo"], 'right', 0),
							
				(self.poseManUI["mainTabs"], 'bottom', 0),				
				(self.poseManUI["mainTabs"], 'left', 0),			
				(self.poseManUI["mainTabs"], 'right', 0)				
			], 
			attachControl=[
				(self.poseManUI["mainTabs"], 'top', 0, self.poseManUI["topInfo"])
			]			
		)
		
		# show up the window!
		cmds.showWindow(self.poseManUI["poseManWin"])		
		
		# poseman menus
		self.PoseManMenu["File"] = cmds.menu(label="File", tearOff=False, en=True)
		# cmds.menuItem(label="New Project...", c=self.createNewCharacterFileBrowser)
		cmds.menuItem(label="New Project...", c=self.createNewProjectWindow)
		cmds.menuItem(label="Open Project...", c=self.openNewProjectWindow)
		
		self.PoseManMenu["Edit"] = cmds.menu(en=1, label="Edit", tearOff=False)
		cmds.menuItem(label="Make shelfbuton project", c=self.projectToShelf)
		
		self.PoseManMenu["Modify"] = cmds.menu(en=0, label="Modify", tearOff=False)
		
		self.PoseManMenu["Sections"] = cmds.menu(en=0, label="Sections", tearOff=False)
		cmds.menuItem(label="New...", c=self.createNewSection_UI)
		cmds.menuItem(label="Delete current...", c=self.deleteSection)
		#cmds.menuItem(label="Rename current...", c=self.renameSection_UI)
		
		self.PoseManMenu["Groups"] = cmds.menu(en=0, label="Groups", tearOff=False)
		cmds.menuItem(label="New...", c=self.createNewSubSection_UI)

		self.PoseManMenu["Poses"] = cmds.menu(en=0, label="Poses", tearOff=False)
		cmds.menuItem(label="New...", c=self.createNewPoseWindow)

		cmds.window(self.poseManUI["poseManWin"], e=True)
		
		# temporal character loading
		"""
		if cmds.about(windows=True):
			self.openNewProject("C:/Users/francis/Documents/My Dropbox/Poseman/Characters/Kubes/Kubes.pman", "large")
		else:
			self.openNewProject("/Users/Francis/Dropbox/Poseman/Characters/Kubes/Kubes.pman", "large")
		"""
		
		# preload a project
		if self.projectPath != "":
			self.openNewProject(self.projectPath)

	# ------------
	# GENERAL DEFS
	# ------------
	
	def setThumbSize(self, thumbSize, *args):
		# obtenemos la seccion actual
		currentSectionLabel = self.getCurrentActiveSection()		
				
		# guardamos todas las seccionesa
		allLabels = cmds.tabLayout(self.poseManUI["mainTabs"], q=1, tl=1)
		# calculamos cual sera el indice para el sti
		index = allLabels.index(currentSectionLabel)+1
		
		# cargamos de nuevo el proyecto
		self.openNewProject(self.characterFilePath, thumbSize)
		
		# seleccionamos la seccion que estaba seleccionada antes de hacer el openNewProject
		cmds.tabLayout(self.poseManUI["mainTabs"], e=1, sti=index)
		
	
	def sayUI(self, ui, *args):
		print ui
		
	def projectToShelf(self, *args):
		"""
		Create a shelf button to open PoseMan UI and a current project together
		"""
		self.pyScriptToShelf(self.projectName, ("import PoseMan as pm\nreload(pm)\npmui = pm.PoseMan_UI(\"" + self.characterFilePath + "\")"))
	
	# -------------
	# PROJECTS DEFS
	# -------------
	
	# -------------
	# SECTIONS DEFS
	# -------------

	def copyTree(self, origen, destino, *args):
		# copyTree ("C:/Users/francis.vega/Dropbox/Poseman/Characters/Kubes2/_ORDEN_" , "C:/Users/francis.vega/Dropbox/Poseman/Characters/Kubes2/PEPIOTE")
		
		# primero creamos el directorio base
		try:
			os.mkdir(destino)
		except:
			pass
		
		hijos = os.listdir(origen)
		
		if len(hijos) > 0:			
			onlyDirs = []
			for i in hijos:
				if len(i.split(".")) < 2:
					os.mkdir(destino + "/" + str(i))
					onlyDirs.append(i)
				else:
					shutil.copy(origen + "/" + str(i), destino + "/" + str(i))
					
			for dir in onlyDirs:
				self.copyTree(origen + "/" + dir, destino + "/" + dir)
				
	def duplicateSection(self, sectionName, newSectionName, *args):
		# copy section tree
		# update xml of sections
		# add new section to UI
		activeSection = self.getCurrentActiveSection()
		
		newSectionName = self.getValidStringName(newSectionName)
		
		origen = self.characterDirectoryPath + "/" + sectionName
		destino = self.characterDirectoryPath + "/" + newSectionName
		
		# self.copyTree(origen, destino)
		shutil.copytree(origen, destino)
		self.addSectionToConfFile_noCreateDirectory(newSectionName)		
		self.loadSections([newSectionName], [""])

	def duplicateGroup(self, sectionName, groupName, newGroupName, *args):
		# copy section tree
		# update xml of sections
		# add new section to UI
		activeSection = self.getCurrentActiveSection()
		
		newGroupName = self.getValidStringName(newGroupName)
		
		origen = self.characterDirectoryPath + "/" + sectionName + "/" + groupName
		destino = self.characterDirectoryPath + "/" + sectionName + "/" + newGroupName
		
		# self.copyTree(origen, destino)
		shutil.copytree(origen, destino)
		#self.addSectionToConfFile_noCreateDirectory(newSectionName)
		# DEBUG
		
		
	def deleteSection(self, *args):
		"""
		Delete a section from UI, section config file and HD (rename to .deleted)
		"""

		# Obtenemos el nombre de la seccion actual, la que vamos a borrar
		activeSection = self.getCurrentActiveSection()
		
		# Pedimos confirmacion
		confirm = cmds.confirmDialog( title='Delete Section', message="Delete Section " + activeSection + "?", button=['Yes','No'], defaultButton='Yes', cancelButton='No', dismissString='No' )

		if confirm == "Yes":
			
			# Deleting from UI
			cmds.deleteUI(self.poseManUI["mainTabs"]+"|"+activeSection)
			
			# Deleteing from XML
			self.removeSectionFromConfigFile(activeSection)
			
			# delete (renaming to .deleted)
			# self.renameSectionToDeleted(activeSection)
			srcSectionDirectory = self.characterDirectoryPath + "/" + activeSection
			dstSectionDirectory = self.characterDirectoryPath + "/" + activeSection + ".deleted"
			
			# rename to .delete
			# os.rename(srcSectionDirectory, dstSectionDirectory)
			
			# real delete
			shutil.rmtree(srcSectionDirectory)

	def renameSection(self, *args):
		"""
		Rename a section from UI, section config file and HD
		"""
		
		activeSection = self.getCurrentActiveSection()
		print activeSection
		

			
	def duplicateSectionUI(self, *args):
		"""
		duplica una seccion
		"""
		if cmds.window("duplicateSectionWindow", exists=True):
			cmds.deleteUI("duplicateSectionWindow", window=True)
			
		self.poseManUI["duplicateSectionWindow"] = cmds.window("duplicateSectionWindow", t="Duplicate Section")
		cmds.frameLayout(mh=5,mw=5,bv=0,lv=0)
		cmds.rowColumnLayout(numberOfRows=3)
		
		cmds.frameLayout(mh=10,mw=10,bv=0,lv=0)
		cmds.text(align="left", label="Enter section name")
		
		self.poseManUI["textFieldSectionName"] = cmds.textField(bgc=(0.7, 0.7, 0.8))
		cmds.setFocus(self.poseManUI["textFieldSectionName"])
		cmds.rowColumnLayout(cat=(1, "right", 1), numberOfColumns=2)
		cmds.button(l="Rename", c=partial(self.duplicateSection))
		cmds.button(l="Cancel", c=partial(self.deleteMyUI, self.poseManUI["duplicateSectionWindow"]))
		
		cmds.showWindow(self.poseManUI["duplicateSectionWindow"])
		cmds.window(self.poseManUI["duplicateSectionWindow"], e=1, w=300, h=100)	
		
	def refreshTabInfo(self, *args):
		"""
		Update section namespace info updating textfield
		"""
		# get current section
		activeSection = self.getCurrentActiveSection()
		
		# set textField with namespaceInfo
		if len(activeSection) > 0:
			sectionNamespace = self.namespaces[activeSection]
		else: 
			sectionNamespace = ""
		cmds.textField(self.poseManUI["sectionNamespaceTF"], e=1, text=sectionNamespace)


	# ----------------------------
	# SUB-SECTIONS DEFS AKA GROUPS
	# ----------------------------
	def deleteSubSection(self, sectionName, subSectionName, *args):
		"""
		Delete a subsection from UI, section config file and HD (rename to .deleted)
		"""		
		confirm = cmds.confirmDialog( title='Delete Group', message="Delete Group " + subSectionName + "?", button=['Yes','No'], defaultButton='Yes', cancelButton='No', dismissString='No' )

		if confirm == "Yes":
			# from ui
			scrollL = cmds.formLayout(self.poseManUI["mainTabs"] + "|" + sectionName, q=1, ca=1)[1]
			
			subSectionLayout = self.getSubSectionFrameLayout(sectionName, subSectionName)
			
			cmds.deleteUI(subSectionLayout)
			# from xml
			self.removeSubSectionFromConfigFile(sectionName, subSectionName)
			# delete (renaming to .deleted)
			# self.renameSectionToDeleted(sectionName)
			srcSectionDirectory = self.characterDirectoryPath + "/" + sectionName + "/" + subSectionName
			dstSectionDirectory = self.characterDirectoryPath + "/" + sectionName + "/" + subSectionName + ".deleted"
			
			# rename to .delete
			# os.rename(srcSectionDirectory, dstSectionDirectory)
			
			# real delete
			shutil.rmtree(srcSectionDirectory)

	def renameSubSectionUI(self, sectionName, subSectionName, poseName, *args):
		"""
		Rename a group UI Window
		"""
		if cmds.window("renameSubSectionWindow", exists=True):
			cmds.deleteUI("renameSubSectionWindow", window=True)
			
		self.poseManUI["renameSubSectionWindow"] = cmds.window("renameSubSectionWindow", t="Rename Group")
		cmds.frameLayout(mh=5,mw=5,bv=0,lv=0)
		cmds.rowColumnLayout(numberOfRows=3)
		
		cmds.frameLayout(mh=10,mw=10,bv=0,lv=0)
		cmds.text(align="left", label="Enter new Group name for " + subSectionName)
		
		self.poseManUI["textFieldSubSectionName"] = cmds.textField(text=subSectionName, bgc=(0.7, 0.7, 0.8))
		cmds.setFocus(self.poseManUI["textFieldSubSectionName"])
		cmds.rowColumnLayout(cat=(1, "right", 1), numberOfColumns=2)
		cmds.button(l="Rename", c=partial(self.renameSubSection, sectionName, subSectionName))
		cmds.button(l="Cancel", c=partial(self.deleteMyUI, self.poseManUI["renameSubSectionWindow"]))
		
		cmds.showWindow(self.poseManUI["renameSubSectionWindow"])
		cmds.window(self.poseManUI["renameSubSectionWindow"], e=1, w=300, h=100)	
		
		
	def renameSubSection(self, sectionName, subSectionName, *args):
		"""
		Renombra una subseccion (grupo)
		"""
		
		layout = self.getSubSectionFrameLayout(sectionName, subSectionName)
		
		# Obtenemos el nombr del directorio actual de la subseccion
		srcDirectory = self.characterDirectoryPath + "/" + sectionName + "/" + subSectionName
		
		# Obtenemos el nuevo nombre desde el textField
		newSubSectionName = cmds.textField(self.poseManUI["textFieldSubSectionName"], q=1, text=1)
		newSubSectionName = self.spacesToDown(newSubSectionName)
		
		# Construimos el nuevo directorio
		dstDirectory = self.characterDirectoryPath + "/" + sectionName + "/" + newSubSectionName
		
		# Obtenemos una lista de todas las poses que hay en la subsection
		
		# comprobamos si la nueva subSeccion ya existe
		if self.subSectionExists(sectionName, newSubSectionName) == False:
			
			# rename direcoty (sub section)
			os.rename(srcDirectory, dstDirectory)			
			
			# update group layout from UI
			self.renameUISubSection(sectionName, subSectionName, newSubSectionName)
			
			# update group conf file
			self.renameSubSectionInSubSectionConfFile(sectionName, subSectionName, newSubSectionName)
			
			# actualizamos en todas las poses los comandos POP-UP
			# actualizamos en todos los grupos los comandos POP-UP
			# Esto hay que hacerlo porque en el comando va la direccion del archivo de pose y como hemos
			# renombrado el directorio habra que cambiar la direccion, ya sea para asignar pose, renombrar pose o renombrar grupo, etc..
			
			# self.setNewSubSectionInPoses(sectionName, subSectionName, newSubSectionName)
			
			# self.updateSectionPupUp(sectionName, newSectionName)
			self.updateSubSectionPupUp(layout, sectionName, newSubSectionName)
			self.updatePosesPupUp(layout, sectionName, newSubSectionName) 
			
			# close rename window
			self.deleteMyUI(self.poseManUI["renameSubSectionWindow"])
			
			
		else:
			print "RENAME, there is a group with this name"
			
			
	def updateSubSectionPupUp(self, layout, sectionName, newSubSectionName):
		popMenu = cmds.frameLayout(layout, q=1, pma=1)
		listaOpciones = cmds.popupMenu(popMenu[-1], q=1, ia=1)
		cmds.menuItem(listaOpciones[0],  e=1, c=partial(self.deleteSubSection, sectionName, newSubSectionName))
		cmds.menuItem(listaOpciones[1],  e=1, c=partial(self.renameSubSectionUI, sectionName, newSubSectionName))

	def updatePosesPupUp(self, layout, sectionName, newSubSectionName):
		poseList = self.getPosesFromSubsection(sectionName, newSubSectionName)
		popMenu = cmds.frameLayout(layout, q=1, pma=1)[:-1]
		
		i = 0
		for menu in popMenu:
			listaOpciones = cmds.popupMenu(menu, q=1, ia=1)
		
			cmds.menuItem(listaOpciones[11], e=1, c=partial(self.renamePoseUI,				sectionName, newSubSectionName, poseList[i]))
				
			cmds.menuItem(listaOpciones[0],  e=1, c=partial(self.sliderMix, 				sectionName, newSubSectionName, poseList[i]))		
			
			cmds.menuItem(listaOpciones[2],  e=1, c="")
			cmds.menuItem(listaOpciones[3],  e=1, c=partial(self.addSelectedControls,		sectionName, newSubSectionName, poseList[i]))
			cmds.menuItem(listaOpciones[4],  e=1, c=partial(self.removeSelectedControls,	sectionName, newSubSectionName, poseList[i]))
			cmds.menuItem(listaOpciones[5],  e=1, c=partial(self.selectPoseControls, 		sectionName, newSubSectionName, poseList[i]))
			
			cmds.menuItem(listaOpciones[7],  e=1, c="")
			cmds.menuItem(listaOpciones[8],  e=1, c=partial(self.editPose,			 		sectionName, newSubSectionName, poseList[i]))
			
			cmds.menuItem(listaOpciones[11], e=1, c=partial(self.renamePoseUI,				sectionName, newSubSectionName, poseList[i]))
			cmds.menuItem(listaOpciones[12], e=1, c=partial(self.deletePose,				sectionName, newSubSectionName, poseList[i]))			
				
			# asignamos nuevos commands al iconTextButton para asignar la nueva pose renombrada
			poseButton = self.getPoseIconTextButton(sectionName, newSubSectionName, poseList[i])
			cmds.iconTextButton(poseButton, e=1, c=partial(self.setPose, sectionName, newSubSectionName, poseList[i]))
		
			textLayout = self.getPoseTextLayout(sectionName, newSubSectionName, poseList[i])
			cmds.text(textLayout, e=1, l=poseList[i])
		
			i = i + 1
		
	def setNewSubSectionInPoses(self, sectionName, subSectionName, newSectionName):
		""" cambia el comando de un boton de pose """
		
		poseNames = []
		poseName = self.getPosesFromSubsection
		
		poseFrame = self.getPoseFrameLayout(sectionName, subSectionName, poseName)
		
		opoupMenu = cmds.frameLayout(poseFrame, q=1, pma=1)
		
		
		"""
		listaOpciones = cmds.popupMenu(opoupMenu, q=1, ia=1)
				
		cmds.menuItem(listaOpciones[0],  e=1, c=partial(self.sliderMix, 				sectionName, subSectionName, newPoseName))		
		
		cmds.menuItem(listaOpciones[2],  e=1, c="")
		cmds.menuItem(listaOpciones[3],  e=1, c=partial(self.addSelectedControls,		sectionName, subSectionName, newPoseName))
		cmds.menuItem(listaOpciones[4],  e=1, c=partial(self.removeSelectedControls,	sectionName, subSectionName, newPoseName))
		cmds.menuItem(listaOpciones[5],  e=1, c=partial(self.selectPoseControls, 		sectionName, subSectionName, newPoseName))
		
		cmds.menuItem(listaOpciones[7],  e=1, c="")
		cmds.menuItem(listaOpciones[8],  e=1, c=partial(self.editPose,			 		sectionName, subSectionName, newPoseName))
		
		cmds.menuItem(listaOpciones[11], e=1, c=partial(self.renamePoseUI,				sectionName, subSectionName, newPoseName))
		cmds.menuItem(listaOpciones[12], e=1, c=partial(self.deletePose,				sectionName, subSectionName, newPoseName))
		
		# asignamos nuevos commands al iconTextButton para asignar la nueva pose renombrada
		poseButton = self.getPoseIconTextButton(sectionName, subSectionName, poseName)
		cmds.iconTextButton(poseButton, e=1, c=partial(self.setPose, sectionName, subSectionName, newPoseName))
	
		textLayout = self.getPoseTextLayout(sectionName, subSectionName, poseName)
		cmds.text(textLayout, e=1, l=newPoseName)
		"""
		
	def renameUISubSection(self, sectionName, subSectionName, newSubSectionName):
	
		"""
		rename de textfield of a pose in poseman ui
		"""
		# obtenemos el frameLayout para asignar nuevos comandos a su popmenu y al propio label del frameLayout
		subSectionFrame = self.getSubSectionFrameLayout(sectionName, subSectionName)
		
		# cambiamos el label del framelayout
		cmds.frameLayout(subSectionFrame, e=1, label=newSubSectionName)
		
		"""
		aqui deberemos cambiar el subsection de cada pose, para que al asignar se dirigan a un directorio correcto
		"""

	# debug
	def getSubSectionFrameLayout_DEBUG(self, sectionName, subSectionName):
		"""
		obtenemos el framelayout de la subseccion/grupo
		"""		
		poseScrollLayout = cmds.formLayout(self.poseManUI["mainTabs"] + "|" + sectionName, q=1, ca=1)[1]
				
		grupoFrameLayout = cmds.scrollLayout(poseScrollLayout, q=1, ca=1)
		groupFrameLayout = None
    
		for FL in grupoFrameLayout:
			frameLayoutLabel = cmds.frameLayout(FL, q=1, label=1)
			if frameLayoutLabel == subSectionName:
				groupFrameLayout = poseScrollLayout + "|" + FL
				break
            
		return groupFrameLayout
		
	def getSubSectionFrameLayout(self, sectionName, subSectionName):
		poseScrollLayout = cmds.formLayout(self.poseManUI["mainTabs"] + "|" + sectionName, q=1, ca=1)[1]
		grupoFrameLayout = cmds.scrollLayout(poseScrollLayout, q=1, ca=1)
		grupoFrameLayout = [self.poseManUI["mainTabs"] + "|" + sectionName + "|" + poseScrollLayout + "|" + f for f in grupoFrameLayout]

		for frmLyt in grupoFrameLayout:
			label = cmds.frameLayout(frmLyt, q=1, label=1)
			if label == subSectionName:
				subSectionFrameLayout = frmLyt
				break
			
		return subSectionFrameLayout
	
	def renameSubSectionInPoseConfFile(self, sectionName, subSectionName, newSubSectionName):
		"""
		rename a group from xml group config file
		"""
		xmlFile = self.characterDirectoryPath + "/" + sectionName + "/" + self.subSectionConfigFile
		xmlDoc = xml.dom.minidom.parse(xmlFile)

		mainSubSectionNode = xmlDoc.getElementsByTagName("sections")[0]
		subSections = xmlDoc.getElementsByTagName("section")

		# primero miramos si ya existe esa pose
		yaexiste = 0
		for section in sections:
			attrName = pose.getAttribute("name")
			if attrName == newSubSectionName:
				print "There is a group with this name " + newSubSectionName + " in XML file"
				yaexiste = 1
				break

		if yaexiste == False:
			encontrado = False
			for section in sections:
				attrName = pose.getAttribute("name")
				if attrName == subSectionName:
					encontrado = True
					section.setAttribute("name", newSubSectionName)

			if encontrado:
				f = open(xmlFile, "w")
				f.write(xmlDoc.toxml())
				f.close()
			else:
				print "There isn't group with name " + subSectionName
									
	def subSectionExists(self, sectionName, subSectionName, *args):
		"""
		Check if group directory exists
		"""
		
		exists = False
		xmlFile = self.characterDirectoryPath + "/" + sectionName + "/" + subSectionName + "/" + self.sectionConfigFile
		xmlDoc = xml.dom.minidom.parse(xmlFile)
		
		sectionsNode = xmlDoc.getElementsByTagName("section")
			
		for section in sectionsNode:
			if pose.getAttribute("name") == subSectionName:
				exists = True
				break
		
		return exists
	
	# ----------
	# POSES DEFS
	# ----------		
	def getCurrentActiveSection(self):
		currentTab = cmds.tabLayout(self.poseManUI["mainTabs"], q=1, st=1)
		return currentTab

	def getCurrentActiveSectionNew(self):
		currentTab = cmds.tabLayout(self.poseManUI["mainTabs"], q=1, st=1)	
		selectedTabIndex = cmds.tabLayout(self.poseManUI["mainTabs"], q=1, sti=1)	
		allTabNames = cmds.tabLayout(self.poseManUI["mainTabs"], q=1, tl=1)	
		selectedTab = allTabNames[selectedTabIndex-1]
		
		return selectedTab
		
	def getCurrentActiveIDSection(self):
		currentTab = cmds.tabLayout(self.poseManUI["mainTabs"], q=1, sti=1)
		return currentTab
		
	def setSectionNamespace(self, *args):
		# get current section
		activeSection = self.getCurrentActiveSection()
		
		namespaceText = cmds.textField(self.poseManUI["sectionNamespaceTF"], q=1, text=1)
		splitNamespaces = namespaceText.split(",")
		
		cleanNamespaces = []
		for section in splitNamespaces:
			if len(section) > 0:
				# cleanNamespaces.append(re.sub("\W", "", section))
				cleanNamespaces.append(self.getValidStringName(section))				

		# anadimos una coma
		namespaceswithcoma = ""
		for i in range(len(cleanNamespaces)):
			if i < len(cleanNamespaces)-1:
				namespaceswithcoma = namespaceswithcoma + cleanNamespaces[i] + ","
			else:
				namespaceswithcoma = namespaceswithcoma + cleanNamespaces[i] + ""
				break
			
		cmds.textField(self.poseManUI["sectionNamespaceTF"], e=1, text=namespaceswithcoma)
		
		# set namespace into namespace dict
		self.namespaces[activeSection] = namespaceswithcoma
		
		# write namespace info into project xml file
		xmlFile = self.characterFilePath
		xmlDoc = xml.dom.minidom.parse(xmlFile)
			
		mainSectionsNode = xmlDoc.getElementsByTagName("sections")[0]
		sections = xmlDoc.getElementsByTagName("section")
		
		for section in sections:
			attrName = section.getAttribute("name")
			if attrName == activeSection:
				section.setAttribute("namespace", namespaceswithcoma)
				break

		# write file
		f = open(xmlFile, "w")
		f.write(xmlDoc.toxml())
		f.close()
	
	def setSectionNamespace2(self, *args):
		# get current section
		activeSection = self.getCurrentActiveSection()
		
		# get namespace text
		# posibles formatos:
		# 0 "" (vacio)
		# 1 ns1
		# 2 ns1, ns2, ns3
		# 3 ns1:, ns2
		# 4 ns1:, ns2:, ns3:
		# ...
		
		namespaceText = cmds.textField(self.poseManUI["sectionNamespaceTF"], q=1, text=1)
		
		if namespaceText.partition(" ")[0] != "":
			# create a list for multiple or single ns
			textFieldNamespaces = namespaceText.split(",")
			# put ":" if not
			for i in range(len(textFieldNamespaces)):
				if textFieldNamespaces[i][-1] != ":":
					textFieldNamespaces[i] = str(textFieldNamespaces[i]) + ":"
			
			# rewrite namespace text correctly formated with ":"		
			stringNamespacesToTextField = ""
			for i in range(len(textFieldNamespaces)):
				stringNamespacesToTextField += textFieldNamespaces[i] + ", "
			
			stringNamespacesToTextField = stringNamespacesToTextField[:-2]
			cmds.textField(self.poseManUI["sectionNamespaceTF"], e=1, text=stringNamespacesToTextField)
		else:
			stringNamespacesToTextField = ""

		# set namespace into namespace dict
		self.namespaces[activeSection] = stringNamespacesToTextField
		
		# write namespace info into project xml file		
		xmlFile = self.characterFilePath
		xmlDoc = xml.dom.minidom.parse(xmlFile)
			
		mainSectionsNode = xmlDoc.getElementsByTagName("sections")[0]
		sections = xmlDoc.getElementsByTagName("section")
		
		for section in sections:
			attrName = section.getAttribute("name")
			if attrName == activeSection:
				section.setAttribute("namespace", stringNamespacesToTextField)
				break

		# write file
		f = open(xmlFile, "w")
		f.write(xmlDoc.toxml())
		f.close()
		
	def createNewPoseWindow(self, *args):
		"""
		UI for new pose
		"""		
		# object list
		objList = cmds.ls(l=1, sl=1)
		
		"""
		# temporal camera name
		poseManCameraName = "PoseMan_Camera"

		# if poseman camera doesn't exists, create one
		if cmds.objExists(poseManCameraName) == 0:
			self.poseManCamera = cmds.camera(n=poseManCameraName)
			cmds.viewSet(self.poseManCamera[0], p=1)
			cmds.setAttr(self.poseManCamera[0] + ".focalLength", 100)
			cmds.setAttr(self.poseManCamera[0] + ".visibility", 0)
		"""
		# borramos todas las cameras de poseman
		if len(self.camList) > 0:
			cmds.delete(self.camList)
			self.camList = []
		
		self.poseManCamera = cmds.camera(n="PoseManCaptureCam")
		self.camList.append(self.poseManCamera[0])
		cmds.viewSet(self.poseManCamera[0], p=1)
		cmds.setAttr(self.poseManCamera[0] + ".focalLength", 100)
		cmds.setAttr(self.poseManCamera[0] + ".visibility", 0)
			
		# delete window if exists
		if cmds.window("capturePoseWindow", exists=1):
			cmds.deleteUI("capturePoseWindow", window=1)

		# main window
		self.poseManUI["capturePose"] = cmds.window("capturePoseWindow")
		
		# FrameLayout
		FL = cmds.frameLayout(mh=5,mw=5,bv=0,lv=0)
		# RowColumnLayout with 6 rows
		# 1 = capture viewport
		# 2 = camera pre-set buttons
		# 3 = section selection
		# 4 = subsection selection
		# 5 = enter pose name
		# 6 = create, apply and cancel button
		RL = cmds.rowColumnLayout(p=FL, nr=6, w=300)	
		
		# 1
		cmds.paneLayout("myPane", p=RL, w=300, h=350)
		self.capturePoseModelPanel=cmds.modelPanel(mbv=0, camera=self.poseManCamera[0])
		cmds.modelEditor(self.capturePoseModelPanel, e=1, grid=0, da="smoothShaded")
		cmds.modelEditor(self.capturePoseModelPanel, e=1, allObjects=0)
		cmds.modelEditor(self.capturePoseModelPanel, e=1, nurbsSurfaces=1)
		cmds.modelEditor(self.capturePoseModelPanel, e=1, polymeshes=1)
		cmds.modelEditor(self.capturePoseModelPanel, e=1, subdivSurfaces=1)

		# 2
		cmds.frameLayout(mh=5,mw=0,bv=0,lv=0, p=RL)
		cmds.rowColumnLayout(nc=5)
		cmds.button(l="CamSet 1", bgc=(0.43, 0.63, 0.43), w=10,h=20)
		cmds.button(l="CamSet 2", bgc=(0.43, 0.63, 0.43), w=10,h=20)
		cmds.button(l="CamSet 3", bgc=(0.43, 0.63, 0.43), w=10,h=20)
		cmds.button(l="CamSet 4", bgc=(0.43, 0.63, 0.43), w=10,h=20)
		cmds.button(l="CamSet 5", bgc=(0.43, 0.63, 0.43), w=10,h=20)
		
		# 3
		cmds.frameLayout(mh=5,mw=0,bv=0,lv=0, p=RL)
		cmds.rowColumnLayout(nr=2)
		cmds.text(align="left", label="Section")
		self.poseManUI["optionSection"] = cmds.optionMenu(cc=partial(self.refreshSectionAndSubsectionOptionMenu))
		
		for section in self.getSections():
			cmds.menuItem(label=section)

		# 4
		cmds.frameLayout(mh=5,mw=0,bv=0,lv=0, p=RL)
		cmds.rowColumnLayout(nr=2)
		cmds.text(align="left", label="Sub Section")
		self.poseManUI["optionSubSection"] = cmds.optionMenu()
		currentSectionSelected = cmds.optionMenu(self.poseManUI["optionSection"], q=1, v=1)
		
		for section in self.getSubSections(currentSectionSelected):
			cmds.menuItem(label=section)
			
		# 5
		cmds.frameLayout(mh=5,mw=0,bv=0,lv=0, p=RL)
		cmds.rowColumnLayout(nr=3)
		cmds.text(align="left", label="Enter pose name:")		
		self.poseManUI["poseNameTextField"] = cmds.textField()
		
		# 6
		cmds.frameLayout(mh=5,mw=0,bv=0,lv=0, p=RL)
		cmds.rowColumnLayout(nc=3)
		cmds.button(label="Create", c=partial(self.createNewPose, 1))
		cmds.button(label="Apply", c=partial(self.createNewPose, 0))
		cmds.button(label="Cancel", c=partial(self.deleteMyUI, "capturePoseWindow"))
		
		# show up window!
		cmds.window("capturePoseWindow", e=1, rtf=0, t="New Pose", w=345, h=490)		
		cmds.showWindow("capturePoseWindow")

		# re-selection pose object list
		if len(objList) > 0:
			cmds.select(objList)
			
		# focus capture viewport and textField
		cmds.setFocus(self.capturePoseModelPanel)
		cmds.setFocus(self.poseManUI["poseNameTextField"])
		
		# select the actual section and the first sub-section
		currentSelectedTab = cmds.tabLayout(self.poseManUI["mainTabs"], q=1, sti=1)
		cmds.optionMenu(self.poseManUI["optionSection"], e=1, sl=currentSelectedTab)
		self.refreshSectionAndSubsectionOptionMenu()
		
	def refreshSectionAndSubsectionOptionMenu(self, *args):
		"""
		
		"""
		# la seccion por defecto es la que este seleccionada en el optionMenu
		self.currentSection = cmds.optionMenu(self.poseManUI["optionSection"], q=1, v=1)
		
		# con la seccion por defecto obtenemos las subsecciones y rellenamos el optionmenu
		# pero primero debemos vaciarlo
		
		# vaciado
		childs = cmds.optionMenu(self.poseManUI["optionSubSection"], q=1, ils=1)
		for child in childs:
			cmds.deleteUI(child)

		# llenado
		for section in self.getSubSections(self.currentSection):
			cmds.menuItem(p=self.poseManUI["optionSubSection"], label=section)
	
	def createNewPose(self, deleteUI, *args):
		"""
		Def to create a new pose
		Create a pose at UI, modify config file, create a pose file and pose image
		"""
		# object List
		objList = cmds.ls(l=1, sl=1)
		
		if len(objList) > 0:
			# obtenemos la seccion y la subseccion donde ira la pose
			sectionName = cmds.optionMenu(self.poseManUI["optionSection"], q=1, v=1)
			subSectionName = cmds.optionMenu(self.poseManUI["optionSubSection"], q=1, v=1)
			
			# obtenemos el nombre de la pose
			poseName = cmds.textField(self.poseManUI["poseNameTextField"], q=1, text=1)
			#poseName = self.spacesToDown(poseName)
			
			# poseName_tmp = re.sub("\W", "_", poseName)
			poseName = self.getValidStringName(poseName)
			
			# comprobamos si ya existe, si no, proseguimos
			# debug new pose
			if self.poseExists(sectionName, subSectionName, poseName) == False:
				formL = self.poseManUI["mainTabs"] + "|" + sectionName
				scrollL = cmds.formLayout(formL, q=1, ca=1)[1]
				subSectionLayout = self.getSubSectionFrameLayout(sectionName, subSectionName)				
				gridL = cmds.frameLayout(subSectionLayout, q=1, ca=1)[0]				
				
				# gridL = cmds.scrollLayout(scrollL, q=1, ca=1)[0]
				# subSectionsFrames = cmds.scrollLayout(scrollL, q=1, ca=1)[0]
				
				# escribimos el archivo de configuracion				
				self.addPoseToConfFile(sectionName, subSectionName, poseName)
				
				# escribimos el archivo de la pose
				self.writePoseFile(sectionName, subSectionName, poseName)
				
				# escribimos el archivo png de la pose
				# self.writeImagePoseFile(sectionName, subSectionName, poseName)			
				self.writeImagePoseFileBuffer(sectionName, subSectionName, poseName)
				
				# anadimos el thumbnail frameLayout(rowColumnLayour(iconTextButton,text)) a la interfaz
				self.addSinglePoseToUI(sectionName, subSectionName, poseName, gridL)
			
				# delete create pose window ui
				if deleteUI:
					self.deleteMyUI("capturePoseWindow")
					# borramos todas las cameras de poseman
					if len(self.camList) > 0:
						cmds.delete(self.camList)
						self.camList = []
				
			else:
				# msg code: 002
				cmds.warning(self.ERROR_poseNameExist)
		else:
			# msg code: 001
			cmds.warning(self.WARNING_selectAtLeastOneObject)
		
	def poseExists(self, sectionName, subSectionName, poseName, *args):
		"""
		Check if file pose exists
		"""
		exists = False
		xmlFile = self.characterDirectoryPath + "/" + sectionName + "/" + subSectionName + "/" + self.poseConfigFile
		xmlDoc = xml.dom.minidom.parse(xmlFile)
		
		posesNode = xmlDoc.getElementsByTagName("pose")
			
		for pose in posesNode:
			if pose.getAttribute("name") == poseName:
				exists = True
				break
		
		return exists
			
	def renamePoseUI(self, sectionName, subSectionName, poseName, *args):
		"""
		
		"""
		if cmds.window("renamePoseWindow", exists=True):
			cmds.deleteUI("renamePoseWindow", window=True)
			
		self.poseManUI["renamePoseWindow"] = cmds.window("renamePoseWindow", t="Rename pose")
		cmds.frameLayout(mh=5,mw=5,bv=0,lv=0)
		cmds.rowColumnLayout(numberOfRows=3)
		
		cmds.frameLayout(mh=10,mw=10,bv=0,lv=0)
		cmds.text(align="left", label="Enter new pose name for " + poseName)
		
		self.poseManUI["textFieldPoseName"] = cmds.textField(text=poseName, bgc=(0.7, 0.7, 0.8))
		cmds.setFocus(self.poseManUI["textFieldPoseName"])
		cmds.rowColumnLayout(cat=(1, "right", 1), numberOfColumns=2)
		cmds.button(l="Rename", c=partial(self.renamePose, sectionName, subSectionName, poseName))	
		cmds.button(l="Cancel", c=partial(self.deleteMyUI, self.poseManUI["renamePoseWindow"]))
		
		cmds.showWindow(self.poseManUI["renamePoseWindow"])
		cmds.window(self.poseManUI["renamePoseWindow"], e=1, w=300, h=100)		
	
	def renamePose(self, sectionName, subSectionName, poseName, *args):
		"""
		Rename a pose. File, image, config xml, etc..
		"""
		
		# get file names
		srcDirectory = self.characterDirectoryPath + "/" + sectionName + "/" + subSectionName
		srcPoseFilePath = self.characterDirectoryPath + "/" + sectionName + "/" + subSectionName + "/" + poseName + ".pose"
		# srcImageFilePath = self.characterDirectoryPath + "/" + sectionName + "/" + subSectionName + "/" + "thumbs" + "/" + self.poseThumbnailSize[2] + "/" + poseName + ".png"
		srcImageFilePath_s = self.characterDirectoryPath + "/" + sectionName + "/" + subSectionName + "/" + "thumbs" + "/" + "small" + "/" + poseName + ".png"
		srcImageFilePath_m = self.characterDirectoryPath + "/" + sectionName + "/" + subSectionName + "/" + "thumbs" + "/" + "medium" + "/" + poseName + ".png"
		srcImageFilePath_l = self.characterDirectoryPath + "/" + sectionName + "/" + subSectionName + "/" + "thumbs" + "/" + "large" + "/" + poseName + ".png"
		
		newPoseName = cmds.textField(self.poseManUI["textFieldPoseName"], q=1, text=1)		
		newPoseName = self.getValidStringName(newPoseName)		
		

		# comprobamos si la nueva pose ya existe
		if not self.poseExists(sectionName, subSectionName, newPoseName):
			dstPoseFilePath = srcDirectory + "/" + newPoseName + ".pose"
			dstImageFilePath_s = srcDirectory + "/" + "thumbs" + "/" + "small" + "/" + newPoseName + ".png"
			dstImageFilePath_m = srcDirectory + "/" + "thumbs" + "/" + "medium" + "/" + newPoseName + ".png"
			dstImageFilePath_l = srcDirectory + "/" + "thumbs" + "/" + "large" + "/" + newPoseName + ".png"

			# rename pose and image files to new name
			os.rename(srcPoseFilePath, dstPoseFilePath)
			os.rename(srcImageFilePath_s, dstImageFilePath_s)
			os.rename(srcImageFilePath_m, dstImageFilePath_m)
			os.rename(srcImageFilePath_l, dstImageFilePath_l)
			
			# update pose layout from UI
			self.renameUIPose(sectionName, subSectionName, poseName, newPoseName)
			
			# update pose conf file
			self.renamePoseInPoseConfFile(sectionName, subSectionName, poseName, newPoseName)

			# close rename window
			self.deleteMyUI(self.poseManUI["renamePoseWindow"])
		else:
			print "RENAME, there is a pose with this name"

			
	def renameUIPose(self, sectionName, subSectionName, poseName, newPoseName):
		"""
		rename de textfield of a pose in poseman ui
		"""
		# obtenemos el frameLayout para asignar nuevos comandos a su popmenu
		
		poseFrame = self.getPoseFrameLayout(sectionName, subSectionName, poseName)
		
		opoupMenu = cmds.frameLayout(poseFrame, q=1, pma=1)
		# 00 = mix pose slider
		# 01 = divider
		# 02 = update all controls
		# 03 = add selected controls
		# 04 = remove selected controls from pose
		# 05 = select controls pose
		# 06 = divider
		# 07 = override controls
		# 08 = edit pose
		# 09 = divider
		# 10 = move to
		# 11 = rename pose
		# 12 = delete pose	
		# 11 = renamePose
		
		listaOpciones = cmds.popupMenu(opoupMenu, q=1, ia=1)
		
		cmds.menuItem(listaOpciones[0],  e=1, c=partial(self.sliderMix, 				sectionName, subSectionName, newPoseName))		
		
		cmds.menuItem(listaOpciones[2],  e=1, c="")
		cmds.menuItem(listaOpciones[3],  e=1, c=partial(self.addSelectedControls,		sectionName, subSectionName, newPoseName))
		cmds.menuItem(listaOpciones[4],  e=1, c=partial(self.removeSelectedControls,	sectionName, subSectionName, newPoseName))
		cmds.menuItem(listaOpciones[5],  e=1, c=partial(self.selectPoseControls, 		sectionName, subSectionName, newPoseName))
		
		cmds.menuItem(listaOpciones[7],  e=1, c="")
		cmds.menuItem(listaOpciones[8],  e=1, c=partial(self.editPose,			 		sectionName, subSectionName, newPoseName))
		
		cmds.menuItem(listaOpciones[11], e=1, c=partial(self.renamePoseUI,				sectionName, subSectionName, newPoseName))
		cmds.menuItem(listaOpciones[12], e=1, c=partial(self.deletePose,				sectionName, subSectionName, newPoseName))
		
		# asignamos nuevos commands al iconTextButton para asignar la nueva pose renombrada
		poseButton = self.getPoseIconTextButton(sectionName, subSectionName, poseName)
		cmds.iconTextButton(poseButton, e=1, c=partial(self.setPose, sectionName, subSectionName, newPoseName))
	
		textLayout = self.getPoseTextLayout(sectionName, subSectionName, poseName)
		cmds.text(textLayout, e=1, l=newPoseName)

	def setPosePopUps(self, sectionName, subSectionName, poseName, newPoseName):
			"""
			rename de textfield of a pose in poseman ui
			"""
			# obtenemos el frameLayout para asignar nuevos comandos a su popmenu
			
			poseFrame = self.getPoseFrameLayout(sectionName, subSectionName, poseName)
			
			opoupMenu = cmds.frameLayout(poseFrame, q=1, pma=1)
			# 00 = mix pose slider
			# 01 = divider
			# 02 = update all controls
			# 03 = add selected controls
			# 04 = remove selected controls from pose
			# 05 = select controls pose
			# 06 = divider
			# 07 = override controls
			# 08 = edit pose
			# 09 = divider
			# 10 = move to
			# 11 = rename pose
			# 12 = delete pose	
			# 11 = renamePose
			
			listaOpciones = cmds.popupMenu(opoupMenu, q=1, ia=1)
			
			cmds.menuItem(listaOpciones[0],  e=1, c=partial(self.sliderMix, 				sectionName, subSectionName, newPoseName))		
			
			cmds.menuItem(listaOpciones[2],  e=1, c="")
			cmds.menuItem(listaOpciones[3],  e=1, c=partial(self.addSelectedControls,		sectionName, subSectionName, newPoseName))
			cmds.menuItem(listaOpciones[4],  e=1, c=partial(self.removeSelectedControls,	sectionName, subSectionName, newPoseName))
			cmds.menuItem(listaOpciones[5],  e=1, c=partial(self.selectPoseControls, 		sectionName, subSectionName, newPoseName))
			
			cmds.menuItem(listaOpciones[7],  e=1, c="")
			cmds.menuItem(listaOpciones[8],  e=1, c=partial(self.editPose,			 		sectionName, subSectionName, newPoseName))
			
			cmds.menuItem(listaOpciones[11], e=1, c=partial(self.renamePoseUI,				sectionName, subSectionName, newPoseName))
			cmds.menuItem(listaOpciones[12], e=1, c=partial(self.deletePose,				sectionName, subSectionName, newPoseName))
			
			# asignamos nuevos commands al iconTextButton para asignar la nueva pose renombrada
			poseButton = self.getPoseIconTextButton(sectionName, subSectionName, poseName)
			cmds.iconTextButton(poseButton, e=1, c=partial(self.setPose, sectionName, subSectionName, newPoseName))
		
			textLayout = self.getPoseTextLayout(sectionName, subSectionName, poseName)
			cmds.text(textLayout, e=1, l=newPoseName)
		
	def renamePoseInPoseConfFile(self, sectionName, subSectionName, poseName, newPoseName):
		"""
		rename a pose from xml pose config file
		"""
		xmlFile = self.characterDirectoryPath + "/" + sectionName + "/" + subSectionName + "/" + self.poseConfigFile
		xmlDoc = xml.dom.minidom.parse(xmlFile)
		
		mainPoseNode = xmlDoc.getElementsByTagName("poses")[0]
		poses = xmlDoc.getElementsByTagName("pose")
		
		# primero miramos si ya existe esa pose
		yaexiste = 0
		for pose in poses:
			attrName = pose.getAttribute("name")
			if attrName == newPoseName:
				print "There is a pose with this name " + newPoseName
				yaexiste = 1
				break

		if yaexiste == False:
			encontrado = 0	
			for pose in poses:
				attrName = pose.getAttribute("name")
				if attrName == poseName:
					encontrado = 1
					pose.setAttribute("name", newPoseName)

			if encontrado:
				f = open(xmlFile, "w")
				f.write(xmlDoc.toxml())
				f.close()
			else:
				print "there isn't pose with name " + poseName	

	
	def renameSubSectionInSubSectionConfFile(self, sectionName, subSectionName, newSubSectionName):
		"""
		rename a subSection from xml subSection config file
		"""
		xmlFile = self.characterDirectoryPath + "/" + sectionName + "/" + self.subSectionConfigFile
		xmlDoc = xml.dom.minidom.parse(xmlFile)
		
		mainSubSectionNode = xmlDoc.getElementsByTagName("sections")[0]
		subSections = xmlDoc.getElementsByTagName("section")
		
		encontrado = 0
		for subSection in subSections:
			attrName = subSection.getAttribute("name")
			if attrName == subSectionName:
				encontrado = 1
				subSection.setAttribute("name", newSubSectionName)

		if encontrado:
			f = open(xmlFile, "w")
			f.write(xmlDoc.toxml())
			f.close()
		else:
			print "there isn't Group with name " + subSectionName

	def getPoseFrameLayout(self, sectionName, subSectionName, poseName):
		poseFrameLayout = ""
		subSectionLayout = ""
		
		poseScrollLayout = cmds.formLayout(self.poseManUI["mainTabs"] + "|" + sectionName, q=1, ca=1)[1]
		subSections = cmds.layout(poseScrollLayout, q=1, ca=1)
		fullPath = self.poseManUI["mainTabs"] + "|" + sectionName + "|" + poseScrollLayout

		for SS in subSections:
			label = cmds.frameLayout(fullPath + "|" + SS, q=1, label=1)
			if label == subSectionName:
				subSectionLayout = fullPath + "|" + SS
				break

		gridL = cmds.frameLayout(subSectionLayout, q=1, ca=1)[0]
		poseFramesLayout = cmds.gridLayout(gridL, q=1, ca=1)

		# ya tenemos el layout de la subseccion
		for PFL in poseFramesLayout:
			rowChild = cmds.frameLayout(PFL, q=1, ca=1)[0]
			poseTextField = cmds.rowColumnLayout(rowChild, q=1, ca=1)[1]
			poseTextName = cmds.text(poseTextField, q=1, l=1)

			if poseTextName == poseName:
				poseFrameLayout = PFL
		
		return poseFrameLayout
				
	def getPoseRowColumnLayout(self, sectionName, subSectionName, poseName):
		"""
		
		"""
		FL = self.getPoseFrameLayout(sectionName, subSectionName, poseName)
		rowColumnLayout = cmds.frameLayout(FL, q=1, ca=1)[0]
		
		return rowColumnLayout
	
	def getPoseIconTextButton(self, sectionName, subSectionName, poseName):
		"""
		
		"""
		RL = self.getPoseRowColumnLayout(sectionName, subSectionName, poseName)
		icon = cmds.rowColumnLayout(RL, q=1, ca=1)[0]
		
		return icon

	def getPoseTextLayout(self, sectionName, subSectionName, poseName):
		"""
		
		"""
		RL = self.getPoseRowColumnLayout(sectionName, subSectionName, poseName)
		textLayout = cmds.rowColumnLayout(RL, q=1, ca=1)[1]
		
		return textLayout
	
	def deletePose(self, sectionName, subSectionName, poseName, *args):
		"""
		
		"""
		
		confirm = cmds.confirmDialog( title='Delete Pose', message="Delete Pose " + poseName + "?", button=['Yes','No'], defaultButton='Yes', cancelButton='No', dismissString='No' )

		if confirm == "Yes":		
			# get file names
			xmlFile = self.characterDirectoryPath + "/" + sectionName + "/" + subSectionName + "/" + poseName + ".pose"
			imgFile_S = self.characterDirectoryPath + "/" + sectionName + "/" + subSectionName + "/" + "thumbs" + "/" + "small" + "/" + poseName + ".png"
			imgFile_M = self.characterDirectoryPath + "/" + sectionName + "/" + subSectionName + "/" + "thumbs" + "/" + "medium" + "/" + poseName + ".png"
			imgFile_L = self.characterDirectoryPath + "/" + sectionName + "/" + subSectionName + "/" + "thumbs" + "/" + "large" + "/" + poseName + ".png"
			
			# rename to .delete
			"""
			os.rename(xmlFile, xmlFile+".deleted")
			os.rename(imgFile_S, imgFile_S+".deleted")
			os.rename(imgFile_M, imgFile_M+".deleted")
			os.rename(imgFile_L, imgFile_L+".deleted")
			"""
			
			# real delete
			os.remove(xmlFile)
			os.remove(imgFile_S)
			os.remove(imgFile_M)
			os.remove(imgFile_L)
			
			# remove pose from pose configuration file
			self.removePoseFromFileConfig(sectionName, subSectionName, poseName)
			
			# remove pose layout from UI
			self.removePoseFromUI(sectionName, subSectionName, poseName)			
	
	def getSectionLayout(self, sectionName, *args):
		#debug
	
		poseScrollLayout = cmds.formLayout(self.poseManUI["mainTabs"] + "|" + sectionName, q=1, ca=1)[1]
		grupoFrameLayout = cmds.scrollLayout(poseScrollLayout, q=1, ca=1)
		grupoFrameLayout = [self.poseManUI["mainTabs"] + "|" + sectionName + "|" + poseScrollLayout + "|" + f for f in grupoFrameLayout]

		for frmLyt in grupoFrameLayout:
			label = cmds.frameLayout(frmLyt, q=1, label=1)
			if label == subSectionName:
				subSectionFrameLayout = frmLyt
				break
			
		return subSectionFrameLayout
		
		
	
	def removePoseFromUI(self, sectionName, subSectionName, poseName):
		"""
		Remove a pose widget from poseman UI
		
		"""
		scroll = cmds.formLayout(self.poseManUI["mainTabs"] + "|" + sectionName, q=1, ca=1)[1]
		grid = cmds.frameLayout(scroll + "|" + subSectionName, q=1, ca=1)
		poseFrames = cmds.gridLayout(grid, q=1, ca=1)		
		
		for PFL in poseFrames:
			rowChild = cmds.frameLayout(PFL, q=1, ca=1)[0]
			poseTextField = cmds.rowColumnLayout(rowChild, q=1, ca=1)[1]
			poseTextName = cmds.text(poseTextField, q=1, l=1)
			
			if poseTextName == poseName:				
				cmds.deleteUI(PFL)
		
	def removePoseFromFileConfig(self, sectionName, subSectionName,  poseName):
		"""
		remove a pose item from xml file config
		
		"""
		xmlFile = self.characterDirectoryPath + "/" + sectionName + "/" + subSectionName + "/" + self.poseConfigFile
		xmlDoc = xml.dom.minidom.parse(xmlFile)
			
		mainPoseNode = xmlDoc.getElementsByTagName("poses")[0]
		poses = xmlDoc.getElementsByTagName("pose")
		
		for pose in poses:
			attrName = pose.getAttribute("name")
			if attrName == poseName:
				mainPoseNode.removeChild(pose)				
				break

		# write file
		f = open(xmlFile, "w")
		f.write(xmlDoc.toxml())
		f.close()
		
	def removeSubSectionFromConfigFile(self, sectionName, subSectionName, *args):
		"""
		remove a sub section item from xml file config
		
		"""
		xmlFile = self.characterDirectoryPath + "/" + sectionName + "/" + self.sectionConfigFile
		xmlDoc = xml.dom.minidom.parse(xmlFile)
			
		mainSubSectionsNode = xmlDoc.getElementsByTagName("sections")[0]
		subSections = xmlDoc.getElementsByTagName("section")
		
		for subSection in subSections:
			attrName = subSection.getAttribute("name")
			if attrName == subSectionName:
				mainSubSectionsNode.removeChild(subSection)				
				break

		# write file
		f = open(xmlFile, "w")
		f.write(xmlDoc.toxml())
		f.close()	

		
	def removeSectionFromConfigFile(self, sectionName, *args):
		"""
		remove a section item from xml file config
		
		"""
		xmlFile = self.characterFilePath
		xmlDoc = xml.dom.minidom.parse(xmlFile)
			
		mainSectionsNode = xmlDoc.getElementsByTagName("sections")[0]
		sections = xmlDoc.getElementsByTagName("section")
		
		for section in sections:
			attrName = section.getAttribute("name")
			if attrName == sectionName:
				mainSectionsNode.removeChild(section)				
				break

		# write file
		f = open(xmlFile, "w")
		f.write(xmlDoc.toxml())
		f.close()		
	
	def _wroteImagePoseFileBuffer(self, sectionName, subSectionName, poseName, *args):
		import maya.OpenMaya as api
		import maya.OpenMayaUI as apiUI

		# set view with active viewport
		view = apiUI.M3dView.active3dView()

		image = api.MImage()
		view.readColorBuffer(image, True)

		image.resize(self.poseThumbnailSize[0], self.poseThumbnailSize[1], True)
		
		imagePoseFile = self.characterDirectoryPath + "/" + sectionName + "/" + subSectionName + "/" + "thumbs" + "/" + self.poseThumbnailSize[2] + "/" + poseName + ".png"

		image.writeToFile(imagePoseFile, "png")
		
	def writeImagePoseFileBuffer(self, sectionName, subSectionName, poseName, *args):		
		"""
		playblast a .png for thumbnail pose
		"""
		print sectionName, subSectionName, poseName
		
		cTime = cmds.currentTime(q=1)
		cmds.select(cl=1)
		cmds.setAttr("defaultRenderGlobals.imageFormat", 32)
		
		# 80 x 80
		imagePoseFile = self.characterDirectoryPath + "/" + sectionName + "/" + subSectionName + "/" + "thumbs" + "/" + "small" + "/" + poseName + ".png"		
		cmds.playblast(v=0, fr=cTime, w=80*2, h=80*2, orn=0, fmt="image", cf=imagePoseFile)

		# 160 x 160
		imagePoseFile = self.characterDirectoryPath + "/" + sectionName + "/" + subSectionName + "/" + "thumbs" + "/" + "medium" + "/" + poseName + ".png"		
		cmds.playblast(v=0, fr=cTime, w=160*2, h=160*2, orn=0, fmt="image", cf=imagePoseFile)

		# 320 x 320
		imagePoseFile = self.characterDirectoryPath + "/" + sectionName + "/" + subSectionName + "/" + "thumbs" + "/" + "large" + "/" + poseName + ".png"		
		cmds.playblast(v=0, fr=cTime, w=320*2, h=320*2, orn=0, fmt="image", cf=imagePoseFile)
				
	def addPoseToConfFile(self, sectionName, subSectionName, poseName, *args):
		"""
		add a pose item to xml config file
		"""
		xmlFile = self.characterDirectoryPath + "/" + sectionName + "/" + subSectionName + "/" + self.poseConfigFile
		xmlDoc = xml.dom.minidom.parse(xmlFile)	
		
		poses = xmlDoc.getElementsByTagName("poses")[0]
		
		newPoseNode = xmlDoc.createElement("pose")
		newAttr = xmlDoc.createAttribute("name")	
		newPoseNode.setAttributeNode(newAttr)
		newPoseNode.setAttribute("name", poseName)
		poses.appendChild(newPoseNode)
		
		f = open(xmlFile, "w")
		f.write(xmlDoc.toxml())
		f.close()
	
	def writePoseFile(self, sectionName, subSectionName, poseName, *args):
		"""
		write objects attribute data to a xml pose file
		"""		
		xmlFile = self.characterDirectoryPath + "/" + sectionName + "/" + subSectionName + "/" + poseName + ".pose"
	
		xmlPoseData = "<?xml version='1.0' encoding='iso-8859-1'?>\n"
		xmlPoseData += "<pose name=\"" + poseName + "\">\n"
		
		objects = cmds.ls(sl=1, l=1)		

		for i in range(len(objects)):
			keyAttrList = cmds.listAttr(objects[i], keyable=1, scalarAndArray=1, unlocked=True)
			
			objectNoWithoutNamespace = self.stripNamespace(objects[i])
			xmlPoseData += "\t<obj name=\"" + objectNoWithoutNamespace + "\">\n"
			for k in range(len(keyAttrList)):
				attrName = keyAttrList[k]
				attrValue = cmds.getAttr(objects[i]+"."+keyAttrList[k])
				
				# convert True = 1 and False = 0
				if attrValue == True:
					attrValue = 1
				elif attrValue == False:
					attrValue = 0
					
				mixValue = 1.0
				xmlPoseData += "\t\t<attr name=\"" + attrName + "\" value=\"" + str(attrValue) + "\" mix=\"" + str(mixValue) + "\" />\n"
			xmlPoseData += "\t</obj>\n"
		xmlPoseData +="</pose>"
		
		f = open(xmlFile, "w")
		f.write(xmlPoseData)
		f.close()
		
	
	def createNewCharacterFileBrowser(self, *args):
		"""
		open a file dialog to create a new proyect (Character)
		"""
		singleFilter = "*.*"
		returnFile = cmds.fileDialog2(cap="Save PoseMan Character", fileFilter=singleFilter, dialogStyle=2, fm=0, okc="Save")
		
		if returnFile != None:
			splitReturnFile = returnFile[0].rpartition("/")
			charDir = splitReturnFile[0]
			charFile = splitReturnFile[2]
			self.createNewCharacter(charDir, charFile)		
		else:
			print "do not nothing"
			
	def createNewCharacter(self, directory, projectName, *args):
		"""
		Create a new proyect directory/files structure
		"""
		
		# create project directory from data
		# directory = /Users/foo/characters/
		# projectName = nemo.pman
		# project directory = /Users/foo/characters/nemo/nemo.pman
		
		cleanProjectName = projectName[:-5]
		projectDir = directory + "/" + cleanProjectName

		# proyect directory
		os.makedirs(projectDir)		
		f = open(projectDir + "/" + projectName, "w")
		f.write("<?xml version='1.0' ?>\n<character icon='file.png' name='" + cleanProjectName + "' thumbSize='small'>\n\t<sections>\n\t\t<section name='Default'/>\n\t</sections></character>")
		
		# create default section
		os.makedirs(projectDir + "/" + "Default")		
		f = open(projectDir + "/" + "Default" + "/" + self.sectionConfigFile, "w")		
		f.write("<?xml version='1.0' ?>\n<sections>\n\t<section name='Default'/>\n</sections>")
		f.close()
		
		# create defaul sub-section
		os.makedirs(projectDir + "/" + "Default" + "/" + "Default")		
		f = open(projectDir + "/" + "Default" + "/" + "Default" + "/" + self.poseConfigFile, "w")
		f.write("<?xml version='1.0' ?>\n<poses>\n</poses>")
		f.close()

		# cargamos el nuevo personaje en poseman
		self.openNewProject(directory + "/" + cleanProjectName + "/" + projectName)
		
	def refreshGridWidth(self, *args):
		"""
		refresh all widgets to fit poses in new windows dimension
		"""
		windowWidth = cmds.window(self.poseManUI["poseManWin"], q=1, w=1)
		newWidth = windowWidth / 83
		
		formsLayouts = cmds.tabLayout(self.poseManUI["mainTabs"], q=1, ca=1) # moom, alice, froi
		for FL in formsLayouts:
			scrollsLayouts = cmds.formLayout(FL, q=1, ca=1)[1] # scroll001[1]
			framesLayouts = cmds.scrollLayout(scrollsLayouts, q=1, ca=1)
			for FL in framesLayouts:
				gridLayout = cmds.frameLayout(FL, q=1, ca=1)[0]
				cmds.gridLayout(gridLayout, e=1, nc=newWidth, cw=self.poseThumbnailSize[0], ch=self.poseThumbnailSize[0]+22, ag=1)

	def createNewSection_UI(self, *args):		
		"""
		
		"""
		if cmds.window("newSectionWindow", exists=True):
			cmds.deleteUI("newSectionWindow", window=True)
			
		self.poseManUI["newSectionWindow"] = cmds.window("newSectionWindow", t="New Section")
		cmds.frameLayout(mh=5,mw=5,bv=0,lv=0)
		cmds.rowColumnLayout(numberOfRows=3)
		
		cmds.frameLayout(mh=10,mw=10,bv=0,lv=0)
		cmds.text(align="left", label="Enter section name:")
		
		self.poseManUI["textFieldSectionName"] = cmds.textField()
		cmds.setFocus(self.poseManUI["textFieldSectionName"])
		
		cmds.rowColumnLayout(cat=(1, "right", 1), numberOfColumns=3)
		cmds.button(l="Create", c=(partial(self.createNewSection, 1)))
		cmds.button(l="Apply", c=partial(self.createNewSection, 0))
		cmds.button(l="Close", c=partial(self.deleteMyUI, self.poseManUI["newSectionWindow"]))
		
		cmds.showWindow(self.poseManUI["newSectionWindow"])
		cmds.window("newSectionWindow", e=1, w=300, h=100)
		
	def createNewSection(self, deleteUIWin, *args):
		"""
		Crea una nueva seccion (tab) con una subseccion por defecto "Default"
		"""
		# obtenemos el nombre de la seccion haciendo query al campo de text
		sectionName = cmds.textField(self.poseManUI["textFieldSectionName"], q=1, tx=1)
		# pasamos los espacios en blanco a "_"
		# sectionName = self.spacesToDown(sectionName)
		
		# sectionName_tmp = re.sub("\W", "_", sectionName)
		sectionName = self.getValidStringName(sectionName)		
		
		# first check if section already exist
		if self.sectionExists(sectionName) == False:
			# add section to section conf file
			self.addSectionToConfFile(sectionName)
			
			# add empty namespace to namespaces dic
			self.namespaces[sectionName] = ""

			# add section UI's to poseman window
			sectionToAdd = []
			sectionToAdd.append(sectionName)
			self.loadSections(sectionToAdd, [""])
			
			# delete win if press create
			if deleteUIWin:
				cmds.deleteUI(self.poseManUI["newSectionWindow"], wnd=True)
		else:
			cmds.warning("Section " + sectionName + " already exists")

	def createNewSubSection(self, deleteUIWin, *args):
		"""
		Create a new subsection into a active section
		"""
		sectionName = self.getCurrentActiveSection()

		# obtenemos el nombre de la seccion haciendo query al campo de text
		subSectionName = cmds.textField(self.poseManUI["textFieldSubSectionName"], q=1, tx=1)
		
		# pasamos los espacios en blanco a "_"
		subSectionName = self.getValidStringName(subSectionName)		
		
		# first check if section already exist
		if self.subSectionExists(sectionName, subSectionName) == False:
			# add section UI's to poseman window
			self.addSubSectionToUI(sectionName, subSectionName)			
		
			# add section to section conf file			
			self.addSubSectionToConfFile(sectionName, subSectionName)
			
			# delete win if press create
			if deleteUIWin:
				cmds.deleteUI(self.poseManUI["newSubSectionWindow"], wnd=True)
			
		else:
			cmds.warning("Sub section " + subSectionName + " already exists")
	
	def addSubSectionToConfFile(self, sectionName, subSectionName, *args):
		# getting characgter.poseman file to add new section xml node <section>
		xmlFile = self.characterDirectoryPath + "/" + sectionName + "/" + self.sectionConfigFile
		xmlDoc = xml.dom.minidom.parse(xmlFile)
		
		# main sections xml node <sections>
		section = xmlDoc.getElementsByTagName("sections")[0]
		
		# new section node <section>
		newSectionNode = xmlDoc.createElement("section")
		newAttr = xmlDoc.createAttribute("name")
		newSectionNode.setAttributeNode(newAttr)
		newSectionNode.setAttribute("name", subSectionName)
		section.appendChild(newSectionNode)
		
		# write xml file		
		f = open(xmlFile, "w")
		f.write(xmlDoc.toxml())
		f.close()
		
		# create sub section directory
		os.makedirs(self.characterDirectoryPath + "/" + sectionName + "/" + subSectionName)
		
		# create thumbs for group
		os.makedirs(self.characterDirectoryPath + "/" + sectionName + "/" + subSectionName + "/" + "thumbs")
		os.makedirs(self.characterDirectoryPath + "/" + sectionName + "/" + subSectionName + "/" + "thumbs" + "/" + "small")
		os.makedirs(self.characterDirectoryPath + "/" + sectionName + "/" + subSectionName + "/" + "thumbs" + "/" + "medium")
		os.makedirs(self.characterDirectoryPath + "/" + sectionName + "/" + subSectionName + "/" + "thumbs" + "/" + "large")
		
		# create poses.xml
		f = open(self.characterDirectoryPath + "/" + sectionName + "/" + subSectionName + "/" + self.poseConfigFile, "w")	
		f.write("<?xml version=\"1.0\" ?>\n<poses>\n</poses>")
		f.close()		

	def addSubSectionToUI(self, sectionName, subSectionName, *args):	
		sectionScrollLayout = cmds.formLayout(self.poseManUI["mainTabs"] + "|" + sectionName, q=1, ca=1)[1]
		newSectionFrameLayout = cmds.frameLayout(subSectionName, bgc=(0.2, 0.2, 0.25), bv=1, cll=1, cl=0, bs="in", lv=1, p=sectionScrollLayout)
		
		cmds.frameLayout(subSectionName, e=1,\
		collapseCommand=partial(self.collapse, newSectionFrameLayout),\
		expandCommand=partial(self.expand, newSectionFrameLayout),\
		preCollapseCommand=partial(self.precollapse, newSectionFrameLayout)\
		)
		
		cmds.popupMenu()
		# cmds.menuItem(label="Rename...")
		cmds.menuItem(label="Delete Group...", c=partial(self.deleteSubSection, sectionName, subSectionName))
		cmds.menuItem(label="Rename Group...", c=partial(self.renameSubSectionUI, sectionName, subSectionName))
		
		newSectionGridLayout = cmds.gridLayout(nc=cmds.window(self.poseManUI["poseManWin"], q=True, w=True) / (self.poseThumbnailSize[0]+2), cw=self.poseThumbnailSize[0], ch=(self.poseThumbnailSize[0]+22), ag=1,  aec=0, dpc=self.movePoseFromGroupToGroup)
	
	def createNewSubSection_UI(self, *args):
		"""
		Add new subsection
		"""
		if cmds.window("newSubSectionWindow", exists=True):
			cmds.deleteUI("newSubSectionWindow", window=True)
			
		self.poseManUI["newSubSectionWindow"] = cmds.window("newSubSectionWindow", t="New Group")
		cmds.frameLayout(mh=5,mw=5,bv=0,lv=0)
		cmds.rowColumnLayout(numberOfRows=3)
		
		cmds.frameLayout(mh=10,mw=10,bv=0,lv=0)
		cmds.text(align="left", label="Enter Group name:")
		
		self.poseManUI["textFieldSubSectionName"] = cmds.textField()
		cmds.setFocus(self.poseManUI["textFieldSubSectionName"])
		
		cmds.rowColumnLayout(cat=(1, "right", 1), numberOfColumns=3)
		cmds.button(l="Create", c=(partial(self.createNewSubSection, 1)))
		cmds.button(l="Apply", c=partial(self.createNewSubSection, 0))
		cmds.button(l="Close", c=partial(self.deleteMyUI, self.poseManUI["newSubSectionWindow"]))
		
		cmds.showWindow(self.poseManUI["newSubSectionWindow"])
		cmds.window("newSubSectionWindow", e=1, w=300, h=100)
	
	def subSectionExists(self, sectionName, subSectionName):
		exists = False
		xmlFile = self.characterDirectoryPath + "/" + sectionName + "/" + self.sectionConfigFile
		xmlDoc = xml.dom.minidom.parse(xmlFile)
		subSectionsNode = xmlDoc.getElementsByTagName("section")
		for subSection in subSectionsNode:
			if subSection.getAttribute("name") == subSectionName:
				exists = True
				break
		
		return exists		
		
	def addSectionToUI(self, sectionName):	
		newSectionFormLayout = cmds.formLayout(sectionName , p=self.poseManUI["mainTabs"])
		newSectionScrollLayout = cmds.scrollLayout(cr=1)
		newSectionFrameLayout = cmds.frameLayout("Default", bgc=(0.2, 0.2, 0.25),  bv=1, cll=1, cl=1, bs="in", lv=1, p=newSectionScrollLayout)
		
		newSectionGridLayout = cmds.gridLayout(nc=cmds.window(self.poseManUI["poseManWin"], q=True, w=True) / (self.poseThumbnailSize[0]+3), cr=0, ag=1, allowEmptyCells=0, cw=self.poseThumbnailSize[0], ch=self.poseThumbnailSize[0])

		cmds.formLayout(
				newSectionFormLayout, e=True,
				attachForm=[
					(newSectionScrollLayout, 'top', 1),
					(newSectionScrollLayout, 'left', 1),
					(newSectionScrollLayout, 'right', 1),
					(newSectionScrollLayout, 'bottom', 1)
				]
			)
		
	def addSectionToConfFile(self, sectionName):
		"""
		Anade una seccion al archivo de configuracion
		"""
		
		# getting characgter.poseman file to add new section xml node <section>
		xmlFile = self.characterFilePath
		xmlDoc = xml.dom.minidom.parse(xmlFile)
		
		# main sections xml node <sections>
		section = xmlDoc.getElementsByTagName("sections")[0]
		
		# new section node <section>
		newSectionNode = xmlDoc.createElement("section")
		newAttr = xmlDoc.createAttribute("name")
		newSectionNode.setAttributeNode(newAttr)
		newSectionNode.setAttribute("name", sectionName)
		newAttr = xmlDoc.createAttribute("namespace")
		newSectionNode.setAttributeNode(newAttr)
		newSectionNode.setAttribute("namespace", "")		
		section.appendChild(newSectionNode)
		
		# write xml file		
		f = open(xmlFile, "w")
		f.write(xmlDoc.toxml())
		f.close()
		
		# create section directory
		os.makedirs(self.characterDirectoryPath + "/" + sectionName)

		# create sections.xml
		f = open(self.characterDirectoryPath + "/" + sectionName + "/" + self.sectionConfigFile, "w")
		f.write("<?xml version=\"1.0\" ?>\n<sections>\t<section name=\"Default\" />\n\n</sections>")
		f.close()
		
		# create defatul subsection directory
		os.makedirs(self.characterDirectoryPath + "/" + sectionName + "/" + self.defaultSubSectionName)
		
		# create thumbnails directorys into defatul group
		os.makedirs(self.characterDirectoryPath + "/" + sectionName + "/" + self.defaultSubSectionName + "/" + "thumbs")
		os.makedirs(self.characterDirectoryPath + "/" + sectionName + "/" + self.defaultSubSectionName + "/" + "thumbs" + "/" + "small")
		os.makedirs(self.characterDirectoryPath + "/" + sectionName + "/" + self.defaultSubSectionName + "/" + "thumbs" + "/" + "medium")
		os.makedirs(self.characterDirectoryPath + "/" + sectionName + "/" + self.defaultSubSectionName + "/" + "thumbs" + "/" + "large")
		
		# create poses.xml
		f = open(self.characterDirectoryPath + "/" + sectionName + "/" + self.defaultSubSectionName + "/" + self.poseConfigFile, "w")	
		f.write("<?xml version=\"1.0\" ?>\n<poses>\n</poses>")
		f.close()

	def addSectionToConfFile_noCreateDirectory(self, sectionName):
		"""
		Anade una seccion al archivo de configuracion
		"""
		sectionName= self.getValidStringName(sectionName)
		
		# getting characgter.poseman file to add new section xml node <section>
		xmlFile = self.characterFilePath
		xmlDoc = xml.dom.minidom.parse(xmlFile)
		
		# main sections xml node <sections>
		section = xmlDoc.getElementsByTagName("sections")[0]
		
		# new section node <section>
		newSectionNode = xmlDoc.createElement("section")
		newAttr = xmlDoc.createAttribute("name")
		newSectionNode.setAttributeNode(newAttr)
		newSectionNode.setAttribute("name", sectionName)
		newAttr = xmlDoc.createAttribute("namespace")
		newSectionNode.setAttributeNode(newAttr)
		newSectionNode.setAttribute("namespace", "")		
		section.appendChild(newSectionNode)
		
		# write xml file		
		f = open(xmlFile, "w")
		f.write(xmlDoc.toxml())
		f.close()
		
	def addPMNodeToFile(self, xmlFile, nodeName, attrName, attrValue):
		# usamos esta def para anadir cualquier nodo a un archivo xml, ya sea un nodo pose o seccion
		pass
		
	def removePMNodeFromFile(self, xmlFile, nodeNAme):
		# def para eliminar un nodo de un xml, sea section o pose
		pass
		
	def deleteMyUI(self, UIname, *args):
		cmds.deleteUI(UIname)
		
	def openNewProject(self, characterFilePath, thumbSize="small"):
		"""
		Procedimiento para cargar un pesonaje en la UI de poseman
		a partir de un archivo .xml de personaje character.poseman
		"""
		
		# cambiamos el nombre de la ventana con el nombre del proyecto
		projectName = characterFilePath.split("/")[-1].split(".")[0]
		cmds.window(self.poseManUI["poseManWin"], e=1, title="PoseMan 2 (beta) | PROJECT NAME: " + projectName)
		
		# establecemos el tamano de las imagenes de pose
		self.poseThumbnailSize = self.poseSize[thumbSize]
		
		# activamos los controles relacionados con la carga de un character
		cmds.iconTextButton	(self.poseManUI["createNewSectionITB"],			e=1, en=1)
		cmds.iconTextButton	(self.poseManUI["createNewSubSectionITB"],		e=1, en=1)
		cmds.iconTextButton	(self.poseManUI["createNewPoseITB"],			e=1, en=1)
		
		cmds.iconTextButton	(self.poseManUI["getNamespaceFromSelection"],	e=1, en=1)
		cmds.textField		(self.poseManUI["sectionNamespaceTF"],			e=1, en=1)
		cmds.button			(self.poseManUI["setNamespaceBTN"],				e=1, en=1)
		
		# activamos los menus
		cmds.menu			(self.PoseManMenu["Sections"],					e=1, en=1)
		cmds.menu			(self.PoseManMenu["Groups"],					e=1, en=1)
		cmds.menu			(self.PoseManMenu["Poses"],						e=1, en=1)
		
		# activamos los botones de small, medium y large
		cmds.button			(self.poseManUI["thumbSizeSmall"],				e=1, en=1)
		cmds.button			(self.poseManUI["thumbSizeMedium"],				e=1, en=1)
		cmds.button			(self.poseManUI["thumbSizeLarge"],				e=1, en=1)

		# Lo primero reseteamos los namespaces
		self.namespaces = {}
		self.namespaces.clear()
		
		cmds.tabLayout(self.poseManUI["mainTabs"], e=1, cc=self.passDef)
		
		# si existe un personaje, borramos las tabs
		tabsSections = cmds.tabLayout(self.poseManUI["mainTabs"], q=1, ca=1)
		if tabsSections != None:
			for tab in tabsSections:
				cmds.deleteUI(self.poseManUI["mainTabs"] + "|" + tab)
				
		# establecemos dos variables "globales"
		self.characterFilePath = characterFilePath
		self.characterDirectoryPath = characterFilePath.rpartition("/")[0]
		self.projectName = self.characterFilePath.rpartition("/")[2].rpartition(".")[0]
		
		# obtenemos un diccionario con los datos del personaje, nombre, icono, secciones y namespaces
		characterData = {}
		characterData = self.getCharacterDataFromXMLFile(self.characterFilePath)
		
		# desglosamos characterData
		name = characterData["name"]
		icon = characterData["icon"]
		sections = characterData["sections"]
		namespaces = characterData["namespaces"]
		
		# cargamos el personaje en la UI
		# basicamente es cargar las secciones como tabs y las subsecciones como framelayouts dentro de cada tab
		self.loadSections(sections, namespaces)
	
		# ponemos en el textField de namespace el namesapce de la seccion 1		
		firstSection = self.getCurrentActiveSection()
		cmds.textField(self.poseManUI["sectionNamespaceTF"], e=1, text=self.namespaces[firstSection])
		
		cmds.tabLayout(self.poseManUI["mainTabs"], e=1, cc=self.refreshTabInfo)		

	def getParentLayout(self, layout, depth=1, *args):		
		result = ""
		childs = layout.split("|")
		nChilds = len(childs)
		
		if depth==0 or depth==-1 or depth>nChilds-1:
			result = childs[0]
		else:
			tail = depth*-1
			result = "|".join(layout.split("|")[:tail])
			
		return result

	def getChildsLayout(self, layout, depth=1):    
		result = ""
		childs = layout.split("|")
		nChilds = len(childs)
		
		if depth==0 or depth==-1 or depth>nChilds-1:
			result = childs[0]
		else:
			tail = depth*-1
			result = "|".join(layout.split("|")[tail:nChilds])
			
		return result
	
	def poseDrag (self, dragControl, x, y, modifiers, *args):
		pass

	def collapse(self, widget, *args):
		cmds.frameLayout(widget, e=1, h=20)

	def expand(self, widget, *args):
		cmds.frameLayout(widget, e=1, h=self.groupFrameLayoutHeights[widget])    

	def precollapse(self, widget, *args):
		altura = cmds.frameLayout(widget, q=1, h=1)
		self.groupFrameLayoutHeights[widget] = altura
	
	def overwriteOrRename(self, *args):
		poseName = "debug pose name"
		confirm = cmds.confirmDialog( title='Pose exists.', message="A pose with same \"" + poseName + "exists.", button=['Overwrite','Rename', "Cancel"], defaultButton='Cancel', cancelButton='Cancel', dismissString='Cancel')
		
	def movePoseFromGroupToGroup(self, dragControl, dropControl, messages, x, y, dragType, *args):	
		# Obtenemos los layotus, los nombres etc..
		
		# > ORIGEN
		poseLayout = self.getParentLayout(dragControl)
		textLayout = cmds.layout(poseLayout, q=1, ca=1)[1]
		
		# pose
		poseName = cmds.text(textLayout, q=1, label=1)
		
		# group
		groupLayout = self.getParentLayout(dragControl, 4)
		groupName = cmds.frameLayout(groupLayout, q=1, label=1)
		
		# section
		sectionLayout = self.getParentLayout(dragControl, 7)
		sectionName = cmds.tabLayout(sectionLayout, q=1, st=1)
		
		# > DESTINO
		# section
		targetSectionLayout = self.getParentLayout(dropControl, 4)
		targetSectionName = cmds.tabLayout(targetSectionLayout, q=1, st=1)
		
		targetGroupLayout = self.getParentLayout(dropControl)
		targetGroupName = cmds.frameLayout(targetGroupLayout, q=1, label=1)

		# check if is the same grid		
		sourceGrid = self.getParentLayout(dragControl, 3)
		targetGrid = dropControl		
		
		#
		# print "self.setPose("+ targetSectionName + ", " + targetGroupName + ", " + poseName +")"
		
		
		# todo ocurrira si la pose no existe en el sitio de destino		
		if self.poseExists(targetSectionName, targetGroupName, poseName) == False:
		
			# evita que arrastremos una pose a su mismo grupo
			if targetGrid != sourceGrid:		
				# XML EDITION		
				# REMOVE POSE FROM ITS GROUP
				# source pose xml name file	
				self.removePoseFromFileConfig(sectionName, groupName,  poseName)
				
				# ADD POSE TO TARGET GROUP
				self.addPoseToConfFile(targetSectionName, targetGroupName, poseName)
				
				# movemos los archivos
				shutil.move(self.characterDirectoryPath + "/" + sectionName + "/" + groupName + "/" + poseName + ".pose", self.characterDirectoryPath + "/" + targetSectionName + "/" + targetGroupName + "/")
				shutil.move(self.characterDirectoryPath + "/" + sectionName + "/" + groupName + "/" + "thumbs" + "/" + "small" + "/" + poseName + ".png", self.characterDirectoryPath + "/" + targetSectionName + "/" + targetGroupName + "/" + "thumbs" + "/" + "small" + "/")
				shutil.move(self.characterDirectoryPath + "/" + sectionName + "/" + groupName + "/" + "thumbs" + "/" + "medium" + "/" + poseName + ".png", self.characterDirectoryPath + "/" + targetSectionName + "/" + targetGroupName + "/" + "thumbs" + "/" + "medium" + "/")
				shutil.move(self.characterDirectoryPath + "/" + sectionName + "/" + groupName + "/" + "thumbs" + "/" + "large" + "/" + poseName + ".png", self.characterDirectoryPath + "/" + targetSectionName + "/" + targetGroupName + "/" + "thumbs" + "/" + "large" + "/")
				
				# move ui pose from group to group
				cmds.frameLayout(self.getParentLayout(dragControl, 2), e=1, p=dropControl)
				
			# ahora atualizamos el tamano del grid
			
			#hijos
			sourceGridChilds = cmds.gridLayout(sourceGrid, q=1, ca=1)
			targetGridChilds = cmds.gridLayout(targetGrid, q=1, ca=1)
			
			#tamanos
			sourceGridWidth = cmds.gridLayout(sourceGrid, q=1, w=1)
			targetGridWidth = cmds.gridLayout(targetGrid, q=1, w=1)
			
			sourceGridHeight = cmds.gridLayout(sourceGrid, q=1, h=1)
			targetGridHeight = cmds.gridLayout(targetGrid, q=1, h=1)		
			
			# ajustamos tamano gridOrigen
			# 102 es el tamano actual de una pose, habra que meterlo en variable para
			# diferentes tamanos de thumbnail
			if sourceGridChilds:
				nSourceGridChilds = len(sourceGridChilds)
				nuevoAltoGridOrigen = ((self.poseThumbnailSize[0]+22) * math.ceil((nSourceGridChilds*self.poseThumbnailSize[0])/sourceGridWidth)) + 22
				sourceFrameLayout = self.getParentLayout(sourceGrid)
				cmds.frameLayout(sourceFrameLayout, e=1, h=nuevoAltoGridOrigen)
		
			# ajustamos tamano gridDestino
			if targetGridChilds:
				ntargetGridChilds = len(targetGridChilds)
				nuevoAltoGridDestino = ((self.poseThumbnailSize[0]+22) * math.ceil((ntargetGridChilds*self.poseThumbnailSize[0])/targetGridWidth)) + 22
				targetFrameLayout = self.getParentLayout(targetGrid)
				cmds.frameLayout(targetFrameLayout, e=1, h=nuevoAltoGridDestino)
				
			# usamos setPosePupUps para actualizar los comandos del boton pose, ya que esta pose se habra cambiado de seccion y o grupo
			# es lo mismo que cuando la renombramos
			self.setPosePopUps(targetSectionName, targetGroupName, poseName, poseName)
		
		else:
			print "Existe una pose con ese nombre"
			
		
	def loadSections(self, sections, namespaces):
		
		# recorremos todas las secciones
		for i in range(len(sections)):
			
			# establecemos la entrada en el diccionario de los namespaces escritos en el XML "" (vacio) o con valor
			self.namespaces[sections[i]] = namespaces[i]
			
			# Layout principal de la seccion			
			self.poseManUI["mainSectionForm"] = cmds.formLayout(sections[i] , p=self.poseManUI["mainTabs"])
			self.LYT[sections[i]] = self.poseManUI["mainSectionForm"]
			
			# 1 un layout provisional, para anadir botones, etc.. 
			self.poseManUI["namespaceSetionForm"] = cmds.rowColumnLayout(nc=1, cw=[(1,30)], p=self.poseManUI["mainSectionForm"])
			# botones provisionales, en principio pongo este para que se vea el layout
			# cmds.button(label="", w=1, h=1)
			
			# 2 el scrollLayout donde van las subseccinoes y las poses
			self.poseManUI["scroll"] = cmds.scrollLayout(p=self.poseManUI["mainSectionForm"], cr=1)
			
			# lista de subsecciones
			subSections = self.getSubSections(sections[i])
			
			# subsecciones		
			subSectionsDic = {}
			for z in range(len(subSections)):
				#subSectionFrame = cmds.frameLayout(subSections[z], bgc=(0.2, 0.2, 0.25), bv=1, cll=1, cl=0, bs="in", lv=1, p=self.poseManUI["scroll"])
				subSectionsDic["subSectionFrame"] = cmds.frameLayout(subSections[z], bgc=(0.2, 0.2, 0.25), bv=0, cll=1, cl=0, bs="in", lv=1, p=self.poseManUI["scroll"])				
				cmds.frameLayout(subSectionsDic["subSectionFrame"], e=1,\
				collapseCommand=partial(self.collapse, subSectionsDic["subSectionFrame"]),\
				expandCommand=partial(self.expand, subSectionsDic["subSectionFrame"]),\
				preCollapseCommand=partial(self.precollapse, subSectionsDic["subSectionFrame"])\
				)
				
				cmds.popupMenu()
				
				# cmds.menuItem(label="Rename...")
				cmds.menuItem(label="Delete Group...", c=partial(self.deleteSubSection, sections[i], subSections[z]))
				cmds.menuItem(label="Rename Group...", c=partial(self.renameSubSectionUI, sections[i], subSections[z]))
				
				subSectionGrid = cmds.gridLayout(\
						nc=cmds.window(self.poseManUI["poseManWin"], q=True, w=True) / (self.poseThumbnailSize[0]+2),\
						cw=(self.poseThumbnailSize[0]+2),\
						ch=(self.poseThumbnailSize[0]+22),\
						ag=1,\
						aec=0,\
						p=subSectionsDic["subSectionFrame"],\
						dpc=self.movePoseFromGroupToGroup\
				)
				
				poses = []
				poses = self.getPosesFromSubsection(sections[i], subSections[z])				
				
				for k in range(len(poses)):
					self.addSinglePoseToUI(sections[i], subSections[z], poses[k], subSectionGrid)

				### positions
				cmds.formLayout(
					self.poseManUI["mainSectionForm"], e=True,
					attachForm=[
						(self.poseManUI["namespaceSetionForm"], 'top', 5),
						(self.poseManUI["namespaceSetionForm"], 'left', 5),
						(self.poseManUI["namespaceSetionForm"], 'right', 5),
						(self.poseManUI["scroll"], 'left', 1),
						(self.poseManUI["scroll"], 'right', 1),
						(self.poseManUI["scroll"], 'bottom', 1)
					],
					
					attachControl=[
						(self.poseManUI["scroll"], 'top', 0, self.poseManUI["namespaceSetionForm"])
					]
				)
				
	def getCharacterDataFromXMLFile (self, xmlfile):
		"""
		devuelve un diccionario con los datos del personaje
		charDic = {"name":"charName", "icon":"charIcon", "sections":["s1", "s2", "s3"]}
		"""		
		characterData = {"name":"", "icon":"", "sections":"", "namespaces":""}
	
		xmlFile = xml.dom.minidom.parse(xmlfile)
		charName = xmlFile.getElementsByTagName("character")[0].getAttribute("name")
		charIcon = xmlFile.getElementsByTagName("character")[0].getAttribute("icon")
		
		charSections = []
		charNamespaces = []
		for section in xmlFile.getElementsByTagName("section"):
			charSections.append(section.getAttribute("name"))
			charNamespaces.append(section.getAttribute("namespace"))	
		
		characterData["name"] = charName
		characterData["icon"] = charIcon
		characterData["sections"] = charSections
		characterData["namespaces"] = charNamespaces
		
		return characterData
		
	def addSinglePoseToUI(self, sectionName, subSectionName, poseName, menuUI, *args):
		# add a pose thumbnail to UI parented to menuUI
		# this is de main def where put all related with iconTextbutton pose item

		poseBorderFrame = cmds.frameLayout(bgc=(0.2, 0.2, 0.2), p=menuUI, lv=0, bv=1, bs="out")
		
		cmds.rowColumnLayout(p=poseBorderFrame, nr=2)
		
		cmds.iconTextButton(
			dgc=self.poseDrag,
			image=(self.characterDirectoryPath + "/" + sectionName + "/" + subSectionName + "/" + "thumbs" + "/" + self.poseThumbnailSize[2] + "/" + poseName + ".png"),
			command=partial(self.setPose, sectionName, subSectionName, poseName)
		)
		
		textIconLabel = cmds.text(l=poseName, bgc=(0.4, 0.4, 0.4))

		# contextual menu
		cmds.popupMenu(p=poseBorderFrame)
		cmds.menuItem(en=1, l="Mix pose Slider", 									c=partial(self.sliderMix, sectionName, subSectionName, poseName))
		cmds.menuItem(divider=1)
		cmds.menuItem(en=0, l="Update (All controls)", 								c="")
		cmds.menuItem(en=1, l="Add selected controls", 								c=partial(self.addSelectedControls, sectionName, subSectionName, poseName))
		cmds.menuItem(en=1, l="Remove selected controls from pose", 				c=partial(self.removeSelectedControls, sectionName, subSectionName, poseName))
		cmds.menuItem(en=1, l="Select controls", 									c=partial(self.selectPoseControls, sectionName, subSectionName, poseName))
		cmds.menuItem(divider=1)
		cmds.menuItem(en=0, l="Override controls...", 								c="")
		cmds.menuItem(en=0, l="Edit Pose...", 										c=partial(self.editPose, sectionName, subSectionName, poseName))
		cmds.menuItem(divider=1)
		cmds.menuItem(en=1, l="Move to...",											c=partial(self.movePoseUI, sectionName, subSectionName, poseName))
		cmds.menuItem(en=1, l="Rename ...", 										c=partial(self.renamePoseUI, sectionName, subSectionName, poseName))
		cmds.menuItem(en=1, l="Delete pose", 										c=partial(self.deletePose, sectionName, subSectionName, poseName))
	
	def editPose(self, sectionName, subSectionName, poseName):
		xmlFile = self.characterDirectoryPath + "/" + sectionName + "/" + subSectionName + "/" + poseName + ".pose"
		xmlDoc = xml.dom.minidom.parse(xmlFile)	
	
	def addSelectedControls(self, sectionName, subSectionName, poseName, *args):
		# hacemos una lista de los objetos seleccionados y de los mismos sin namespaces si los tuviesen
		fullSelectedObjects = cmds.ls(l=1, sl=1)
		fullSelectedObjects_NO_NS = self.stripNamespaceList(fullSelectedObjects)

		xmlFile = self.characterDirectoryPath + "/" + sectionName + "/" + subSectionName + "/" + poseName + ".pose"
		xmlDoc = xml.dom.minidom.parse(xmlFile)
		
		# lista de objetos en el XML
		objectsInFile = self.getObjectsFromPoseFile(sectionName, subSectionName, poseName)

		# el nodo principal <pose> de todos los objetos <obj>
		mainObjNode = xmlDoc.getElementsByTagName("pose")[0]
		
		# anadimos todos los objetos, uno por uno
		# creamos el nuevo nodo que hay que anadir, un nodo <obj> con su atributo name
		# por cada objeto creamos los nodos de sus atributos <attr>
		
		for i in range(len(fullSelectedObjects)):
		
			if fullSelectedObjects_NO_NS[i] not in objectsInFile:				
				# lista de atributos keyables
				newObjNode = xmlDoc.createElement("obj")
				newAttr = xmlDoc.createAttribute("name")
				newObjNode.setAttributeNode(newAttr)
				newObjNode.setAttribute("name", fullSelectedObjects_NO_NS[i])
				mainObjNode.appendChild(newObjNode)
			
				keyAttrList = cmds.listAttr(fullSelectedObjects[i], keyable=1, scalarAndArray=1, unlocked=True)
				
				for k in range(len(keyAttrList)):
					# nodo <attr>
					newAttrNode = xmlDoc.createElement("attr")
					# atributos
					newMixAttr = xmlDoc.createAttribute("mix")
					newNameAttr = xmlDoc.createAttribute("name")
					newValueAttr = xmlDoc.createAttribute("value")
					
					# asignamos los atributos al nodo
					newAttrNode.setAttributeNode(newMixAttr)
					newAttrNode.setAttributeNode(newNameAttr)
					newAttrNode.setAttributeNode(newValueAttr)
					
					# asignamos valor a los atributos
					newAttrNode.setAttribute("mix", "1")
					newAttrNode.setAttribute("name", keyAttrList[k])
					attrValue = cmds.getAttr(fullSelectedObjects[i] + "." + keyAttrList[k])
					
					# convert True = 1 and False = 0
					if attrValue == True:
						attrValue = 1
					elif attrValue == False:
						attrValue = 0
					
					newAttrNode.setAttribute("value", str(attrValue))
					
					newObjNode.appendChild(newAttrNode)

		f = open(xmlFile, "w")
		f.write(xmlDoc.toxml())
		f.close()
		
	
	def getObjectsFromPoseFile(self, sectionName, subSectionName, poseName, *args):
		"""
		Devuelve una lista con todos los nombres de objetos que hay en una pose
		"""
		xmlFile = self.characterDirectoryPath + "/" + sectionName + "/" + subSectionName + "/" + poseName + ".pose"
		xmlDoc = xml.dom.minidom.parse(xmlFile)
		
		objects = []
		objNodes = xmlDoc.getElementsByTagName("obj")
		for obj in objNodes:
			objects.append(obj.getAttribute("name"))
		
		return objects

	def objectInXMLExists(self, poseXMLDoc, objectName):
		exists = 0
		
		# el nodo principal <pose> de todos los objetos <obj>
		objNodes = poseXMLDoc.getElementsByTagName("obj")
	
	def removeSelectedControls(self, sectionName, subSectionName, poseName, *args):
		# hacemos una lista con los seleccionados
		fullSelectedObjects = cmds.ls(l=1, sl=1)
		fullSelectedObjects_NO_NS = self.stripNamespaceList(fullSelectedObjects)
		
		# lista de objetos en el XML
		objectsInFile = self.getObjectsFromPoseFile(sectionName, subSectionName, poseName)		
		
		xmlFile = self.characterDirectoryPath + "/" + sectionName + "/" + subSectionName + "/" + poseName + ".pose"
		xmlDoc = xml.dom.minidom.parse(xmlFile)
		
		mainObjNodes = xmlDoc.getElementsByTagName("pose")[0]
		objNodes = xmlDoc.getElementsByTagName("obj")
		for obj in objNodes:
			objName = obj.getAttribute("name")
			if objName in fullSelectedObjects_NO_NS:
				mainObjNodes.removeChild(obj)
				
		# write file
		f = open(xmlFile, "w")
		f.write(xmlDoc.toxml())
		f.close()
		
	def selectPoseControls(self, sectionName, subSectionName, poseName, *args):
		"""
		selecciona los controles que tiene una pose
		"""
		xmlFile = self.characterDirectoryPath + "/" + sectionName + "/" + subSectionName + "/" + poseName + ".pose"
		xmlDoc = xml.dom.minidom.parse(xmlFile)
		
		cmds.select(cl=1)
		objNodes = xmlDoc.getElementsByTagName("obj")
		for obj in objNodes:
			objName = obj.getAttribute("name")
			# get the namespaces
			sectionNSList = self.namespaces[sectionName]
			sectionNamespaces = sectionNSList.split(",")
			
			# apply pose for each one ns
			for singleNS in sectionNamespaces:
				objWithNS = string.replace(objName, "|", "|" + singleNS + ":")
				
				print objWithNS
				
				cmds.select(objWithNS, add=1)
	
	def getPosesFromSubsection(self, sectionName, subSectionName):
		posesConfFile = self.characterDirectoryPath + "/" + sectionName + "/" + subSectionName + "/" + self.poseConfigFile
		xmlFile = xml.dom.minidom.parse(posesConfFile)
		
		poses = []
		for pose in xmlFile.getElementsByTagName("pose"):
			poses.append(pose.getAttribute("name"))
			
		return poses	
			
	def setPose(self, sectionName, subSectionName, poseName, sides=("L_", "R_"), *args):
		"""
		set a pose from xml file
		"""
		
		self.sym = False
		self.sides = sides
		
		import time
		start = time.time()
		
		self.globalSectionName = sectionName

		# miramos si tenemos alt, ctrl, etc.. pulsado
		self.mods = cmds.getModifiers()
		
		self.mult = 1.0
		
		# ctrl
		if self.mods == 4: self.mult = 0.1
		
		# shift 
		if self.mods == 1: self.mult = 0.5
		
		# alt
		if self.mods == 8: self.sym = True
	
		
		# Shift = 1
		# Caps = 2
		# Ctrl = 4
		# Alt = 8
		# Shift+Ctrl = 5
		# Shift+Alt = 9
		# Ctrl+Alt = 12
		# Shift+Ctrl+Alt = 13
		
		# leemos el archivo de pose (xml)
		xmlFile = self.characterDirectoryPath + "/" + sectionName + "/" + subSectionName + "/" + poseName + ".pose"
		xmlDoc = xml.dom.minidom.parse(xmlFile)
		
		# si tenemos objetos seleccionados se aplicara pose solo a estos objetos
		preselected = False
		fullObjects = cmds.ls(sl=1, l=1)		
		
		# Al hacer cmds.ls obtenemos los nombres de los objetos con la informacion del namespace
		# para facilitar la asignacion, quitaremos ese namespace y anadiermos el que tengamos en la interfaz de poseman
		objects = self.stripNamespaceList(fullObjects)
		
		if len(objects)>0: preselected = True
		
		# TODOS LOS NODOS DE OBJETOS		
		xmlObjects = xmlDoc.getElementsByTagName("obj")
		
		# NOS QUEDAMOS SOLO CON LOS NODOS XML DE LOS OBJETOS QUE TENEMOS SELECCIONADOS SI PRESELECTED = TRUE
		filterObjNodes = []
		if preselected:
			for obj in xmlObjects:
				objName = obj.getAttribute("name")
				if objName in objects:
					filterObjNodes.append(obj)
		else:
			filterObjNodes = xmlObjects
		
		# usamos map para ejecutar mas rapido
		map(self.setPoseMap, filterObjNodes)
		
		end = time.time()
		# print start, end, end-start

	def setPoseMap(self, obj, sym=False):		
		
		objName = obj.getAttribute("name")
		
		if self.sym:
			objName = self.flipSides(objName, self.sides[0], self.sides[1])
		
		
		# get the namespaces ["ns1", "ns2", "ns3"]
		sectionNSList = self.namespaces[self.globalSectionName]
		sectionNamespaces = sectionNSList.split(",")		
		
		# apply pose for each one ns
		
		for singleNS in sectionNamespaces:
			self.objWithNS = string.replace(objName, "|", "|" + singleNS + ":")		
			
			if cmds.objExists(self.objWithNS):				
				attrNodes = obj.getElementsByTagName("attr")				
				map(self.setAttrMap, attrNodes)
			else:
				cmds.warning("Can't find \"" + self.objWithNS + "\" object")
			

	def setAttrMap(self, attr):
		"""
		finalmente hacemos setAttr para establecer la pose
		"""
		
		attrName = attr.getAttribute("name")
		attrValue = attr.getAttribute("value")
					
		if self.mods:
			self.pmSetAttr(self.objWithNS, attrName, float(attrValue), self.mult)
		else:
			cmds.setAttr(self.objWithNS + "." + attrName, float(attrValue))


	def replaceSide(self, object, side1, side2):
		
		objectSymmed = ""
		objetosSolos = object.split("|")[1:]
		objetosTemp = objetosSolos
		slen = len(side1)
		
		for i in range(len(objetosSolos)):
			objetosTemp[i] = "|" + objetosTemp[i]
			crop = objetosSolos[i][0:slen+1]
			if crop == "|"+side1:
				objetosTemp[i] = "|"+side2+objetosSolos[i][slen+1:]

		objectSymmed = "".join(objetosTemp)
		
		return objectSymmed

	def flipSides(self, object, side1, side2):

		print len(side1), len(side2)
		
		if len(side1) == len(side2):
			objectSymmed = ""
			objetosSolos = object.split("|")[1:]
			objetosTemp = objetosSolos
			slen = len(side1)

			for i in range(len(objetosSolos)):
				objetosTemp[i] = "|" + objetosTemp[i]
				
				crop = objetosSolos[i][0:slen+1]

				# side1 > side2
				if crop == "|"+side1:
					objetosTemp[i] = "|"+side2+objetosSolos[i][slen+1:]
				# side2 > side1
				elif crop == "|"+side2:
					objetosTemp[i] = "|"+side1+objetosSolos[i][slen+1:]

			objectSymmed = "".join(objetosTemp)
		else:
			print "Ambos lados deben tener el mismo tamano de letras"
			objectSymmed = None

		return objectSymmed
	
	def setPosex(self, sectionName, subSectionName, poseName, *args):
	
		import time
		start = time.time()

		# miramos si tenemos alt, ctrl, etc.. pulsado
		mods = cmds.getModifiers()		
		
		mult = 1.0
		
		# ctrl
		if mods == 4: mult = 0.1
		
		# shift 
		if mods == 1: mult = 0.5
		
		# Shift = 1
		# Caps = 2
		# Ctrl = 4
		# Alt = 8
		# Shift+Ctrl = 5
		# Shift+Alt = 9
		# Ctrl+Alt = 12
		# Shift+Ctrl+Alt = 13
		
		# leemos el archivo de pose (xml)	
		xmlFile = self.characterDirectoryPath + "/" + sectionName + "/" + subSectionName + "/" + poseName + ".pose"
		xmlDoc = xml.dom.minidom.parse(xmlFile)
		
		# si tenemos objetos seleccionados se aplicara pose solo a estos objetos
		preselected = False
		objects = cmds.ls(sl=1, l=1)
		
		if len(objects)>0: preselected = True
		
		objNodes = xmlDoc.getElementsByTagName("obj")
		for obj in objNodes:
			objName = obj.getAttribute("name")
			
			# get the namespaces
			sectionNSList = self.namespaces[sectionName]
			sectionNamespaces = sectionNSList.split(",")
			
			# apply pose for each one ns
			for singleNS in sectionNamespaces:
				objWithNS = string.replace(objName, "|", "|" + singleNS)
				
				if cmds.objExists(objWithNS):				
					attrNodes = obj.getElementsByTagName("attr")
					for attr in attrNodes:
						attrName = attr.getAttribute("name")
						attrValue = attr.getAttribute("value")					
						
						# Si hay preseleccion, aplicaremos la pose solo a esos objetos
						if preselected:
							# Con este if lo que hacemos es entrar dentro si objWithNS esta dentro de objects
							# objects es el grupo de objetos que tenemos seleccionados
							if objWithNS in objects:								
								# separamos el setattr del mpsetattr porquye el setattr es mas rapido
								# y si no tenemos pulsada una tecla lo usamos
								if mods:
									self.pmSetAttr(objWithNS, attrName, float(attrValue), mult)
								else:
									cmds.setAttr(objWithNS + "." + attrName, float(attrValue))
						else:
							# Si no hay nada seleccionado, aplicaremos la pose a todos los objetos
							if mods:
								self.pmSetAttr(objWithNS, attrName, float(attrValue), mult)
							else:
								cmds.setAttr(objWithNS + "." + attrName, float(attrValue))
				else:
					cmds.warning("Can't find \"" + objWithNS + "\" object")
		end = time.time()
		print start, end, end-start

		
	"""
	def setPose(self, sectionName, subSectionName, poseName, *args):
	
		# miramos si tenemos alt, ctrl, etc.. pulsado
		mods = cmds.getModifiers()		
		
		mult = 1.0
		
		# ctrl
		if mods == 4: mult = 0.1
		
		# shift 
		if mods == 1: mult = 0.5
		
		# Shift = 1
		# Caps = 2
		# Ctrl = 4
		# Alt = 8
		# Shift+Ctrl = 5
		# Shift+Alt = 9
		# Ctrl+Alt = 12
		# Shift+Ctrl+Alt = 13
		
		# leemos el archivo de pose (xml)	
		xmlFile = self.characterDirectoryPath + "/" + sectionName + "/" + subSectionName + "/" + poseName + ".pose"
		xmlDoc = xml.dom.minidom.parse(xmlFile)
		
		# si tenemos objetos seleccionados se aplicara pose solo a estos objetos
		preselected = False
		objects = cmds.ls(sl=1, l=1)
		
		if len(objects)>0: preselected = True
		
		objNodes = xmlDoc.getElementsByTagName("obj")
		for obj in objNodes:
			objName = obj.getAttribute("name")
			
			# get the namespaces
			sectionNSList = self.namespaces[sectionName]
			sectionNamespaces = sectionNSList.split(",")
			
			# apply pose for each one ns
			for singleNS in sectionNamespaces:
				objWithNS = string.replace(objName, "|", "|" + singleNS)
				
				if cmds.objExists(objWithNS):				
					attrNodes = obj.getElementsByTagName("attr")
					for attr in attrNodes:
						attrName = attr.getAttribute("name")
						attrValue = attr.getAttribute("value")					
						# si hay preseleccion
						if preselected:
							# aplicar solo a los seleccionados
							if objWithNS in objects:
								# separamos el setattr del mpsetattr porquye el setattr es mas rapido
								# y si no tenemos pulsada una tecla lo usamos
								if mods:
									self.pmSetAttr(objWithNS, attrName, float(attrValue), mult)
								else:
									cmds.setAttr(objWithNS + "." + attrName, float(attrValue))
						else:
							# si no, a todos
							if mods:
								self.pmSetAttr(objWithNS, attrName, float(attrValue), mult)
							else:
								cmds.setAttr(objWithNS + "." + attrName, float(attrValue))
				else:
					cmds.warning("Can't find \"" + objWithNS + "\" object")
	
	"""
	"""
	def setPose(self, sectionName, subSectionName, poseName, *args):
	
		# miramos si tenemos alt, ctrl, etc.. pulsado
		mods = cmds.getModifiers()		
		
		mult = 1.0
		
		# ctrl
		if mods == 4: mult = 0.5
		
		# shift + ctrl
		if mods == 5: mult = 0.1
		
		# Shift = 1
		# Caps = 2
		# Ctrl = 4
		# Alt = 8
		# Shift+Ctrl = 5
		# Shift+Alt = 9
		# Ctrl+Alt = 12
		# Shift+Ctrl+Alt = 13
		
		# leemos el archivo de pose (xml)	
		xmlFile = self.characterDirectoryPath + "/" + sectionName + "/" + subSectionName + "/" + poseName + ".pose"
		xmlDoc = xml.dom.minidom.parse(xmlFile)
		
		# si tenemos objetos seleccionados se aplicara pose solo a estos objetos
		preselected = False
		objects = cmds.ls(sl=1, l=1)
		
		if len(objects)>0: preselected = True
		
		objNodes = xmlDoc.getElementsByTagName("obj")
		for obj in objNodes:
			objName = obj.getAttribute("name")
			
			# get the namespaces
			sectionNSList = self.namespaces[sectionName]
			sectionNamespaces = sectionNSList.split(",")
			
			# apply pose for each one ns
			for singleNS in sectionNamespaces:
				objWithNS = string.replace(objName, "|", "|" + singleNS)
				
				attrNodes = obj.getElementsByTagName("attr")
				for attr in attrNodes:
					attrName = attr.getAttribute("name")
					attrValue = attr.getAttribute("value")					
					# si hay preseleccion
					if preselected:
						# aplicar solo a los seleccionados
						if objWithNS in objects:
							cmds.setAttr(objWithNS + "." + attrName, float(attrValue))
					else:
						# si no, a todos
						cmds.setAttr(objWithNS + "." + attrName, float(attrValue))
		
		print objWithNS	
	"""
	
	def getSections(self, *args):
		xmlFile = self.characterFilePath
		xmlDoc = xml.dom.minidom.parse(xmlFile)
		
		sectionsNode = xmlDoc.getElementsByTagName("section")
		sections = []
		for section in sectionsNode:
			sections.append(section.getAttribute("name"))
			
		return sections

	def getSubSections(self, sectionName, *args):
		xmlFile = self.characterDirectoryPath + "/" + sectionName + "/" + self.sectionConfigFile
		xmlDoc = xml.dom.minidom.parse(xmlFile)
		
		sectionsNode = xmlDoc.getElementsByTagName("section")
		subSections = []
		for section in sectionsNode:
			subSections.append(section.getAttribute("name"))
			
		return subSections
		
	def getPosesFromFile(self, characterPath, sectionName):
		pass

	def getDirs(self, path):		
		dirs=[]

		for entry in os.listdir(path):
			fullpath=os.path.join(path,entry)
			if os.path.isdir(fullpath):
				dirs.append(fullpath)
		return dirs
		
	def findPoseFiles(self, sectionName):		
		fileExtension = ".pose"
		fileDirectory = self.characterPath + "/" + sectionName
		allFiles = os.listdir(fileDirectory)

		returnFiles = []
		for f in allFiles:
			splitString = str(f).rpartition(fileExtension)
					
			if not splitString[1] == "" and splitString[2] == "":
				if not splitString[0] == "__init__" and not splitString[0] == "__poses__":
					returnFiles.append(splitString[0])

		return returnFiles
		
	def openNewProjectWindow(self, *args):
		singleFilter = "*.pman"
		returnFile = cmds.fileDialog2(cap="Open PoseMan project", fileFilter=singleFilter, dialogStyle=2, fm=1, okc="Open")
		if returnFile != None:
			self.openNewProject(returnFile[0])
		else:
			print "do not nothing"
		
	def learnNamespace(self):
		"""
		A apartir de una seleccion de objetos, obtiene el/los namespaces los pone en el inputText y los activa
		"""
		
		objList = cmds.ls(sl=1, l=1)
		
		self.charNamespaces = []
		textNamespaces = ""
		for object in objList:
			NS = self.getNS(object)
			if len(NS)>0:
				if not NS in self.charNamespaces:					
					self.charNamespaces.append(NS)
					textNamespaces += NS[:-1] + ", "
		
		# print namespaces into textfield separated with commas
		# nemo:, merlin:, juan:
		# strip the ","
		textNamespaces = textNamespaces[:-2]
		cmds.textField(self.poseManUI["sectionNamespaceTF"], e=1, text=textNamespaces)
		
		self.setSectionNamespace()
		
		return self.charNamespaces

	def getNS(self, obj):
		if obj != "":
			NS = obj.rpartition("|")[2].rpartition(":")[0]
			
			if len(NS)>0:
				charNamespace = NS + ":"
			else:
				charNamespace = ""
				
		return charNamespace
		
	def stripNamespace(self, objName):
		"""
		elimina la informacion de namespace del nombre de un objeto
		
		"""
		import string
		ns = self.getNS(objName)
		cleanObjName = string.replace(objName, ns, "")
		
		return cleanObjName		
		#return string.replace(obj, ns, "")
		
	def stripNamespaceList(self, objList):
		"""
		elimina la informacion de namespace de una lista de objetos
		
		"""		
		cleanList = []
		for obj in objList:
			cleanList.append(self.stripNamespace(obj))
			
		return cleanList
	
	def findHighestTrailingNumber(names, basename):
		"""
		
		"""
		highestValue = 0
	
		for n in names:
			if n.find(basename) == 0:
				suffix = n.partition(basename)[2]
				if re.match("^[0-9]*$", suffix):
					numericalElemnt = int(suffix)
					
					if numericalElemnt > highestValue:
						highestValue = numericalElemnt
		
		return highestValue

	def getFullPath(object):
		"""
		
		"""
		fullPath = ""
		parents = cmds.listRelatives(object, p=1, f=1)

		if parents == None:
			parents = [""]
		
		fullPath = parents[0] + "|" + object
		return fullPath
		
	def spacesToDown(self, string):
		"""
		
		"""
		return string.replace(" ", "_")
		
	def sectionExists(self, section):
		"""
		Comprueba si existe una seccion, tanto en hd como en el archivo de configuracion
		"""
		sectionExists = True
		hdExists = True
		configFileExists = False

		# obtenemos de alguna forma el path y el nombre de la seccion, tanto si recibimos el path como el nombre de la seccion
		if "/" in section:
			sectionPath = section
			sectionName = section.rpartition("/")[2]
		else:
			sectionPath = self.characterDirectoryPath + "/" + section
			sectionName = section

		# 1 - comprobamos que existe en el HD
		hdExists = os.path.exists(sectionPath)

		# 2 - comprobamos que existe en el archivo de configuracion
		xmlFile = self.characterFilePath
		xmlDoc = xml.dom.minidom.parse(xmlFile)

		mainSectionsNode = xmlDoc.getElementsByTagName("sections")[0]
		sectionsNodes = xmlDoc.getElementsByTagName("section")

		for sectionNode in sectionsNodes:
			if sectionNode.getAttribute("name") == sectionName:
				configFileExists = True
				break
			
		if not hdExists and not configFileExists:
			sectionExists = False
			# print "la seccion no existe en " + sectionPath + ", procedemos al copiado"
		elif hdExists == False and configFileExists  == True:
			sectionExists = True
			# print "no existe una direccion fisica de la seccion pero en el archivo de configuracion consta ese nombre de seccion, edita el archivo " + "file" + " manualmente"
		elif hdExists == True:
			sectionExists = True
			# print "Ya existe en el disco una seccion con el mismo nombre"
			
		return sectionExists
		
	def createNewProjectWindow(self, *args):
		"""
		Crea una ventana para crear un proyecto nuevo de poseman
		"""
		
		if cmds.window("newposemanprojectwindow", exists=True):
			cmds.deleteUI("newposemanprojectwindow", window=True)
		
		self.poseManUI["newProjectWindow"] = cmds.window("newposemanprojectwindow", title="New PoseMan Project", w=300, h=200)
		
		# 5 main rows
		cmds.frameLayout(mh=5,mw=5,bv=0,lv=0)
		
		ML = cmds.rowColumnLayout(nr=6)
		
		# 1 - Project name
		c1 = cmds.rowColumnLayout(p=ML, nr=3)
		cmds.frameLayout(p=c1, mh=5,mw=10,bv=0,lv=0)
		cmds.text(w=100, label="Project Name", align="left")
		self.poseManUI["newProjectNameTextField"] = cmds.textField(w=200, text="")
		cmds.setFocus(self.poseManUI["newProjectNameTextField"])
		
		# 2 - Project path
		c2 = cmds.rowColumnLayout(p=ML, nr=3)
		cmds.frameLayout(p=c2, mh=5,mw=10,bv=0,lv=0)		
		cmds.text(align="left", label="Project Location")
		self.poseManUI["newProjectPathTextField"] = cmds.textFieldButtonGrp(text="", buttonLabel='Browse...', bc=self.newProjectFileDialog)
		
		# 3 - separator
		c3 = cmds.separator(p=ML, style="in")
		
		# 4 - new sections and subsections
		c4 = cmds.rowColumnLayout(p=ML, nr=3)
		cmds.frameLayout(p=c4, mh=5,mw=10,bv=0,lv=0)	
		cmds.text(w=100, align="left", label="New Sections (comma separated: Section1, Section2, etc...)")
		self.poseManUI["newSectionsName"] = cmds.textField(w=200, text="Default")

		# 5 - separator
		c5 = cmds.separator(p=ML, style="in")
		
		# 6 - 
		c6 = cmds.rowColumnLayout(p=ML, nr=2)
		cmds.frameLayout(p=c6, mh=25, mw=10, bv=0, lv=0)		
		cmds.button(label="Create", c=self.createNewProject)
		cmds.button(label="Cancel", c=partial(self.deleteMyUI, self.poseManUI["newProjectWindow"]))
		
		cmds.showWindow(self.poseManUI["newProjectWindow"])		

	def newProjectFileDialog(self, *args):
		"""
		Filebrowser for create a new project
		"""
		returnFile = cmds.fileDialog2(cap="New PoseMan Project", dialogStyle=2, fm=2, okc="Open")[0]
		if returnFile != None or returnFile == False:
			cmds.textFieldButtonGrp(self.poseManUI["newProjectPathTextField"], e=1, text=returnFile)
		else:
			print "do not nothing"
	
	def validDirectory(self, directory):
		pass
	
	def createNewProject(self, *args):
		"""
		Create a new proyect directory/files structure
		"""
		
		directory = cmds.textFieldButtonGrp(self.poseManUI["newProjectPathTextField"], q=1, text=1)
		projectName = cmds.textField(self.poseManUI["newProjectNameTextField"], q=1, text=1)
		projectName = self.stripEdgeSpacesAndUnderlines(projectName)
		sectionUser = cmds.textField(self.poseManUI["newSectionsName"], q=1, text=1)
		
		# regular expression part		
		projectName = self.getValidStringName(projectName)
		
		# if self.validDirectory(directory)
		
		if os.path.isdir(directory) and projectName != "":
			# si no ponemos nada, se crearia una seccion por defecto, esta se llamaria Default
			if sectionUser.rpartition(" ")[2] == "":
				sectionUser = "Default"

			# clean all possibles combinations with commas and spaces
			# aplicar expresion regular para limpiar los caracteres extranos
			sectionUserCommaSplit = sectionUser.split(",")
			cleanSections = []
			
			for userSection in sectionUserCommaSplit:
				cleanSections.append(self.getValidStringName(userSection))

			projectDir = directory + "/" + projectName

			# proyect directory
			os.makedirs(projectDir)
			f = open(projectDir + "/" + projectName + self.projectExtension, "w")
			projectXMLString = "<?xml version='1.0' ?>\n<character icon='file.png' name='" + projectName + "' thumbSize='small'>\n\t<sections>\n"
			for section in cleanSections:
				projectXMLString += "\t\t<section name='" + section + "' namespace=\"\"/>\n"
			projectXMLString += "\t</sections>\n</character>"
			f.write(projectXMLString)
			
			# create default section
			for section in cleanSections:
				os.makedirs(projectDir + "/" + section)
				f = open(projectDir + "/" + section + "/" + self.sectionConfigFile, "w")		
				f.write("<?xml version='1.0' ?>\n<sections>\n\t<section name='Default'/>\n</sections>")
				f.close()
			
				# create defaul sub-section
				os.makedirs(projectDir + "/" + section + "/" + "Default")
				# create default thumbnails directorys
				os.makedirs(projectDir + "/" + section + "/" + "Default" + "/" + "thumbs" + "/" + "small")
				os.makedirs(projectDir + "/" + section + "/" + "Default" + "/" + "thumbs" + "/" + "medium")
				os.makedirs(projectDir + "/" + section + "/" + "Default" + "/" + "thumbs" + "/" + "large")
				
				print "hago " + projectDir + "/" + section + "/" + "Default"
				f = open(projectDir + "/" + section + "/" + "Default" + "/" + self.poseConfigFile, "w")
				f.write("<?xml version='1.0' ?>\n<poses>\n</poses>")
				f.close()

			# cargamos el nuevo proyecto en PoseMan
			self.openNewProject(directory + "/" + projectName + "/" + projectName + self.projectExtension)
			
			# borramos la ventana de creacion de proyecto
			self.deleteMyUI(self.poseManUI["newProjectWindow"])
			
		else:
			if projectName == "":				
				print "Type a project name"
			elif os.path.isdir(directory) == False:
				print "Select a valid path"
				
	def stripEdgeSpacesAndUnderlines(self, stringIn):
		"""
		Elimina caracteres para formatearlos como hace maya normalmente.
		Elmina del principio y final de la cadena espacios y "_"
		"""
		cleanString = stringIn.replace("-"," ")
		cleanString = cleanString.replace(" ","_")
	
		i = 0
		for i in range(len(cleanString)):
			if cleanString[i] == "_":
				pass
			else:
				cleanString = cleanString[i:]
				break

		k = len(cleanString)-1
		for i in range(len(cleanString)):
			if cleanString[k] == "_":
				pass
			else:
				cleanString = cleanString[:k+1]
				break
			k=k-1
			
		return cleanString

	def passDef(self, *args):
		"""
		No nace nada, se usa para editar el comportamiento de las tabas cuando no hay seccione y que no de
		error al refrescarse
		"""
		pass
	
	def pyScriptToShelf(self, label, script):
		gShelfTopLevel = mel.eval("$temp = $gShelfTopLevel")
		
		if cmds.tabLayout(gShelfTopLevel, exists=1):
		
			currentShelf = cmds.tabLayout(gShelfTopLevel, q=True, selectTab=True)
			cmds.setParent(currentShelf)

			sourceIcon = "pythonFamily.png"
			cmds.shelfButton(
				command=script,
				sourceType="python",
				label=label,
				annotation=script,
				imageOverlayLabel=label,
				image1=sourceIcon,
				style=cmds.shelfLayout(currentShelf, query=1, style=1),
				width=cmds.shelfLayout(currentShelf, query=1, cellWidth=1),
				height=cmds.shelfLayout(currentShelf, query=1, cellHeight=1)
			)
			
			
	### SLIDER PART
	def mixValue(self, valueFromFile, valueInViewport, mixValue):
		finalValue = valueInViewport + (valueFromFile * mixValue - valueInViewport * mixValue)
		return finalValue
		
	def pmSetAttr(self, object, attr, value, mix):

		# Value from viewport
		valueInViewport = cmds.getAttr(object+"."+attr)
		valueFromFile = value
		
		finalValue = self.mixValue(valueFromFile, valueInViewport, mix)

		cmds.setAttr(object+"."+attr, finalValue)

	def getPoseFullDataFromFilePose(self, sectionName, subSectionName, poseName, *args):
		"""
		devuelve una lista de tuplas con la informacion de la pose (object, attr, value)
		"""
		
		xmlFile = self.characterDirectoryPath + "/" + sectionName + "/" + subSectionName + "/" + poseName + ".pose"
		xmlDoc = xml.dom.minidom.parse(xmlFile)
		
		objNodes = xmlDoc.getElementsByTagName("obj")
		poseFullDataFromFilePose = []
		
		for obj in objNodes:
			objName = obj.getAttribute("name")
			# get the namespaces
			sectionNSList = self.namespaces[sectionName]
			sectionNamespaces = sectionNSList.split(",")
			
			# apply pose for each one ns
			for singleNS in sectionNamespaces:
				objWithNS = string.replace(objName, "|", "|" + singleNS + ":")
				attrNodes = obj.getElementsByTagName("attr")
				
				for attr in attrNodes:
					attrName = attr.getAttribute("name")
					attrValue = attr.getAttribute("value")
					
					poseFullDataFromFilePose.append((objWithNS, attrName, attrValue))
					
		return poseFullDataFromFilePose
		
	
	def getPoseFullDataOfViewportUsingFullDataFromFilePose(self, fullDataTupleList, *args):
		"""
		Devuelve una lista de tuplas con los datos de los objetos del visor
		
		"""		
		poseFullDataFromObjectList = []
		for i in range(len(fullDataTupleList)):
			objName = fullDataTupleList[i][0]
			attrName = fullDataTupleList[i][1]
			attrValue = float(cmds.getAttr(objName+"."+attrName))
			
			if attrValue == True:
				attrValue = 1.0
			elif attrValue == False:
				attrValue = 0.0

			poseFullDataFromObjectList.append((objName, attrName, float(attrValue)))
			
		return poseFullDataFromObjectList	
	

	def setMixPoseWithSliderValue(self, *args):
		"""
		Get slider value and apply a mix pose
		"""
	
		# Obtenemos el valor del widget floatSliderGrp
		mixValue = cmds.floatSliderGrp(self.poseManUI["mixSlider"], q=1, v=1)
		
		# self.poseFullDataFromFilePose
		# self.poseFullDataFromViewport
		
		# Aqui calculamos la mezcla dependiendo del valor del slider, vamos pasando por los atributos
		# y vamos asignando la pose.
		#
		# Proceso muy lento, queda pendiente de optimizar		

		for i in range(len(self.poseFullDataFromFilePose)):
			
			# Sacamos los valores del original
			name_o = str(self.poseFullDataFromFilePose[i][0])
			attr_o = str(self.poseFullDataFromFilePose[i][1])
			valor_o = float(self.poseFullDataFromFilePose[i][2])
			
			# Sacamos los valores del target
			name_t = str(self.poseFullDataFromViewport[i][0])
			attr_t = str(self.poseFullDataFromViewport[i][1])
			valor_t = float(self.poseFullDataFromViewport[i][2])
			
			# Calculamos la mezcla  poseFullDataFromFilePose
			finalAttrValue = valor_t + (valor_o * mixValue - valor_t * mixValue)
			
			# Aplicamos la mezcla, esto es aplicar cada atributo con un nuevo valor
			cmds.setAttr(name_t+"."+attr_t, finalAttrValue)


	def foo(self, L):
			print L[0]
			print L[1]
			D = L[0]
			D2 = L[1]
			name_o = str(D[0])
			attr_o = str(D[1])
			valor_o = float(D[2])
			
			# Sacamos los valores del target
			name_t = str(D2[0])
			attr_t = str(D2[1])
			valor_t = float(D2[2])
			
			
			# Calculamos la mezcla  poseFullDataFromFilePose
			finalAttrValue = valor_t + (valor_o * self.mixValue - valor_t * self.mixValue)
			
			# Aplicamos la mezcla, esto es aplicar cada atributo con un nuevo valor
			cmds.setAttr(name_t+"."+attr_t, finalAttrValue)
	
	def sliderMix(self, sectionName, subSectionName, poseName, *args):
		"""
		Pose Mix Slider UI
		"""
		
		# obtenemos los datos de la pose desde el archivo
		self.poseFullDataFromFilePose = self.getPoseFullDataFromFilePose(sectionName, subSectionName, poseName)
		
		# con esos datos obtenemos los del visor
		self.poseFullDataFromViewport = self.getPoseFullDataOfViewportUsingFullDataFromFilePose(self.poseFullDataFromFilePose)

		if cmds.window("sliderMixWindow", exists=1):
			cmds.deleteUI("sliderMixWindow", window=1)
		
		self.poseManUI["sliderMixWindow"] = cmds.window("sliderMixWindow")
		cmds.columnLayout(adj=1)
		self.poseManUI["mixSlider"] = cmds.floatSliderGrp(h=100, adj=1, minValue=0, maxValue=1, dc=self.setMixPoseWithSliderValue, pre=3)
		cmds.showWindow("sliderMixWindow")					
	
	### NOT POSE MAN DEFS, DEBUGS DEFS
	def printDefs(file):
		f = open(file, "r")
		defs = []		
		lines = f.readlines()
		for line in lines:
			if "def " in line and not "#" in line and ":" in line and not "__init__" in line and not "printDefs" in line:
				defs.append(line.partition("def")[2][:-2][1:])
		
		f.close()
		return defs
		
	def getValidStringName (self, str):		
		cleanStr = None		
		cleanStr = re.sub("\W", "_", re.sub("^\s+", "", str))		
		return cleanStr
		
	"""
	---
	"""
	
	def movePoseUI(self, sectionName, subSectionName, poseName, *args):
		
		if cmds.window("movePoseWindow", exists=True):
			cmds.deleteUI("movePoseWindow", window=True)
			
		self.poseManUI["movePoseWindow"] = cmds.window("movePoseWindow", t="Move Pose")
		cmds.frameLayout(mh=5,mw=5,bv=0,lv=0)
		cmds.rowColumnLayout(numberOfRows=3)
		
		cmds.frameLayout(mh=10,mw=10,bv=0,lv=0)
		cmds.text(align="left", label="Enter new Group name for " + subSectionName)
		
		self.poseManUI["textFieldSubSectionName"] = cmds.textField(text=subSectionName, bgc=(0.7, 0.7, 0.8))
		cmds.setFocus(self.poseManUI["textFieldSubSectionName"])
		cmds.rowColumnLayout(cat=(1, "right", 1), numberOfColumns=2)
		cmds.button(l="Rename", c=partial(self.renameSubSection, sectionName, subSectionName))
		cmds.button(l="Cancel", c=partial(self.deleteMyUI, self.poseManUI["movePoseWindow"]))
		
		cmds.showWindow(self.poseManUI["movePoseWindow"])
		cmds.window(self.poseManUI["movePoseWindow"], e=1, w=300, h=100)	
		
		
		cmds.text(align="left", label="Section", p=mainCL)
		self.poseManUI["optionSection"] = cmds.optionMenu()
		
		for i in range(10):
			cmds.menuItem(label=str(i))
		
		
	def movePose(self, sectionName, subSectionName, poseName, targetSectionName, targetSubSectionName, *args):		

		# Get pose filenames
		xmlFile = self.characterDirectoryPath + "/" + sectionName + "/" + subSectionName + "/" + poseName + ".pose"
		imgFile = self.characterDirectoryPath + "/" + sectionName + "/" + subSectionName + "/" + "thumbs" + "/" + self.poseThumbnailSize[2] + "/" + poseName + ".png"
		
		# Construc source section/group path
		sourcePath = self.characterDirectoryPath + "/" + sectionName + "/" + subSectionName
		
		# Construct target section/group path for pose
		targetPath = self.characterDirectoryPath + "/" + targetSectionName + "/" + targetSubSectionName
		
		# move pose files (.pose y .png)
		shutil.move(xmlFile, targetPath+"/")
		shutil.rename(imgFile, targetPath+"/")
		
		# remove pose from pose configuration file
		self.removePoseFromFileConfig(sectionName, subSectionName, poseName)
		
		# remove pose layout from UI
		self.removePoseFromUI(sectionName, subSectionName, poseName)
		
		# add pose to xml config file
		# add pose to UI