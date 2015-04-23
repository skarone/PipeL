import sqlite3 as lite
import sys
from time import gmtime, strftime
import pipe.task.task as task
reload( task )
import pipe.note.note as note
reload( note )
import pipe.settings.settings as sti
reload( sti )
import os

class ProjectDataBase(object):
	"""class to handle the database of the proyect"""
	def __init__(self, project):
		self.project = project

	@property
	def dataBaseFile(self):
		"""data base dataBaseFile"""
		#return 'D:/' + self.project + '.db'
		return sti.Settings().General[ "serverpath" ] + self.project + '/' + self.project + '_pipel.db'

	@property
	def exists(self):
		"""docstring for exists"""
		return os.path.exists( self.dataBaseFile )

	def create(self):
		"""create bases for database"""
		if not os.path.exists( os.path.dirname( self.dataBaseFile ) ):
			return
		con = lite.connect( self.dataBaseFile )
		with con:
			cur = con.cursor()    
			cur.execute("CREATE TABLE Assets( Id INTEGER PRIMARY KEY, Name TEXT, Area TEXT,Sequence TEXT, UserId INTEGER, Priority INTEGER, Status INTEGER, TimeStart TEXT, TimeEnd TEXT );")
			cur.execute("CREATE TABLE Notes( Id INTEGER PRIMARY KEY, Note TEXT, UserId INTEGER, AssetId INTEGER, Date TEXT );")

	def addAsset(self, name, area, seq, user, priority, status, timeStart, timeEnd ):
		"""add asset to database"""
		if not self.exists:
			self.create()
		if user:
			userId = self.getUserIdFromName( user )
		else:
			userId = 0
		if self.getAssetIdFromName( name, area, seq ):
			self.updateAsset( name, area, seq, user, priority, status, timeStart, timeEnd )
		else:
			con = lite.connect(self.dataBaseFile)
			with con:
				cur = con.cursor()
				cur.execute("INSERT OR REPLACE INTO Assets( Name, Area, Sequence, UserId, Priority, Status, TimeStart, TimeEnd ) VALUES(?,?,?,?,?,?,?,?)",(name,area,seq,userId,priority,status,timeStart,timeEnd))

	def updateAsset(self, name, area, seq, user, priority, status, timeStart, timeEnd ):
		"""docstring for updateAsset"""
		assetId = self.getAssetIdFromName(name, area, seq )
		userId  = self.getUserIdFromName( user )
		if not userId:
			return
		con = lite.connect(self.dataBaseFile)
		with con:
			cur = con.cursor()
			cur.execute("UPDATE Assets SET UserId = ?, Priority = ?, Status = ?, TimeStart = ?, TimeEnd = ?  WHERE Id = ?",(userId, priority, status, timeStart, timeEnd, assetId)) 
			con.commit()
	
	def remAsset( self, name, area, seq ):
		"""remove asset from database"""
		assetId = self.getAssetIdFromName(name, area, seq )
		con = lite.connect(self.dataBaseFile)
		with con:
			cur = con.cursor()
			#
			cur.execute("DELETE FROM Assets WHERE Id=%i"%(assetId ))

	def getAssets(self):
		"""return all the assets information"""
		if not self.exists:
			return []
		con = lite.connect(self.dataBaseFile)
		with con:
			cur = con.cursor()
			cur.execute("SELECT * FROM Assets")        
			con.commit()
			return cur.fetchall()

	def getAssetsForUser(self, userName ):
		"""return the assets assigned to the user"""
		if not self.exists:
			return []
		userId = self.getUserIdFromName( userName )
		if not userId:
			return []
		con = lite.connect(self.dataBaseFile)
		with con:
			con.row_factory = lite.Row
			cur = con.cursor()
			#(1, u'Brocoli', u'Shading', u'', 1, 50, 0, u'Now', u'Tomorrow')
			cur.execute("ATTACH DATABASE '"+ BaseDataBase().dataBaseFile +"' AS dbOne" )
			cur.execute("SELECT Assets.Id as id, Assets.Name as name, Assets.Area as area, Assets.Sequence as seq, Users.Name as userName, Assets.Priority as priority, Assets.Status as status, Assets.TimeStart as timeStart, Assets.TimeEnd as timeEnd FROM Assets INNER JOIN Users ON Assets.UserId = Users.Id WHERE UserId=:user", {"user": userId})        
			con.commit()
			tasks = []
			for t in cur.fetchall():
				tasks.append( task.Task( t ) )
			return tasks
			
	def setAssetTime(self, assetName, area, timeStart, timeEnd, seq = ''):
		"""docstring for setAssetTime"""
		assetId = self.getAssetIdFromName(assetName, area, seq)
		con = lite.connect(self.dataBaseFile)
		with con:
			cur = con.cursor()
			cur.execute("UPDATE Assets SET TimeStart = %s, TimeEnd = %s WHERE Id = %i"%(timeStart,timeEnd,assetId)) 

	def setAssetUser(self, assetName, area, userName, seq = ''):
		"""assing user to asset"""
		assetId = self.getAssetIdFromName(assetName, area, seq )
		userId  = self.getUserIdFromName( userName )
		if userId:
			con = lite.connect(self.dataBaseFile)
			with con:
				cur = con.cursor()
				cur.execute("UPDATE Assets SET UserId = %i WHERE Id = %i"%(userId, assetId)) 

	def setAssetStatus(self, assetName, area, status, seq = '' ):
		"""set asset status"""
		assetId = self.getAssetIdFromName(assetName, area, seq )
		con = lite.connect(self.dataBaseFile)
		with con:
			cur = con.cursor()
			cur.execute("UPDATE Assets SET Status = %i WHERE Name = %i"%(status, assetId)) 

	def setAssetPriority(self, assetName, area, priority, seq = ''):
		"""set asset priority"""
		assetId = self.getAssetIdFromName(assetName, area, seq)
		con = lite.connect(self.dataBaseFile)
		with con:
			cur = con.cursor()
			cur.execute("UPDATE Assets SET Priority = %i WHERE Id = %i"%(priority, assetId)) 

	def getAssetIdFromName(self, assetName, area, seq = ''):
		"""return user id from user name"""
		if not self.exists:
			return
		con = lite.connect(self.dataBaseFile)
		with con:
			cur = con.cursor()
			cur.execute("SELECT Id FROM Assets WHERE Name=:name AND Area=:area AND Sequence=:seq", {"name": assetName, "area": area, "seq":seq})        
			con.commit()
			assetId = cur.fetchone()
			if assetId:
				return assetId[0]
			return None

	def getAsset(self, assetName, area):
		"""return asset information from assetName and Area"""
		if not self.exists:
			return 
		con = lite.connect(self.dataBaseFile)
		with con:
			con.row_factory = lite.Row
			cur = con.cursor()
			cur.execute("ATTACH DATABASE '"+ BaseDataBase().dataBaseFile +"' AS dbOne" )
			cur.execute("SELECT Assets.Name AS assetName, Users.Name AS userName, Assets.Area, Assets.Priority, Assets.Status, Assets.TimeStart, Assets.TimeEnd FROM Assets INNER JOIN Users ON Assets.UserId = Users.Id WHERE Assets.Name=:name AND Assets.Area=:area", {"name": assetName, "area": area})        
			con.commit()
			return cur.fetchone()

	def addUser(self, userName, Mail, Area = 0):
		"""add user to database"""
		baseData = BaseDataBase()
		if not baseData.exists:
			baseData.create()
		baseData.addUser( userName, Mail, Area )

	def remUser(self, userName):
		"""remove user from database"""
		baseData = BaseDataBase()
		if not baseData.exists:
			return
		baseData.remUser( userName )

	def getUsers(self):
		"""docstring for getUsers"""
		baseData = BaseDataBase()
		return baseData.getUsers()

	def getUserIdFromName(self, userName):
		"""return user id from user name"""
		baseData = BaseDataBase()
		if not baseData.exists:
			return
		return baseData.getUserIdFromName( userName )

	def addNote(self, note, user, asset, area, seq = '' ):
		"""add note to database"""
		userId = self.getUserIdFromName( user )
		if not userId:
			self.addUser( user )
			userId = self.getUserIdFromName( user )
		assetId = self.getAssetIdFromName( asset, area, seq )
		date = strftime("%d-%m-%Y %H:%M:%S", gmtime())
		con = lite.connect(self.dataBaseFile)
		with con:
			cur = con.cursor()
			cur.execute("INSERT INTO Notes(Note, UserId, AssetId, Date ) VALUES(?,?,?,?)",(note,userId,assetId,date))

	def removeNote(self, asset, area, date, seq = '' ):
		"""remove note from database"""
		assetId = self.getAssetIdFromName( asset, area, seq )
		con = lite.connect(self.dataBaseFile)
		with con:
			cur = con.cursor()
			cur.execute("DELETE FROM Notes WHERE AssetId=:name AND Date=:area", {"name": assetId, "area": date}) 

	def getNotesForAsset(self, assetName, area, seq = '' ):
		"""return all the notes for asset"""
		con = lite.connect(self.dataBaseFile)
		assetId = self.getAssetIdFromName( assetName, area, seq )
		with con:
			con.row_factory = lite.Row
			cur = con.cursor()
			cur.execute("ATTACH DATABASE '"+ BaseDataBase().dataBaseFile +"' AS dbOne" )
			cur.execute("SELECT Note as note, Users.Name as userName, Assets.Name as assetName, Date as date FROM Notes INNER JOIN Users ON Notes.UserId = Users.Id INNER JOIN Assets ON Notes.AssetId = Assets.Id WHERE Notes.AssetId=:name ORDER BY Notes.Id DESC" , {"name": assetId})        
			con.commit()
			notes = cur.fetchall()
			return [note.Note( n ) for n in notes]



class BaseDataBase(object):
	"""docstring for BaseDataBase"""
	def __init__(self):
		pass

	def create(self):
		"""create bases for database"""
		if not os.path.exists( os.path.dirname( self.dataBaseFile ) ):
			return
		con = lite.connect( self.dataBaseFile )
		with con:
			cur = con.cursor()    
			cur.execute("CREATE TABLE Users( Id INTEGER PRIMARY KEY, Name TEXT UNIQUE, Area INTEGER, Mail TEXT );")

	@property
	def exists(self):
		"""docstring for exists"""
		return os.path.exists( self.dataBaseFile )

	@property
	def dataBaseFile(self):
		"""data base dataBaseFile"""
		#return 'D:/' + self.project + '.db'
		return sti.Settings().General[ "serverpath" ] + 'pipel_database.db'

	def addUser(self, userName, Mail, Area = 0 ):
		"""add user to database"""
		if not self.exists:
			self.create()
		con = lite.connect(self.dataBaseFile)
		with con:
			cur = con.cursor()
			cur.execute("INSERT INTO Users(Name, Area, Mail) VALUES(?,?,?)",( userName, Area, Mail ))

	def remUser(self, userName):
		"""docstring for remUser"""
		con = lite.connect(self.dataBaseFile)
		with con:
			cur = con.cursor()
			cur.execute("DELETE FROM Users WHERE Name=%s"%userName )

	def getUserIdFromName(self, userName):
		"""return user id from user name"""
		con = lite.connect(self.dataBaseFile)
		with con:
			cur = con.cursor()
			cur.execute("SELECT Id FROM Users WHERE Name=:name", {"name": userName})        
			con.commit()
			userId = cur.fetchone()
			if userId:
				return userId[0]
			return 

	def getUsers(self):
		"""docstring for getUsers"""
		if not self.exists:
			return []
		con = lite.connect(self.dataBaseFile)
		with con:
			cur = con.cursor()
			cur.execute("SELECT Name FROM Users")        
			con.commit()
			res = cur.fetchall()
			final = []
			for r in res:
				final.append( r[0] )
			return final

	def getMailFromUser(self, userName):
		"""return mail from userName"""
		userId = sefl.getUserIdFromName( userName )
		con = lite.connect(self.dataBaseFile)
		with con:
			cur = con.cursor()
			cur.execute("SELECT Mail FROM Users WHERE Id=:name", {"name": userId})        
			con.commit()
			userId = cur.fetchone()
			if userId:
				return userId[0]

		

