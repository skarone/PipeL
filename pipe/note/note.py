'''
File: note.py
Author: Ignacio Urruty
Description: 
	Manage notes easylly, note class handle... user, date, asset (per area), shot (per area), and note text.
'''

class Note(object):
	"""base class to handle notes"""
	def __init__(self, noteData ):
		#note, userName, assetName, date
		self.noteData = noteData

	@property
	def note(self):
		"""return the noteString"""
		return self.noteData[ 'note' ]
		
	@property
	def user(self):
		"""return the user for the note"""
		return self.noteData[ 'userName' ]

	@property
	def date(self):
		"""return the date of the note"""
		return self.noteData[ 'date' ]

	@property
	def asset(self):
		"""return the asset of the note"""
		return self.noteData[ 'assetName' ]

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

