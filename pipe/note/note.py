'''
File: note.py
Author: Ignacio Urruty
Description: 
	Manage notes easylly, note class handle... user, date, asset (per area), shot (per area), and note text.
'''

class Note(object):
	"""base class to handle notes"""
	def __init__(self, asset, area ):
		self._asset      = asset
		self._area       = area

	def add(self, user, noteString ):
		"""docstring for create"""
		pass

	@property
	def noteString(self):
		"""return the noteString"""
		pass
		
	@property
	def user(self):
		"""return the user for the note"""
		pass

	@property
	def date(self):
		"""return the date of the note"""
		pass

	@property
	def area(self):
		"""return the area of the asset"""
		pass

	@property
	def asset(self):
		"""return the asset of the note"""
		pass

class Notes(object):
	"""base class to handle group of notes"""
	def __init__(self, asset, area):
		self._asset = asset 
		self._area  = area

	def notes(self):
		"""return all the notes for the asset in the area"""
		pass
		

	@property
	def last(self):
		"""return the last note of the note for the asset"""
		pass

