import ConfigParser
import pipe.file.file as fl
import os

PYFILEDIR = os.path.dirname( os.path.abspath( __file__ ) )
skinsDir = PYFILEDIR.replace( 'pipe\\settings','general\\ui\\skins' )
SKINS = sorted([ a.split('.')[0] for a in os.listdir( skinsDir ) if a.endswith( '.stylesheet')])
SKINS.insert( 0, 'None' )
from sys import platform as _platform
if _platform == 'win32':
	settingsFile =  str( os.getenv('USERPROFILE') ) + '/pipel_settings.ini'
else:
	settingsFile =  str( os.path.expanduser( '~' ) ) + '/pipel_settings.ini'

class Settings(fl.File):
	"""class to handle settings in pipe"""
	def __init__(self, path = settingsFile):
		super(Settings, self).__init__( path )
		self.config = ConfigParser.ConfigParser()

	def read(self):
		"""read config file"""
		self.config.read( self.path )

	@property
	def hasGeneral(self):
		"""has general Settings"""
		if not self.exists:
			return False
		self.read()
		return self.hasSection( "General" )

	@property
	def hasStatusFilter(self):
		"""docstring for hasStatusFilter"""
		if not self.exists:
			return False
		self.read()
		return self.hasSection( "StatusFilter" )

	@property
	def hasUserFilter(self):
		"""docstring for hasStatusFilter"""
		if not self.exists:
			return False
		self.read()
		return self.hasSection( "UserFilter" )

	@property
	def hasHistory(self):
		"""has history settings"""
		if not self.exists:
			return False
		self.read()
		return self.hasSection( "History" )

	@property
	def History(self):
		"""return history"""
		self.read()
		if self.exists:
			if self.hasSection( "History" ):
				return self.ConfigSectionMap( "History" )
		return {}

	@property
	def UserFilter(self):
		"""docstring for UserFilter"""
		self.read()
		if self.exists:
			if self.hasSection( "UserFilter" ):
				return self.ConfigSectionMap( "UserFilter" )
		return {}

	@property
	def StatusFilter(self):
		"""docstring for UserFilter"""
		self.read()
		if self.exists:
			if self.hasSection( "StatusFilter" ):
				return self.ConfigSectionMap( "StatusFilter" )
		return {}

	@property
	def General(self):
		"""return general"""
		self.read()
		if self.exists:
			if self.hasSection( "General" ):
				return self.ConfigSectionMap( "General" )
		return {}

	def hasSection(self, section):
		"""return if has section in config file"""
		return self.config.has_section( section )

	def ConfigSectionMap(self, section):
		"""return dictionary with options of the section"""
		dict1 = {}
		options = self.config.options(section)
		for option in options:
			try:
				dict1[option] = self.config.get(section, option)
				if dict1[option] == -1:
					DebugPrint("skip: %s" % option)
			except:
				print("exception on %s!" % option)
				dict1[option] = None
		return dict1

	def write(self, section, option, value):
		"""write option to section"""
		self.read()
		if not self.config.has_section( section ):
			self.config.add_section( section )
		self.config.set( section, option, value )
		with open( self.path, 'w' ) as cfgfile:
			self.config.write( cfgfile )
