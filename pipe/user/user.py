'''
File: user.py
Author: Ignacio Urruty
Description: base class to handle users in the pipe
Handle permissions, notes, dates, assignments
'''
import socket

class User(object):
	"""class to handle users in the pipe"""
	def __init__(self, name):
		self._name = name

	@property
	def name(self):
		"""return the name of the node"""
		return self._name

	@property
	def permissions(self):
		"""docstring for permissons"""
		pass

	@property
	def machine(self):
		"""return the current machine that the user is loged in"""
		return socket.gethostname()

	@property
	def assets(self):
		"""assets assigned to the user"""
		pass

	def addAsset(self, asset, area):
		"""assign an asset to the user"""
		pass

	@property
	def shots(self):
		"""shots assigned to the user"""
		pass

	def addShot(self, shot, area):
		"""assign shot to user"""
		pass

