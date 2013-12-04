"""
import modeling.polyShell.polyShell as polyShell
asd = polyShell.Win()
"""

#-----------------------------------------------------------------------------------------------
# Imports
#-----------------------------------------------------------------------------------------------
import sys
import os
import maya.OpenMaya as OpenMaya
import maya.cmds as mc

#-----------------------------------------------------------------------------------------------
# END Imports
#-----------------------------------------------------------------------------------------------


#-----------------------------------------------------------------------------------------------
# Global Variables and definitions
#-----------------------------------------------------------------------------------------------

#-----------------------------------------------------------------------------------------------
# END Global Varables and definitions
#-----------------------------------------------------------------------------------------------

#-----------------------------------------------------------------------------------------------
# Main functions 
#-----------------------------------------------------------------------------------------------
def ftb_gen_shell ():
	"""
	INPUTS:
		none
	OUTPUTS:
		none
	DESCRIPTION:
		main function of shell
		Custom Extrude with auto UVs for the border faces
		Shame on iurruty!
	AUTHOR:
		iurruty
	REVISION:
		001 reason: started
			changes: none
			by: iurruty
			on: 2011-07-19_10:10:42
		002 reason: ...
			changes: ...
			by: ...
			on:
	TOOLTYPE:
		ftb_ttyp_maya
	"""
	shell_UI()

def ftb_gen_shellSCP():
	mskNodes = mc.ls('*MSK',r=True)
	finalNodes = []
	for msk in mskNodes:
		shape = mc.listRelatives(msk,noIntermediate = True,shapes=True)
		if(mc.attributeQuery('shThickness',node=shape[0],ex=True)):
			finalNodes.append(msk)
	for fin in finalNodes:
		mc.select(fin)
		ftb_gen_shell_doIt(1.0,1.0,1)
#-----------------------------------------------------------------------------------------------
# END Main functions 
#-----------------------------------------------------------------------------------------------


#-----------------------------------------------------------------------------------------------
# Utility functions 
#-----------------------------------------------------------------------------------------------
def ftb_gen_shell_doIt(dist,distUV,div):
	if (mc.window('shellUiWin',q=True,exists=True)):
		mc.deleteUI('shellUiWin')
	#mc.loadPlugin( 'c:/ftb_mayaplugins/ppl/2011 x64/shellNode.mll')
	sel = mc.ls(sl=True)
	if(len(sel)!= 0):
		shape = mc.listRelatives(sel[0],noIntermediate = True,shapes=True)
		His = mc.listHistory(shape[0])
		shell = ''
		for h in His:
			if(mc.nodeType(h) == 'polyShell'):
				shell = h
		if(shell == ''):
			if(mc.attributeQuery('shThickness',node=shape[0],ex=True)):
				dist = mc.getAttr(shape[0]+'.shThickness')
			else:
				mc.addAttr(shape[0],ln="shThickness",at='double',dv=0)
				mc.setAttr(shape[0]+'.shThickness',e=True,keyable=True)
			if(mc.attributeQuery('shUvThickness',node=shape[0],ex=True)):
				distUV = mc.getAttr(shape[0]+'.shUvThickness')
			else:
				mc.addAttr(shape[0],ln="shUvThickness",at='double',dv=0)
				mc.setAttr(shape[0]+'.shUvThickness',e=True,keyable=True)
			if(mc.attributeQuery('shDiv',node=shape[0],ex=True)):
				div = mc.getAttr(shape[0]+'.shDiv')
			else:
				mc.addAttr(shape[0],ln="shDiv",at='long',dv=0,min=0)
				mc.setAttr(shape[0]+'.shDiv',e=True,keyable=True)
			faceInitalCount = mc.polyEvaluate(sel[0],f=True)
			mc.polyShell(thickness = dist,uvOffset = distUV);
			sel2 = mc.ls(sl=True)
			faceFinalCount = mc.polyEvaluate(sel[0],f=True)
			mc.addAttr(sel2[0],ln="div",at='long',min=0,dv=0)
			mc.setAttr(sel2[0]+'.div',e=True,keyable=True)
			mc.setAttr(sel2[0]+'.div',div)
			mc.addAttr(sel2[0],ln="splits",dt="string")
			mc.setAttr(sel2[0]+'.splits',e=True,keyable=True)
			mc.select((sel[0]+'.f[%i' % (faceInitalCount*2)+':%i' % faceFinalCount+']'))
			faceList = mc.ls(sl=True,fl=True)
			facesRings = makeFaceRingGroups(faceList)
			for faceRing in facesRings:
				mc.select(facesRings[faceRing])
				mc.ConvertSelectionToContainedEdges()
				mc.setAttr(sel2[0]+'.thickness',0.2)
				split = mc.polySplitRing(mc.ls(sl=True),ch=True,splitType=2,divisions=0,useEqualMultiplier=1,smoothingAngle=30,fixQuads=1)
				splits = mc.getAttr(sel2[0]+'.splits')
				if(splits == None):
					splits = ""
				mc.setAttr(sel2[0]+'.splits',("%s"%splits+"%s,"%split[0]),type="string")
				mc.connectAttr(sel2[0]+'.div', (split[0]+'.divisions'))
				mc.setAttr(sel2[0]+'.thickness',dist)
				
			mc.connectAttr(sel2[0]+'.thickness',shape[0]+'.shThickness')
			mc.connectAttr(sel2[0]+'.uvOffset',shape[0]+'.shUvThickness')
			mc.connectAttr(sel2[0]+'.div',shape[0]+'.shDiv')
		else:
			print('This mesh have a shellModifier allready!!!!!')
	else:
		mc.error("please select some mesh")


def makeFaceRingGroups(faceList):
	i = 0
	finalFaceList ={}
	for f in range(0,len(faceList),1):
		if(len(faceList) == 0):
			break
		mc.select(faceList[0])
		mc.GrowPolygonSelectionRegion();
		sel2 = mc.ls(sl=True,fl=True);
		remlist = list(set(sel2)& set(faceList));
		mc.select(remlist)
		mc.pickWalk(type="faceloop",d='right');
		ringList = mc.ls(sl=True,fl=True)
		mc.ConvertSelectionToContainedEdges()
		finalFaceList[i] = ringList
		faceList = list(set(faceList)-set(ringList))
		i = i + 1
		
	return(finalFaceList)

def deleteShellNode():
	sel = mc.ls(sl=True)
	for s in sel:
		shape = mc.listRelatives(s,noIntermediate = True,shapes=True)
		His = mc.listHistory(shape[0])
		shell = ''
		
		for h in His:
			if(mc.nodeType(h) == 'polyShell'):
				shell = h
		splits = mc.getAttr('%s'%shell+'.splits')
		polySplitsList = splits.split(',')
		for ps in polySplitsList:
			if(ps != ""):
				mc.delete(ps)
		print(shell)
		inputMesh = mc.listConnections( shell+'.inMesh', d=False, s=True,connections=True,p=True )		  
		outMesh = mc.listConnections( shell+'.outMesh', d=True, s=False,shapes=True,connections=True,p=True  )	  
		mc.connectAttr(inputMesh[1],outMesh[1],f=True)	
		mc.delete(shell)
#-----------------------------------------------------------------------------------------------
# END Utility functions 
#-----------------------------------------------------------------------------------------------


#-----------------------------------------------------------------------------------------------
# UI functions
#-----------------------------------------------------------------------------------------------
def shell_UI():
	if (mc.window('shellUiWin',q=True,exists=True)):
		mc.deleteUI('shellUiWin')
	window = mc.window('shellUiWin', title="Shell UI", iconName='Shell UI', widthHeight=(181, 77),s=False)
	mc.columnLayout( adjustableColumn=True )
	mc.rowLayout( numberOfColumns=2,adjustableColumn=True )
	mc.text(label='Thickness:')
	mc.textField('shellTickText',text='0.1' )
	mc.setParent('..')
	mc.rowLayout( numberOfColumns=2,adjustableColumn=True )
	mc.text(label='Uv Thickness:')
	mc.textField('shellUVTickText',text='0.1' )
	mc.setParent('..')
	mc.rowLayout( numberOfColumns=2,adjustableColumn=True )
	mc.text(label='Divisions:')
	mc.textField('shellDivText',text='0' )
	mc.setParent('..')
	mc.rowLayout( numberOfColumns=2,adjustableColumn=True )
	mc.button( label='Do It!', command=('polyShell.ftb_gen_shell_doIt(float(mc.textField(\'shellTickText\',query=True, text=True)),float(mc.textField(\'shellUVTickText\',query=True, text=True)),float(mc.textField(\'shellDivText\',query=True, text=True)))'),bgc=[0.0,0.5,0.0] )
	mc.button( label='Close', command=('mc.deleteUI(\"' + window + '\", window=True)'),bgc=[0.5,0.0,0.0] )
	mc.setParent('..')
	mc.button( label='Delete Shell', command=('ftb_gen_shell.deleteShellNode()'),bgc=[0.0,0.0,0.5] )
	
	mc.showWindow(window)
	
class Callback(object): 
	def __init__(self, func, *args, **kwargs): 
			self.func = func 
			self.args = args 
			self.kwargs = kwargs
	def __call__(self, *args): 
			return self.func( *self.args, **self.kwargs ) 

class Win(object):
	def __init__(self):
		if (mc.window('shellUiWin',q=True,exists=True)):
			mc.deleteUI('shellUiWin')
		window = mc.window('shellUiWin', title="Shell UI", iconName='Shell UI', widthHeight=(181, 77),s=False)
		mc.columnLayout( adjustableColumn=True )
		mc.rowLayout( numberOfColumns=2,adjustableColumn=True )
		mc.text(label='Thickness:')
		mc.textField('shellTickText',text='0.1' )
		mc.setParent('..')
		mc.rowLayout( numberOfColumns=2,adjustableColumn=True )
		mc.text(label='Uv Thickness:')
		mc.textField('shellUVTickText',text='0.1' )
		mc.setParent('..')
		mc.rowLayout( numberOfColumns=2,adjustableColumn=True )
		mc.text(label='Divisions:')
		mc.textField('shellDivText',text='0' )
		mc.setParent('..')
		mc.rowLayout( numberOfColumns=2,adjustableColumn=True )
		mc.button( label='Do It!', command = self.doShell,bgc=[0.0,0.5,0.0] )
		mc.button( label='Close', command=('mc.deleteUI(\"' + window + '\", window=True)'),bgc=[0.5,0.0,0.0] )
		mc.setParent('..')
		mc.button( label='Delete Shell', command= self.deleteShell,bgc=[0.0,0.0,0.5] )
		
		mc.showWindow(window)
 
	def doShell(self, *args ):
		ftb_gen_shell_doIt(float(mc.textField('shellTickText',query=True, text=True)),float(mc.textField('shellUVTickText',query=True, text=True)),float(mc.textField('shellDivText',query=True, text=True)))

	def deleteShell(self, *args):
		"""docstring for fname"""
		deleteShellNode()
	 	
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

#-----------------------------------------------------------------------------------------------
# END UI 
#-----------------------------------------------------------------------------------------------




