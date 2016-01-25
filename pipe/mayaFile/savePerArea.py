import pipe.mayaFile.mayaFile as mfl;
reload(mfl);
import general.utils.utils as gutils
import maya.cmds as mc
import shading.textureManager.textureManager as tm
import pipe.settings.settings as sti
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
		if '_final' in curFile.name.lower():# send mail to lighting department
			gen = sti.Settings().General
			sendMail = gen[ "sendmail" ]
			mailServer = gen[ "mailserver" ]
			mailPort = gen[ "mailport" ]
			mailsPath = gen[ "departmentspath" ]
			if sendMail:
				ml.mailFromTool( 'new_asset_publish',{
						'<AssetName>': ','.join( exportedAsset ),
						'<UserName>': os.getenv('username')},
						os.getenv('username') + '@bitt.com',
						mailsPath , mailServer, mailPort  )


def showMessage( msg ):
	"""display message"""
	result = mc.confirmDialog( title='Confirm', message=msg, button=['Save Anyway','Ok'], defaultButton='Save Anyway', cancelButton='Ok', dismissString='Ok' )
	return result
