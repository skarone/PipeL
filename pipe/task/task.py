class Task(object):
	"""manage task UI"""
	def __init__(self, taskData ):
		#(1, u'Brocoli', u'Shading', u'', 1, 50, 0, u'Now', u'Tomorrow')
		self.taskData = taskData

	@property
	def id(self):
		"""return id of task"""
		return self.taskData['id']

	@property
	def timeStart(self):
		"""return start date"""
		return self.taskData['timeStart']

	@property
	def timeEnd(self):
		"""docstring for endDate"""
		return self.taskData['timeEnd']

	@property
	def fullname(self):
		"""return name of the task, if asset.. return asset + area, if shot returns sequence + shot"""
		if self.taskData['seq'] == '': #ASSET
			return self.taskData['name'] + ' ' + self.taskData['area']
		return self.taskData['seq'] + ' ' + self.taskData['name'] + ' ' + self.taskData['area'] #SHOT

	@property
	def name(self):
		"""docstring for name"""
		return self.taskData[ 'name' ]

	@property
	def seq(self):
		"""docstring for seq"""
		return self.taskData[ 'seq' ]

	@property
	def area(self):
		"""docstring for area"""
		return self.taskData[ 'area' ]
		
	@property
	def user(self):
		"""assigned user"""
		return self.taskData['user']

	@property
	def priority(self):
		"""priority for task"""
		return self.taskData['priority']

	@property
	def status(self):
		"""return status of task"""
		return self.taskData['status']

	def notes(self, dataBase):
		"""return notes for task"""
		return dataBase.getNotesForAsset( self.taskData['name'], self.taskData['area'], self.taskData['seq'] )

	def addNote(self, dataBase, note, user, asset, area, seq = ''):
		"""docstring for addNote"""
		dataBase.addNote( note, user, asset, area, seq )
