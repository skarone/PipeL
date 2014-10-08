'''
File: deadline.py
Author: Ignacio Urruty
Description: deadline helper, to create jobs and start render


Render current Frame:
import render.deadline.deadline as dl
reload( dl )
import pipe.mayaFile.mayaFile as mfl
dead = dl.Deadline()
groups = dead.groups
Job = dl.Job( {'Group':groups[6]},{}, mfl.currentFile() )
Job.write()
dead.runMayaJob( Job )
'''

import pipe.file.file as fl
reload( fl )
try:
	import maya.cmds as mc
except:
	pass
import subprocess

class Job(object):
	"""docstring for job"""
	def __init__(self, name, infoDict, pluginDict, mayaFile):
		self._mayaFile = mayaFile
		self._infoDict = {
				'Plugin'                             : 'MayaBatch',
				'ForceReloadPlugin'                  : 'false',
				'Frames'                             : '101-240',
				'ChunkSize'                          : '5',
				'Priority'                           : '50',
				'Pool'                               : 'none',
				'TaskTimeoutMinutes'                 : '0',
				'Name'                               : self._mayaFile.name,
				'EnableAutoTimeout'                  : 'False',
				'ConcurrentTasks'                    : '1',
				'LimitConcurrentTasksToNumberOfCpus' : 'True',
				'MachineLimit'                       : '0',
				'Whitelist'                          : '',
				'LimitGroups'                        : '',
				'Group'                              : 'none',
				'JobDependencies'                    : '',
				'OnJobComplete'                      : 'Nothing',
				'Department'                         : 'unknown',
				'Comment'                            : 'I dont put comments because i am lazy',
				'InitialStatus'                      : "Suspended"
				}
		version = mc.about( version=True )
		if version == '2015':
			version  = '2011'
		if version == '2014':
			version  = '2012'
		self._pluginDic = {
				'Version'                   : version,
				'Build'                     : '64bit',
				'StrictErrorChecking'       : 'False',
				'LocalRendering'            : 'False',
				'ProjectPath'               : '',
				'MaxProcessors'             : '0',
				'Renderer'                  : 'File',
				'CommandLineOptions'        : '',
				'IgnoreError211'            : 'False'
				}
		self._name = name
		for k,v in infoDict.items():
			self._infoDict[k]=v
		for k,v in pluginDict.items():
			self._pluginDic[k]=v

	@property
	def name(self):
		"""docstring for name"""
		return self._name

	@property
	def mayaFile(self):
		"""return maya file"""
		return self._mayaFile

	@property
	def infoDict(self):
		"""return info dict"""
		return self._infoDict

	@property
	def pluginDict(self):
		"""return info dict"""
		return self._pluginDic

	def write(self):
		"""write infoDict to file"""
		data = ''
		for k,v in self.infoDict.items():
			data += str(k)+'='+str(v)+'\n'
		self.infoDictFile.write( data )
		data = ''
		for k,v in self.pluginDict.items():
			data += str(k)+'='+str(v)+'\n'
		self.pluginDictFile.write( data )

	@property
	def infoDictFile(self):
		"""return the path of the infoDict File"""
		return fl.File( Deadline().userHomeDirectory + '/' + self.name + '_' + self.mayaFile.name + '_job_info.job' )

	@property
	def pluginDictFile(self):
		"""return the path of the infoDict File"""
		return fl.File( Deadline().userHomeDirectory + '/' + self.name + '_' + self.mayaFile.name + '_plugin_info.job' )

class Deadline(object):
	"""manage deadline render"""
	def __init__(self):
		pass

	def runMayaJob( self, job ):
		"""docstring for """
		command = '"'+job.infoDictFile.path+'" "'+job.pluginDictFile.path+'" "'+job.mayaFile.path+'"\n'
		out, err = self.run( command )
		print out
		deadlineJobId = out.split('\r\n')[-2].split('JobID=')[-1]
		return out, err, deadlineJobId

	def run(self, command):
		"""run command with deadlinecommand.exe"""
		startupinfo = subprocess.STARTUPINFO()
		startupinfo.dwFlags |= subprocess.STARTF_USESHOWWINDOW
		print "running command: ", command
		p = subprocess.Popen( "deadlinecommand " + command, startupinfo=startupinfo, stdin=subprocess.PIPE, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
		out, err = p.communicate()
		p.stdin.close()
		return out, err

	@property
	def pools(self):
		"""return pools in deadline"""
		result, err = self.run( "-pools" )
		return result.split( '\r\n' )[:-1]

	@property
	def groups(self):
		"""return the groups in deadline"""
		result, err = self.run( "-groups" )
		return result.split( '\r\n' )[:-1]

	@property
	def repositoryRoot(self):
		"""return the repository root"""
		result, err = self.run( "-getrepositoryroot" )
		return result.split( '\r\n' )[0]

	@property
	def userHomeDirectory(self):
		"""return the home directory of the user"""
		result, err = self.run( "-GetCurrentUserHomeDirectory" )
		return result.split( '\r\n' )[0]

