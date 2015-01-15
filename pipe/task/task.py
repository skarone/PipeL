class Task(object):
	"""manage task UI"""
	def __init__(self, taskData, notes):
		#(1, u'Brocoli', u'Shading', u'', 1, 50, 0, u'Now', u'Tomorrow')
		self.taskData = taskData
		print self.taskData
		self._notes = notes

	@property
	def id(self):
		"""return id of task"""
		return self.taskData['id']

	@property
	def startDate(self):
		"""return start date"""
		return self.taskData['startDate']

	@property
	def endDate(self):
		"""docstring for endDate"""
		return self.taskData['endDate']

	@property
	def name(self):
		"""return name of the task, if asset.. return asset + area, if shot returns sequence + shot"""
		return self.taskData['name']
		
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

	@property
	def notes(self):
		"""return notes for task"""
		return self._notes
