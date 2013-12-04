"""
import skinning.skinFix as ftb_skf_benjaminButtons
reload(ftb_skf_benjaminButtons)
ftb_skf_benjaminButtons.ftb_skf_benjaminButtons()


"""

#-----------------------------------------------------------------------------------------------
# ImportsC:\Users\Ignacio\Downloads\Collect (1)\Collect
#-----------------------------------------------------------------------------------------------
import sys
import os
import time
import datetime
import cvShapeInverter


import maya.cmds as mc
import maya.mel as mm
	

def ftb_skf_benjaminButtons ():
	"""
	"""
	return openWindow()

def createFix():

	updateUser("write")
	
	if len(mc.ls(sl=True)) == 0:
		errorWindow(4)
		return
		
	fromFrame=mc.textField("fromField", q=True, tx=True)
	toFrame=mc.textField("toField", q=True, tx=True)
	fixDescription=mc.textField("fixDescriptionField", q=True, tx=True)
	if 'fix' in fixDescription:
		ftb_skf_benjaminButtons.errorWindow(8)
		return
	if 'FIX' in fixDescription:
		errorWindow(8)
		return
	if 'Fix' in fixDescription:
		errorWindow(8)
		return
	
	try:
		selectedMesh = (mc.ls(sl=True))[0]
	except:
		errorWindow(1)
		return
	
	if '_fix' in selectedMesh: 
		errorWindow(2)
		return

	selectedMeshNNS = selectedMesh.split(':')[1]

	cTime = mc.currentTime(q=True)
	
	if mc.objExists(selectedMesh+'_goalFix'):
		fixGroup = selectedMesh+'_fixBlends_GRP'
		goalFix = selectedMesh+'_goalFix'
		allFixes = mc.ls('*:*_fix*', typ = 'transform')
		fixList = []
		for fix in allFixes:
			if 'Inverted' not in fix:
				if 'SH' not in fix:
					if 'GRP' not in fix:
						if 'fixed' not in fix:
							if '_grp' not in fix:
								if '_f_' not in fix:
									fixList.append(int(fix.split('fix')[1]))
		bsCount = max(fixList)
	
	else: bsCount = 0
	
	#Desactiva temporalmente los fixes previos, y crea el newFix
	
	try:
		mc.setAttr(selectedMesh+'_goalFixBS'+'.'+selectedMeshNNS+'_goalFix', 0)
	except: 0
		
	newFix = mc.duplicate(selectedMesh, n=selectedMesh+'_'+formatText(fixDescription)+'_fix'+str(bsCount+1))[0]
	mc.polyColorPerVertex(newFix, r=0.3376, g=0.3674, b=0.6203, a=1, cdo=True)
	newFixInverted = cvShapeInverter.invert(selectedMesh, newFix, newFix+'Inverted')
	newFixInvertedNNS = newFixInverted.split(':')[1]
	mc.setAttr(newFixInverted+'.visibility', 0)
	
	mc.select(newFix, r=True)
	mc.addAttr(ln="fixDescription", dt='string')
	mc.addAttr(ln="fixFrame")
	mc.setAttr(newFix+'.fixDescription', fixDescription, type='string')
	mc.setAttr(newFix+'.fixFrame', cTime)
	
	try: 
		mc.setAttr(selectedMesh+'_goalFixBS'+'.'+selectedMeshNNS+'_goalFix', 1)
	except: 0
	
	#Prueba si existe el mesh goalFix. Si existe, agrega el newFixInverted al nodo blendshape existente. Si no existe, lo crea, crea el nodo blendshape con el newFixInverted.
	if mc.objExists(selectedMesh+'_goalFix'):
		fixGroup = selectedMesh+'_fixBlends_GRP'
		goalFix = selectedMesh+'_goalFix'
		allFixes = mc.ls('*:*_fix*',typ = 'transform')
		fixList = []
		for fix in allFixes:
			if 'Inverted' not in fix:
				if 'SH' not in fix:
					if 'GRP' not in fix:
						if 'fixed' not in fix:
							if '_grp' not in fix:
								if '_f_' not in fix:
									fixList.append(int(fix.split('fix')[1]))
		bsCount = max(fixList)
		mc.blendShape(selectedMesh+'FixesBS', edit=True, t=(goalFix, bsCount+1, newFixInverted, 1.0))
 
	else:
		goalFix = mc.duplicate(newFixInverted, n=selectedMesh+'_goalFix')[0]
		
		if mc.objExists(selectedMesh+'_goalFixBS') == False:
			mc.select(goalFix, r=True)
			mc.select(selectedMesh, add=True)
			goalFixBS = mc.blendShape(foc=True, n=selectedMesh+'_goalFixBS')[0] 
			mc.setAttr(goalFixBS+'.'+selectedMeshNNS+'_goalFix', 1)
		
		mc.setAttr(selectedMesh+'_goalFix.visibility', 0)
		fixGroup = mc.group(empty=True, name=selectedMesh+'_fixBlends_GRP', parent=selectedMesh)
		mc.parent(fixGroup, world=True)
		mc.parent(selectedMesh+'_goalFix', selectedMesh+'_fixBlends_GRP')
	
		#Crea el nodo blendshape con newFixInverted al goalFix
		mc.select(newFixInverted, r=True)
		mc.select(goalFix, add=True)
		mc.blendShape(foc=True, n=selectedMesh+'FixesBS')

	#Agrega el newFix y el newFixInverted al grupo fixBlends_GRP.
	mc.parent(newFix, fixGroup)
	mc.parent(newFixInverted, fixGroup)
	if mc.checkBox("noBegCheckBox", q=True, value=True) == False: 
		mc.setKeyframe(selectedMesh+'FixesBS', at=newFixInvertedNNS, v=1)
		mc.setKeyframe(selectedMesh+'FixesBS', at=newFixInvertedNNS, t=cTime-int(fromFrame), v=0)
		
	if mc.checkBox("noBegCheckBox", q=True, value=True) == True:
		mc.setKeyframe(selectedMesh+'FixesBS', at=newFixInvertedNNS, v=1)
		
	if mc.checkBox("noEndCheckBox", q=True, value=True) == False: 
		mc.setKeyframe(selectedMesh+'FixesBS', at=newFixInvertedNNS, t=cTime+int(toFrame), v=0)
		
	mc.select(newFix, r=True)
	mc.setAttr(selectedMesh+'.visibility', 0)
	
def updateCMFDict ():
	
	#Obtiene la lista de fixes
	
	fixList = []
	allFixes = mc.ls('*:*_fix*', typ = 'transform')
	for fix in allFixes:
		if 'Inverted' not in fix:
			if 'SH' not in fix:
				if 'GRP' not in fix:
					if 'fixed' not in fix:
						if '_grp' not in fix:
							if '_f_' not in fix:
								fixList.append (fix)


	CMFDict = {}

	for fix in fixList:
		char = fix.split(':')[0]
		if char not in CMFDict:
			CMFDict[char] = {}
	
	for fix in fixList:
		fixSplit = fix.split(':')
		char = fixSplit[0]
		fixRemove = '_' +fixSplit[1].split( '_' )[-2] + '_' + fixSplit[1].split( '_' )[-1]
		mesh = fixSplit[1].replace( fixRemove, '' )
		fix =  fixSplit[1]
		if mesh not in CMFDict[char]:
			CMFDict[char][mesh] = []
		if fix not in CMFDict[char][mesh]:
			CMFDict[char][mesh].append(fix)
	return CMFDict

#************

def updateChar():
	charNameList = []
	CMFDict = updateCMFDict()
	for char in CMFDict:
		charNameList.append(char)
	mc.textScrollList("meshScrollList", e=True, removeAll=True)       			
	mc.textScrollList("charScrollList", e=True, removeAll=True)
	mc.textScrollList("fixScrollList", e=True, removeAll=True)
	mc.textScrollList("charScrollList", e=True, append=charNameList)
	mc.textScrollList("charScrollList", e=True, selectIndexedItem=1)
	selectChar()
	
#************

def selectChar():
	selectedChar = mc.textScrollList("charScrollList", q=True, selectItem=True)[0]
	CMFDict = updateCMFDict()
	toAppend = []

	for mesh in CMFDict[selectedChar]:
		toAppend.append(mesh)
			
		
	mc.textScrollList("meshScrollList", e=True, removeAll=True, append=toAppend)
	mc.textScrollList("fixScrollList", e=True, removeAll=True)
	mc.textField("fixDescriptionEditField", e=True, text = "")

#************
	
def selectMesh():
	mc.textScrollList("fixScrollList", e=True, removeAll=True)
	selectedChar = mc.textScrollList("charScrollList", q=True, selectItem=True)[0]
	selectedMesh = mc.textScrollList("meshScrollList", q=True, selectItem=True)[0]

	CMFDict = updateCMFDict()
	toAppend = []

	toAppend.append(CMFDict[selectedChar][selectedMesh])
	
	for fix in toAppend[0]:
		print fix
		fixName = selectedChar+':'+fix
		inFrame = mc.getAttr(fixName+'.fixFrame')
		mc.textScrollList("fixScrollList", e=True, append=((fixName).split(':')[1]).split('_')[-2]+'_'+((fixName).split(':')[1]).split('_')[-1]+' ('+str('%i'%inFrame)+')')

	mc.textField("fixDescriptionEditField", e=True, text = "")

	simpleSelectMesh()

#************

def selectFix():
	
	selectedChar = mc.textScrollList("charScrollList", q=True, selectItem=True)[0]
	selectedMesh = mc.textScrollList("meshScrollList", q=True, selectItem=True)[0]
	selectedFix = (mc.textScrollList("fixScrollList", q=True, selectItem=True)[0]).split('(')[0]

	fixName = selectedChar+':'+selectedMesh + '_' + selectedFix[0:-1]
	
	fixDescription = mc.getAttr(fixName+'.fixDescription')
	mc.textField("fixDescriptionEditField", e=True, text=fixDescription)
	mc.select(fixName)
	
#************
	
def showHideFix():
	try:
		
		selectedChar = mc.textScrollList("charScrollList", q=True, selectItem=True)[0]
		selectedMesh = mc.textScrollList("meshScrollList", q=True, selectItem=True)[0]
		selectedFix = (mc.textScrollList("fixScrollList", q=True, selectItem=True)[0]).split('(')[0]
	
		fixName = selectedChar+':'+selectedMesh+'_'+selectedFix
		
		fixVisibility = mc.getAttr(fixName+'.visibility')
		if fixVisibility == 1:
			mc.setAttr(fixName+'.visibility', 0)
		else:
			mc.setAttr(fixName+'.visibility', 1)
	except: 0
	
#************
		
def showHideMesh():
	try:
		selectedChar = mc.textScrollList("charScrollList", q=True, selectItem=True)[0]
		selectedMesh = mc.textScrollList("meshScrollList", q=True, selectItem=True)[0]
		selectedCombined = selectedChar+':'+selectedMesh
		
		meshVisibility = mc.getAttr(selectedCombined+'.visibility')
		if meshVisibility == 1:
			mc.setAttr(selectedCombined+'.visibility', 0)
		else:
			mc.setAttr(selectedCombined+'.visibility', 1)
	except: 0
	
#************
		
def simpleSelectFix():
	try:
		selectedChar = mc.textScrollList("charScrollList", q=True, selectItem=True)[0]
		selectedMesh = mc.textScrollList("meshScrollList", q=True, selectItem=True)[0]
		selectedFix = (mc.textScrollList("fixScrollList", q=True, selectItem=True)[0]).split('(')[0]
	
		fixName = selectedChar+':'+selectedMesh+'_'+selectedFix
		
		mc.select(selectedFix, r=True)
	except: 0
	
#************
	
def simpleSelectMesh():
	try:
		selectedChar = mc.textScrollList("charScrollList", q=True, selectItem=True)[0]
		selectedMesh = mc.textScrollList("meshScrollList", q=True, selectItem=True)[0]
		selectedCombined = selectedChar+':'+selectedMesh
		
		mc.select(selectedCombined, r=True)
	except: 0
	
#************
	
def goToFixFrame():
	try:
		selectedChar = mc.textScrollList("charScrollList", q=True, selectItem=True)[0]
		selectedMesh = mc.textScrollList("meshScrollList", q=True, selectItem=True)[0]
		selectedFix = (mc.textScrollList("fixScrollList", q=True, selectItem=True)[0]).split('(')[0]
	
		fixName = selectedChar+':'+selectedMesh+'_'+selectedFix
		frame = mc.getAttr(fixName+'.fixFrame')
		if mc.currentTime(q=True) != frame:
			mc.currentTime(frame)
	except: 0

#************

def deleteFix():
	

		selectedChar = mc.textScrollList("charScrollList", q=True, selectItem=True)[0]
		selectedMesh = mc.textScrollList("meshScrollList", q=True, selectItem=True)[0]
		selectedFix = (mc.textScrollList("fixScrollList", q=True, selectItem=True)[0]).split('(')[0]
		
		fixName = selectedChar+':'+selectedMesh+ '_'+selectedFix
		meshName = selectedChar+':'+selectedMesh
	
		mc.blendShape(meshName+'FixesBS', edit=True, remove=True, g = (meshName+'_'+selectedFix)[0:-1]+'Inverted', t = ((meshName+'_'+selectedFix)[0:-1]+'Inverted', 1, (meshName+'_'+selectedFix)[0:-1]+'Inverted', 1.0))
		mc.delete(fixName)
		mc.delete(fixName+'Inverted')
		mc.setAttr(meshName+'.visibility', 1)
		if len(mc.listRelatives(meshName+'_fixBlends_GRP', children = True)) <= 1: 
			mc.delete(meshName+'_fixBlends_GRP')
			mc.delete(meshName+'_goalFixBS')
			
		mc.textField("fixDescriptionEditField", e=True, text = "")
		
		try: selectMesh()
		except: updateChar()


	
#************
	
def swap():
	try:
		goToFixFrame()
		selectedChar = mc.textScrollList("charScrollList", q=True, selectItem=True)[0]
		selectedMesh = mc.textScrollList("meshScrollList", q=True, selectItem=True)[0]
		selectedFix = (mc.textScrollList("fixScrollList", q=True, selectItem=True)[0]).split('(')[0]
	
		fixName = selectedChar+':'+selectedMesh+'_'+selectedFix
		meshName = selectedChar+':'+selectedMesh
		
		if mc.getAttr(fixName+'.visibility') == 1:
			mc.setAttr(fixName+'.visibility', 0)
			mc.setAttr(meshName+'.visibility', 1)
			
		else:
			mc.setAttr(fixName+'.visibility', 1)
			mc.setAttr(meshName+'.visibility', 0)
			
	except: 0
	
#************
	
def updateDescription():
	
	try:
	
		selectedChar = mc.textScrollList("charScrollList", q=True, selectItem=True)[0]
		selectedMesh = mc.textScrollList("meshScrollList", q=True, selectItem=True)[0]
		selectedFix = (mc.textScrollList("fixScrollList", q=True, selectItem=True)[0]).split('(')[0]
	
		fixName = selectedChar+':'+selectedMesh+'_'+selectedFix
		
		descrp = mc.textField("fixDescriptionEditField", q=True, text=True)
		mc.setAttr(fixName+'.fixDescription', descrp, type="string")
		
		mc.rename(fixName, fixName+formatText(descrp)+'_fix'+selectedFix.split('fix')[1])
		mc.rename(fixName+'Inverted', fixName+formatText(descrp)+'_fix'+selectedFix.split('fix')[1][0:-1]+'Inverted')
		selectMesh()
		
	except: 0
	
#************

def done():
	selection = mc.ls(sl=True)[0]
	selSplit = selection.split( '_' )
	mesh = selection.replace(  '_' + selSplit[-2] + '_' + selSplit[-1], '' )
	mc.setAttr(selection+'.visibility', 0)
	mc.setAttr(mesh+'.visibility', 1)
	mc.select(mesh)

#************

def frameUpdate():
	fixList = []
	allFixes = mc.ls('*:*_fix*',typ = 'transform')
	for fix in allFixes:
		if 'Inverted' not in fix:
			if 'SH' not in fix:
				if 'GRP' not in fix:
					if 'fixed' not in fix:
						if '_grp' not in fix:
							if '_f_' not in fix:
								fixList.append(fix)
						
	for fix in fixList:
		mc.setAttr(fix+'.visibility', 0)	
		selSplit = fix.split( '_' )
		mc.setAttr(fix.replace(  '_' + selSplit[-2] + '_' + selSplit[-1], '' )+'.visibility', 1)
		
#************

def simpleSelectChar():
	try:
		selectedChar = mc.textScrollList("charScrollList", q=True, selectItem=True)[0]
		char = mc.ls(selectedChar+':*', dagObjects=True)
		mc.select(char, r=True)
	except: 0
	
#************

def formatText(text):
	wordList = text.split(' ')
	finalString = ''
	for word in wordList:
		if finalString == '':
			finalString = word.lower()
		else: 
			finalString = finalString + word[0].upper() + word[1:].lower()
	
	nullChars = ['.', ',', '-', '_', '*', '/', '&', '%', '!', '(', ')']
	
	for char in nullChars:
		finalString = finalString.replace(char, '')

	if finalString == '': return 'NoDescription'	
	else: return finalString
	
#************
	
def errorWindow(error):
	if mc.window('errorWindow',ex=1):
		mc.deleteUI('errorWindow')
	
	mc.window('errorWindow', title='Error '+str(error), minimizeButton = False, maximizeButton = False, titleBarMenu = False, toolbox = True, bgc=[0.65,0.55,0.45], wh=(100, 300), sizeable=True)
	mc.columnLayout(columnAlign = 'center', rowSpacing = 10, columnAttach = ['both', 5], columnWidth = 400)
	mc.text('Error '+str(error))
	mc.separator()
	mc.text(label='')
	if error == 1:
		mc.text('Nothing selected. Select a base mesh to add fixes.')
	if error == 2:
		mc.text('Cannot create a fix over another fix. Select a base mesh instead.')
	if error == 3:
		mc.text('You must select a mesh (__MSK) to import/export.')
	if error == 4:
		mc.text('You must select a mesh (__MSK) to create a fix.')
	if error == 5:
		mc.text('File not found.')
	if error == 6:
		mc.text('WARNING: This file contains fixes from fixBlends.')
	if error == 7:
		mc.text('Error while saving the information.')
		mc.text('Please verify that you have not used any illegal characters such as accents.')
	if error == 8:
		mc.text('Please avoid using the word FIX in the fix description. It messes everything up.')
		mc.text('Thank you.')
		
	mc.text(label='')
	mc.button('ok', label = 'Ok', bgc = [0.608, 0.534, 0.354], command='mc.deleteUI("errorWindow")')
	mc.showWindow('errorWindow')
	mc.text(label='')
	
#************

def importFix():
	
	if len(mc.ls(sl=True)) == 0:
		errorWindow(3)
		return
		
	if (mc.ls(sl=True)[0])[-3:] != 'MSK':
		errorWindow(3)
		return
	
	selectedChar = (mc.ls(sl=True)[0]).split(':')[0]
	selectedMesh = (mc.ls(sl=True)[0]).split(':')[1]
	meshName = 'anm:'+selectedChar+':'+selectedMesh
	selectedGroup = 'anm:'+selectedChar+':'+selectedMesh+'_fixBlends_GRP'
	filename = ((mc.file(q=True, sn=True)).split('/')[-1]).split('_')[0]

	currentSequence = filename[0:7]
	currentShot = filename[7:11]

	try: 
		mc.delete(meshName+'_fixBlends_GRP')
		mc.delete(meshName+'_goalFixBS')
	except: 0
	
	path = 'P:/sequences/'+currentSequence+'/shots/'+currentShot+'/skinfix/fixdata/'+selectedChar+'-'+selectedMesh+'-fixBlends.ma'
	
	try:
		mc.file(path, i=True)
	except: 
		errorWindow(5)
		return
		
	mc.namespace(set=':')
	preListToRename = mc.ls('anm1:*:*')
	fixBlendsGRP = mc.ls('anm1:*:*fixBlends_GRP')

	goalFix = 'anm:'+selectedChar+':'+selectedMesh+'_goalFix'
	
	toRename = []
	for e in preListToRename:
		if 'SH' not in e:
			toRename.append(e)
			
		if 'SHDG' in e:
			toRename.append(e)
	
	for e in toRename:
		mc.rename(e, 'anm'+':'+e.split(':')[1]+':'+e.split(':')[1])
		
	mc.namespace(rm='anm1:'+selectedChar)
	mc.namespace(rm='anm1')
	
	mc.select(goalFix, r=True)
	mc.select('anm:'+selectedChar+':'+selectedMesh, add=True)
	goalFixBS = mc.blendShape(foc=True, n='anm:'+selectedChar+':'+selectedMesh+'_goalFixBS')[0] 
	mc.setAttr(goalFixBS+'.'+selectedMesh+'_goalFix', 1)
	
	updateChar()
	
#************

def exportFix():
	if len(mc.ls(sl=True)) == 0:
		errorWindow(3)
		return
		
	if (mc.ls(sl=True)[0])[-3:] != 'MSK':
		errorWindow(3)
		return
	
	selectedChar = (mc.ls(sl=True)[0]).split(':')[1]
	selectedMesh = (mc.ls(sl=True)[0]).split(':')[1]
	selectedGroup = 'anm:'+selectedChar+':'+selectedMesh+'_fixBlends_GRP'
	filename = ((mc.file(q=True, sn=True)).split('/')[-1]).split('_')[0]
	

	currentSequence = filename[0:7]
	currentShot = filename[7:11]
	
	path = 'P:/sequences/'+currentSequence+'/shots/'+currentShot+'/skinfix/fixdata/'+selectedChar+'-'+selectedMesh+'-fixBlends'
	mc.select(selectedGroup)
	mc.file(path, exportSelected = True, constructionHistory = True, channels = True, shader = True, expressions = False, type = 'mayaAscii')

#************

def updateSkinfixInfo(mode):
	descriptionText = ''
	prevDescriptionText = ''
	
	filename = ((mc.file(q=True, sn=True)).split('/')[-1]).split('_')[0]
	currentSequence = filename[0:7]
	currentShot = filename[7:11]
		
	path = 'P:/sequences/'+currentSequence+'/shots/'+currentShot+'/skinfix/fixdata/skinfixInfo.txt'
	
	if mode == 'update':		
		if mc.window('confirmUpdateSkinfixInfoWindow',ex=1):
			mc.deleteUI('confirmUpdateSkinfixInfoWindow')
	
		mc.window('confirmUpdateSkinfixInfoWindow', title='Confirm file update', minimizeButton = False, maximizeButton = False, titleBarMenu = False, toolbox = True, bgc=[0.65,0.55,0.45], wh=(100, 300), sizeable=False)
		mc.columnLayout(columnAlign = 'center', rowSpacing = 10, columnAttach = ['both', 5], columnWidth = 400)
		mc.text('Confirm file update')
		mc.separator()
		mc.text(label='')
		mc.text(label='Are you sure you want to save/overwrite skinfixInfo.txt?')
		mc.text(label='If existent, previous info will be replaced.')
		mc.text(label='')
		mc.button(label='Yes', bgc = [0.608, 0.534, 0.354], command='mc.deleteUI("confirmUpdateSkinfixInfoWindow"); ftb_skf_benjaminButtons.updateSkinfixInfo("doUpdate")')
		mc.button(label='Cancel', bgc = [0.608, 0.534, 0.354], command='ftb_skf_benjaminButtons.updateSkinfixInfo("read"); mc.deleteUI("confirmUpdateSkinfixInfoWindow")')
		mc.text(label='')
		mc.showWindow('confirmUpdateSkinfixInfoWindow')
		
	if mode == 'doUpdate':
		
		try:
			if mc.textField('skinfixInfoTextField', q=True, tx=True) == '': 
				try:
					f = open(path, 'r')
					descriptionText = f.read()
					mc.textField('skinfixInfoTextField', e=True, tx=descriptionText)
				except: 0
		
			else:
				descriptionText = mc.textField('skinfixInfoTextField', q=True, tx=True)
				try:
					f = open(path, 'r')
					prevDescriptionText = f.read()
				except: 0
				f = open(path, 'w')
				f.write(descriptionText)
		except:
			
			try:
				f = open(path, 'w')
				f.write(prevDescriptionText)
				
			except: 0
			
			errorWindow(7)
			return
			
	if mode == 'read':
		mc.textField('skinfixInfoTextField', e=True, tx='')
		try:
			f = open(path, 'r')
			descriptionText = f.read()
			mc.textField('skinfixInfoTextField', e=True, tx=descriptionText)
		except: 0
	
#************
		
def externalTools(option):
	
	if option == 1:
		sys.path.append('t:/skf/ftb_skf_sceneBuilder')
		import ftb_skf_sceneBuilder as ftb_skf_sceneBuilder
		reload (ftb_skf_sceneBuilder)
		ftb_skf_sceneBuilder.ftb_skf_sceneBuilder()
		
	if option == 2:
		sys.path.append('t:/ppl/ftb_ppl_playblast')
		import ftb_ppl_playblast
		reload (ftb_ppl_playblast)
		ftb_ppl_playblast.ftb_ppl_playblast("skinfix")
		
	if option == 3:
		sys.path.append('t:/skf/ftb_skf_sceneBuilder')
		import ftb_skf_sceneBuilder as ftb_skf_sceneBuilder
		reload (ftb_skf_sceneBuilder)
		ftb_skf_sceneBuilder.exportSceneCache()
		
	if option == 4:
		import sim.ftb_sim_hairBringer.ftb_sim_hairBringer as ftb_sim_hairBringer
		reload (ftb_sim_hairBringer)
		ftb_sim_hairBringer.ftb_sim_hairBringerSel(skin=0,force=1)
		
#************

def updateUser(mode):
	
	currentUser = os.environ.get( "USERNAME" )
	dateTime = str(datetime.datetime.now())[0:19]
	toWrite = currentUser+', '+dateTime
	filename = ((mc.file(q=True, sn=True)).split('/')[-1]).split('_')[0]
	currentSequence = filename[0:7]
	currentShot = filename[7:11]
		
	path = 'P:/sequences/'+currentSequence+'/shots/'+currentShot+'/skinfix/fixdata/userInfo.txt'

	if mode == 'write':
		try:
			f = open(path, 'w')
			f.write(toWrite)
			mc.text('userText', e=True, label=toWrite)
		except: 0
	
	if mode == 'read':
		try:
			f = open(path, 'r')
			toRead = f.read()
			mc.text('userText', e=True, label=toRead)
		except: 0
#-----------------------------------------------------------------------------------------------
# END Utility functions 
#-----------------------------------------------------------------------------------------------


#-----------------------------------------------------------------------------------------------
# UI functions
#-----------------------------------------------------------------------------------------------

#-----------------------------------------------------------------------------------------------
# END UI functions
#-----------------------------------------------------------------------------------------------

#-----------------------------------------------------------------------------------------------
# Classes
#-----------------------------------------------------------------------------------------------

#-----------------------------------------------------------------------------------------------
# END Classes
#-----------------------------------------------------------------------------------------------


#-----------------------------------------------------------------------------------------------
# UI 
#-----------------------------------------------------------------------------------------------
def openWindow():
	if mc.window('bBWindow',ex=1):
		mc.deleteUI('bBWindow')
	
	if mc.objExists('frameUpdate') == False: 
		mc.expression(n='frameUpdate', s='python(\"ftb_skf_benjaminButtons.frameUpdate()\")')
			
	mc.namespace(set=':')
	charList = []
	allList = mc.ls('*:*_fixBlends_GRP')
	for e in allList:
		if e.split(':')[1] not in charList:
			charList.append(e.split(':')[1])
	
	mc.window('bBWindow', title='benjaminButtons v1.68', wh=(100, 300), bgc=[0.65,0.55,0.45], sizeable=True)
	form = mc.formLayout()
	tabs = mc.tabLayout(innerMarginWidth=5, innerMarginHeight=5, selectCommand='ftb_skf_benjaminButtons.updateChar(); ftb_skf_benjaminButtons.updateSkinfixInfo("read"); ftb_skf_benjaminButtons.updateUser("read")')
	mc.formLayout(form, edit=True, attachForm=((tabs, 'top', 05), (tabs, 'left', 10), (tabs, 'bottom', 10), (tabs, 'right', 10)))
	

#******

	tab1 = mc.columnLayout('tab1', columnAlign = 'center', rowSpacing = 5, columnWidth = 100)
	mc.rowColumnLayout('createFixColumnLayout', rowSpacing = [1, 10], numberOfColumns = 2)
	mc.text(label='')
	mc.text(label='')
	mc.text(label='Frames before:')
	mc.textField("fromField", width=30, tx='2', bgc=[0.5,0.5,0.5])

	mc.text(label='Frames after:')
	mc.textField("toField", width=30, tx='2', bgc=[0.5,0.5,0.5])
	mc.separator(w=100)
	mc.separator(w=100)
	mc.text(label='Fix description:')
	mc.textField("fixDescriptionField", width=60, tx='', bgc=[0.40,0.40,0.40])
	mc.separator(w=100)
	mc.separator(w=100)
	mc.checkBox("noBegCheckBox", label = 'No beggining', onCommand = 'mc.textField("fromField", e=True, editable = False)', offCommand = 'mc.textField("fromField", e=True, editable = True, bgc=[0.5,0.5,0.5])')
	mc.text(label='')
	mc.checkBox("noEndCheckBox", label = 'No end', onCommand = 'mc.textField("toField", e=True, editable = False)', offCommand = 'mc.textField("toField", e=True, editable = True, bgc=[0.5,0.5,0.5])')
	mc.text(label='')	
	mc.separator()
	mc.separator()
	mc.button(label='Create fix', bgc = [0.296, 0.337, 0.570], command='ftb_skf_benjaminButtons.createFix()')

	mc.button(label='Done!', bgc = [0.343, 0.570, 0.296], command='ftb_skf_benjaminButtons.done()')
	mc.setParent( '..' )	
	mc.setParent( '..' )
#******
	tab2 = mc.rowColumnLayout('tab2', numberOfColumns=4)

	mc.text(label='')
	mc.text(label='')
	mc.text(label='')
	mc.text(label='')
	mc.text(label='Character')
	mc.text(label='Mesh')
	mc.text(label='Fix')
	mc.text(label='')
	mc.separator()
	mc.separator()
	mc.separator()
	mc.separator()
	mc.text(label='')
	mc.text(label='')
	mc.text(label='')
	mc.text(label='')
	mc.textScrollList("charScrollList", allowMultiSelection=False, w=125, bgc=[0.5,0.5,0.5], selectCommand='ftb_skf_benjaminButtons.selectChar()')
	mc.textScrollList("meshScrollList", allowMultiSelection=False, w=125, bgc=[0.5,0.5,0.5], selectCommand='ftb_skf_benjaminButtons.selectMesh()')
	mc.textScrollList("fixScrollList", allowMultiSelection=False, w=125, bgc=[0.5,0.5,0.5], selectCommand='ftb_skf_benjaminButtons.selectFix()')

	selectedChar = mc.textScrollList("charScrollList", q=True, selectItem=True)

	mc.button(label='Update', bgc = [0.608, 0.534, 0.354], command='ftb_skf_benjaminButtons.updateChar()')
	mc.button(label='Select char', bgc = [0.608, 0.534, 0.354], command='ftb_skf_benjaminButtons.simpleSelectChar()')
	mc.text(label='')
	mc.textField("fixDescriptionEditField", width=100, tx="", bgc=[0.40,0.40,0.40], aie=True, enterCommand='ftb_skf_benjaminButtons.updateDescription()')
	mc.button(label='Update description', bgc = [0.608, 0.534, 0.354], command='ftb_skf_benjaminButtons.updateDescription(); ftb_skf_benjaminButtons.updateSkinfixInfo("read"); ftb_skf_benjaminButtons.updateUser("read")')
	mc.text(label='')
	mc.text(label='')
	mc.text(label='')
	mc.text(label='')
	mc.separator()
	mc.separator()
	mc.separator()
	mc.separator()
	mc.text(label='')
	mc.text(label='')
	mc.text(label='')
	mc.text(label='')
	mc.button(label='Swap mesh/fix', bgc = [0.320, 0.260, 0.342], command='ftb_skf_benjaminButtons.swap()')
	mc.button(label='Show/hide fix', bgc = [0.608, 0.534, 0.354], command='ftb_skf_benjaminButtons.showHideFix()')
	mc.button(label='Show/hide mesh', bgc = [0.608, 0.534, 0.354], command='ftb_skf_benjaminButtons.showHideMesh()')

	mc.button(label='Go to fix frame', bgc = [0.608, 0.534, 0.354], command='ftb_skf_benjaminButtons.goToFixFrame()')
	mc.text(label='')
	mc.text(label='')
	mc.text(label='')
	mc.text(label='')
	mc.text(label='')
	mc.text(label='')
	mc.text(label='')
	mc.button(label='Delete fix', bgc = [0.570, 0.309, 0.296], command='ftb_skf_benjaminButtons.deleteFix()')
	mc.text(label='')
	mc.text(label='')
	mc.text(label='')
	mc.text(label='')
	mc.separator()
	mc.separator()
	mc.separator()
	mc.separator()
	mc.separator()
	mc.separator()
	mc.separator()
	mc.separator()
	mc.text(label='')
	mc.text(label='')
	mc.text(label='')
	mc.text(label='')
	mc.button(label='Import mesh fixes', bgc = [0.575, 0.38, 0.175], command='ftb_skf_benjaminButtons.importFix()')
	mc.button(label='Export mesh fixes', bgc = [0.575, 0.38, 0.175], command='ftb_skf_benjaminButtons.exportFix()')
	mc.text(label = '                                                 ')
	mc.button(label='Update User', bgc = [0.6, 0.6, 0.6], command='ftb_skf_benjaminButtons.updateUser("write")')
	mc.text(label='')
	mc.text(label='')
	mc.text(label='')
	mc.text(label = 'Last fix:', fn = "smallPlainLabelFont")
	mc.text(label='')
	mc.text(label='')
	mc.text(label='')
	mc.text('userText', label = 'No user record', fn = "smallBoldLabelFont")
	mc.setParent( '..' )
	
#******
	tab3 = mc.rowColumnLayout('tab3', numberOfColumns=1)
	
	mc.text(label='')
	mc.text(label='Skinfix dept. information about this shot:')
	mc.text(label='')
	mc.textField('skinfixInfoTextField', width = 560, height = 300, tx="", bgc=[0.40,0.40,0.40], aie=True, enterCommand='ftb_skf_benjaminButtons.updateSkinfixInfo("update")')

	mc.text(label='')
	mc.separator()
	mc.text(label='')
	mc.button(label='Read info', bgc = [0.575, 0.38, 0.175], command='ftb_skf_benjaminButtons.updateSkinfixInfo("read")')
	mc.text(label='')
	mc.button(label='Update info', bgc = [0.575, 0.38, 0.175], command='ftb_skf_benjaminButtons.updateSkinfixInfo("update")')



	mc.setParent( '..' )
	
#******
	
	tab4 = mc.rowColumnLayout('tab4', numberOfColumns=1)
	mc.text(label='')
	mc.button(label='Make Skinfix startup scene', width = 560, bgc = [0.575, 0.38, 0.175], command='ftb_skf_benjaminButtons.externalTools(1)')
	mc.text(label='')
	mc.button(label='Playblast window', bgc = [0.575, 0.38, 0.175], command='ftb_skf_benjaminButtons.externalTools(2)')
	mc.text(label='')

	mc.button(label='Export scene cache window', bgc = [0.575, 0.38, 0.175], command='ftb_skf_benjaminButtons.externalTools(3)')

	mc.text(label='')
	mc.button(label='Update hair to selected characters', bgc = [0.575, 0.38, 0.175], command='ftb_skf_benjaminButtons.externalTools(4)')

	mc.setParent( '..' )
	
#******	

	mc.tabLayout(tabs, edit=True, tabLabel=((tab1, 'Create fixes'), (tab2, 'Edit fixes'), (tab3, 'Skinfix info'), (tab4, 'External tools')))
	
	if mc.objExists('*:*_fixBlends_grp'):
		errorWindow(6)
	mc.showWindow('bBWindow')
#-----------------------------------------------------------------------------------------------
# END UI 
#-----------------------------------------------------------------------------------------------



#eof
