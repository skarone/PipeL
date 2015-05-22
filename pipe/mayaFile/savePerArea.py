import pipe.mayaFile.mayaFile as mfl;
reload(mfl);
import general.utils.utils as gutils
import maya.cmds as mc
import shading.textureManager.textureManager as tm
reload(tm)

def customSavePerArea():
	"""docstring for customSavePerArea"""
	curFile = mfl.currentFile();
	result = True
	if '_shading' in curFile.name.lower() or '_model' in curFile.name.lower():
		transForms = gutils.transformsWithoutFreeze()
		texturesNotInServer = tm.Manager().texturesNotInServerPath()
		msg =''
		if transForms:
			msg = '-There are transforms without freeze!, please fix it\n'
		if texturesNotInServer:
			msg += '-There are textures that are not pointing to the server!, please fix it\n'
		if msg:
			result = showMessage( msg )
	if not result == 'Ok':
		curFile.newVersion();
		curFile.save()


def showMessage( msg ):
	"""display message"""
	result = mc.confirmDialog( title='Confirm', message=msg, button=['Save Anyway','Ok'], defaultButton='Save Anyway', cancelButton='Ok', dismissString='Ok' )
	return result
