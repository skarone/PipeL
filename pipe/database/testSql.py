import sqlite3 as lite
import sys
from time import gmtime, strftime


class ProjectDataBase(object):
	"""class to handle the database of the proyect"""
	def __init__(self, project):
		self.project = project

	@property
	def dataBaseFile(self):
		"""data base dataBaseFile"""
		return 'D:/' + self.project + '.db'
		#return sti.Settings().General[ "basepath" ] + self.project + '.db'

	def create(self):
		"""create bases for database"""
		con = lite.connect( self.dataBaseFile )
		with con:
			cur = con.cursor()    
			cur.execute("CREATE TABLE Assets( Id INTEGER PRIMARY KEY, Name TEXT, Type TEXT, Area TEXT,Sequence TEXT, UserId INTEGER, Priority INTEGER, Status INTEGER, TimeStart TEXT, TimeEnd TEXT );")
			cur.execute("CREATE TABLE Users( Id INTEGER PRIMARY KEY, Name TEXT UNIQUE, Permisions INTEGER );")
			cur.execute("CREATE TABLE Notes( Id INTEGER PRIMARY KEY, Note TEXT, UserId INTEGER, AssetId INTEGER, Date TEXT );")

	def addAsset(self, name, typ, area, seq, user, priority, status, timeStart, timeEnd ):
		"""add asset to database"""
		if user:
			userId = self.getUserIdFromName( user )
		else:
			userId = 0
		con = lite.connect(self.dataBaseFile)
		with con:
			cur = con.cursor()
			cur.execute("INSERT INTO Assets( Name, Type, Area, Sequence, UserId, Priority, Status, TimeStart, TimeEnd ) VALUES(?,?,?,?,?,?,?,?,?)",(name,typ,area,seq,userId,priority,status,timeStart,timeEnd))

	def remAsset(self, assetName):
		"""remove asset from database"""
		con = lite.connect(self.dataBaseFile)
		with con:
			cur = con.cursor()
			#
			cur.execute("DELETE FROM Assets WHERE Name=%s"%assetName )

	def getAssets(self):
		"""return all the assets information"""
		con = lite.connect(self.dataBaseFile)
		with con:
			cur = con.cursor()
			cur.execute("SELECT * FROM Assets")        
			con.commit()
			return cur.fetchall()

	def getAssetsForUser(self, userName ):
		"""return the assets assigned to the user"""
		userId = self.getUserIdFromName( userName )
		con = lite.connect(self.dataBaseFile)
		with con:
			cur = con.cursor()
			cur.execute("SELECT * FROM Assets WHERE UserId=:user", {"user": userId})        
			con.commit()
			return cur.fetchall()
			
	def setAssetTime(self, assetName, timeStart, timeEnd):
		"""docstring for setAssetTime"""
		con = lite.connect(self.dataBaseFile)
		with con:
			cur = con.cursor()
			cur.execute("UPDATE Assets SET TimeStart = %s, TimeEnd = %s WHERE Name = %s"%(timeStart,timeEnd,assetName)) 

	def setAssetUser(self, assetName, userName):
		"""docstring for setAssetUser"""
		con = lite.connect(self.dataBaseFile)
		with con:
			cur = con.cursor()
			cur.execute("UPDATE Assets SET User = %s WHERE Name = %s"%(userName, assetName)) 

	def setAssetStatus(self, assetName, status):
		"""docstring for setAssetStatys"""
		con = lite.connect(self.dataBaseFile)
		with con:
			cur = con.cursor()
			cur.execute("UPDATE Assets SET Status = %i WHERE Name = %s"%(status, assetName)) 

	def setAssetPriority(self, assetName, priority):
		"""docstring for setAssetPriority"""
		con = lite.connect(self.dataBaseFile)
		with con:
			cur = con.cursor()
			cur.execute("UPDATE Assets SET Priority = %i WHERE Name = %s"%(priority, assetName)) 

	def getAssetIdFromName(self, assetName, area):
		"""return user id from user name"""
		con = lite.connect(self.dataBaseFile)
		with con:
			cur = con.cursor()
			cur.execute("SELECT Id FROM Assets WHERE Name=:name AND Area=:area", {"name": assetName, "area": area})        
			con.commit()
			return cur.fetchone()[0]

	def getAsset(self, assetName, area):
		"""return asset information from assetName and Area"""
		con = lite.connect(self.dataBaseFile)
		with con:
			con.row_factory = lite.Row
			cur = con.cursor()
			cur.execute("SELECT Assets.Name AS assetName, Users.Name AS userName, Assets.Area, Assets.Priority, Assets.Status, Assets.TimeStart, Assets.TimeEnd FROM Assets INNER JOIN Users ON Assets.UserId = Users.Id WHERE Assets.Name=:name AND Assets.Area=:area", {"name": assetName, "area": area})        
			con.commit()
			return cur.fetchone()

	def addUser(self, userName, permisions = 0):
		"""add user to database"""
		con = lite.connect(self.dataBaseFile)
		with con:
			cur = con.cursor()
			cur.execute("INSERT INTO Users(Name, Permisions) VALUES(?,?)",(userName,permisions))

	def remUser(self, userName):
		"""remove user from database"""
		con = lite.connect(self.dataBaseFile)
		with con:
			cur = con.cursor()
			cur.execute("DELETE FROM Users WHERE Name=%s"%userName )

	def getUsers(self):
		"""docstring for getUsers"""
		con = lite.connect(self.dataBaseFile)
		with con:
			cur = con.cursor()
			cur.execute("SELECT Name FROM Users")        
			con.commit()
			return cur.fetchall()

	def getUserIdFromName(self, userName):
		"""return user id from user name"""
		con = lite.connect(self.dataBaseFile)
		with con:
			cur = con.cursor()
			cur.execute("SELECT Id FROM Users WHERE Name=:name", {"name": userName})        
			con.commit()
			return cur.fetchone()[0]

	def addNote(self, note, user, asset, area):
		"""add note to database"""
		userId = self.getUserIdFromName( user )
		assetId = self.getAssetIdFromName( asset, area )
		date = strftime("%Y-%m-%d %H:%M:%S", gmtime())
		con = lite.connect(self.dataBaseFile)
		with con:
			cur = con.cursor()
			cur.execute("INSERT INTO Notes(Note, UserId, AssetId, Date) VALUES(?,?,?,?)",(note,userId,assetId,date))

	def removeNote(self, asset, area, date ):
		"""remove note from database"""
		pass

	def getNotesForAsset(self, assetName, area ):
		"""return all the notes for asset"""
		con = lite.connect(self.dataBaseFile)
		assetId = self.getAssetIdFromName( assetName, area )
		with con:
			con.row_factory = lite.Row
			cur = con.cursor()
			cur.execute("SELECT Note, Users.Name as userName, Assets.Name as assetName, Date FROM Notes INNER JOIN Users ON Notes.UserId = Users.Id INNER JOIN Assets ON Notes.AssetId = Assets.Id WHERE Notes.UserId=:name", {"name": assetId})        
			con.commit()
			return cur.fetchall()


	"""
	con = lite.connect( 'D:/' + 'testProject3' + '.db' )
	with con:
		con.row_factory = lite.Row 
		cur = con.cursor()
		cur.execute("SELECT Assets.Name AS assetName, Users.Name AS userName, Assets.Priority, Assets.Status, Assets.TimeStart, Assets.TimeEnd, Notes.Note, Notes.Date FROM Assets INNER JOIN Users ON Assets.UserId = Users.Id INNER JOIN Notes ON Assets.Id = Notes.AssetId;")
		con.commit()
		asd = cur.fetchall()
	for row in asd:
		print row[ "assetName"]
	"""
		
