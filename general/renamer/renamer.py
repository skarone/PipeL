import general.mayaNode.mayaNode as mn
import maya.cmds as mc

"""
import general.renamer.renamer as rn
rn.renameSelection()
"""

def renameSelection():
	"""rename all the selected objects going 1 by 1"""
	sel = mn.ls( sl = True )
	for s in sel:
		s() #select
		mc.refresh()
		result = mc.promptDialog(
				title         = 'Rename Object ' + s.name,
				message       = 'Enter Name:',
				button        = ['OK', 'Cancel','Stop'],
				defaultButton = 'OK',
				tx            = s.name,
				cancelButton  = 'Cancel',
				dismissString = 'Cancel')
		if result == 'OK':
			text = mc.promptDialog(query=True, text=True)
			if '#' in text:
				similars = mn.ls( text.replace( '#', '*' ) )
				if not similars:
					similars = []
				s.name = text.replace( '#', str( len( similars ) ) )
			else:
				s.name = text
		if result == 'Stop':
			return

def renameSimilarObjects():
	result = mc.promptDialog(
		title         = 'Rename Object ' ,
		message       = 'Enter Name:',
		button        = ['OK', 'Cancel'],
		defaultButton = 'OK',
		cancelButton  = 'Cancel',
		dismissString = 'Cancel')
	if result == 'OK':
		text = mc.promptDialog(query=True, text=True)
		if '#' in text:
			sel = mn.ls( sl = True )
			i = 0
			for s in sel:
				s.name =  text.replace( '#', str( i ) )
				i += 1
				

