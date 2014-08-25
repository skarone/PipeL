'''
File: batcher.py
Author: Ignacio Urruty
Description:
	Tool to do a batch of a script in a maya file
'''
#-----------------------------------------------------------------------------------------------
# Imports
#-----------------------------------------------------------------------------------------------
import sys
import os
import subprocess
import shutil
import imp

def batcher(modules = [], functions = [], mayaFiles = [],makeBckp = False,makeLog = False,localRepoPath = 'F:',help = False):
	""" create a Batch file """
	helpText = 'This script is for run an array of scripts\n'
	helpText += '(mel or python) in an array of maya files.\n'
	#helpText += 'The functions array will be executed in order.\n'
	helpText += 'WARNING:\n'
	helpText += '\tFor every module you need a function!!\n'
	helpText += '\tIf the function has the same name of the module,\n'
	helpText += '\tYou can leave the item in the function array empty-->\'\'\n'
	helpText += 'USAGE Ex:\n'
	helpText += '\tbatcher(\n'
	helpText += '\tmodules = [\'t:/lay/ftb_lay_importExportCamaraFromLayout\',\'t:/mel/ftb_mel_cameraSequence.mel\']\n'
	helpText += '\t,functions = [\'ftb_lay_importExportCamaraFromLayout.fixThisCameraScene()\',\'cameraSequence\']\n'
	helpText += '\t,mayaFiles = [\'C:/pol/270ride010a_lay_camera_v003.ma\',\'C:/skarone/666ride666a_lay_camera_v666.ma\']\n'
	helpText += '\t,makeBckp = True  (This will make a back up of the file before edit)\n'
	helpText += '\t,makeLog = True  (This will make a log of the batch per file in the same path))\n'
	helpText += '\t,localRepoPath = \'F:\' (this is the path of the local repository of fuzion)'
	if (help):
		print helpText
		return False
	if not (len(mayaFiles)):
		print '>>please give me some maya Files'
		print '>>use batchFiles(help=True) for more information'
		return False
	if not (len(modules)):
		print '>>please give me some module'
		print '>>use batchFiles(help=True) for more information'
		return False
	if not (len(functions)):
		print '>>please give me some function'
		print '>>use batchFiles(help=True) for more information'
		return False
	if not (len(functions) == len(modules)):
		print '>>the lenght of the functions array is'
		print '>>not the same of the modules array'
		print '>>use batchFiles(help=True) for more information'
		return False
	#CREATE THE COMMAND TO EXECUTE
	cmd = ''
	cmd +='python (\\"import sys\\");' 
	for n,mod in enumerate(modules):
		#module exists???
		"""
		if not os.path.exists(mod):
			print '>>can\'t find module',mod
			return False;
		"""
		#detect if it is mel or python
		if(os.path.isfile(mod)):
			#probably is a mel
			filepath, fileMod = os.path.split(mod)
			file, fileExtension = os.path.splitext(fileMod)
			if not(fileExtension == 'mel'):
				print '>>this file isn\'t a python or a mel module',mod
				return False;
			else:
				#is a mel =) source
				cmd += 'source \"'+mod+'\";'
				if(functions[n] == ''):
					cmd += ''+file+';'
				else:
					cmd += ''+functions[n]+';'
		elif(os.path.isdir(mod)):
			#is a python =) module
			mod.replace('\\','/')
			m = mod.split('/')[-1]
			cmd +='python (\\"sys.path.append(\''+mod+'\')\\");'
			cmd +='python (\\"import '+m+'\\");'
			cmd +='python (\\"reload( '+m+')\\");'
			if(functions[n] == ''):
				cmd +='python (\\"'+m+'.'+m+'()'+'\\");'
			else:
				cmd +='python (\\"'+functions[n]+'\\");'
		else:
			print '>>something in this module is wrong',mod
			return False
	
	#LOOP THRU THE FILES
	for fileName in mayaFiles:
		finalcmd = cmd
		#fileName = fileName.replace('\\','/')
		if not os.path.exists(fileName):
			print '>>cant find file',fileName
			continue;
		if (makeBckp):
			backup = fileName.replace('.ma','_bckp.ma')
			print '>>backup made at',backup
			shutil.copy(fileName, backup)
			renFile = fileName.replace('\\','/')
			finalcmd +='file -rename \\"'+renFile+'\\";'
			finalcmd +='file -save;'
		finalcmd +='print (\\"done!\\n\\");'
		
		batch = ''
		batch +='C:\\Program Files\\Autodesk\\Maya2013\\bin\\mayabatch.exe -file "'+fileName+'" '
		batch +='-command "'+finalcmd+'" '
		
		if(makeLog):
			log = fileName.replace('.ma','.log')
			print log
			batch +=' -log "'+log+'"'
		print '>>about to execute',batch
		subprocess.call(str(batch))
		#os.system(batch)
		if(makeLog):
			subprocess.call('notepad.exe "'+log+'"')
	return


def module_exists( module_name ):
	try:
		imp.find_module( module_name )
		found = True
	except ImportError:
		found = False
	return found


