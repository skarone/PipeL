import sqlite3 as lite
import sys
from time import gmtime, strftime
import pipe.task.task as task
reload( task )
import pipe.note.note as note
reload( note )

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
			cur.execute("CREATE TABLE Assets( Id INTEGER PRIMARY KEY, Name TEXT, Area TEXT,Sequence TEXT, UserId INTEGER, Priority INTEGER, Status INTEGER, TimeStart TEXT, TimeEnd TEXT );")
			cur.execute("CREATE TABLE Users( Id INTEGER PRIMARY KEY, Name TEXT UNIQUE, Permisions INTEGER );")
			cur.execute("CREATE TABLE Notes( Id INTEGER PRIMARY KEY, Note TEXT, UserId INTEGER, AssetId INTEGER, Date TEXT );")

	def addAsset(self, name, area, seq, user, priority, status, timeStart, timeEnd ):
		"""add asset to database"""
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
		assetId = self.getAssetIdFromName(assetName, area, seq )
		userId  = self.getUserIdFromName( userName )
		con = lite.connect(self.dataBaseFile)
		with con:
			cur = con.cursor()
			cur.execute("UPDATE Assets SET UserId = %i, Prority = %i, Status = %i, TimeStart = %s, TimeEnd = %s  WHERE Id = %i"%(userId, priority, status, timeStart, timeEnd, assetId)) 
	
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
			con.row_factory = lite.Row
			cur = con.cursor()
			#(1, u'Brocoli', u'Shading', u'', 1, 50, 0, u'Now', u'Tomorrow')
			cur.execute("SELECT Assets.Id as id, Assets.Name as name, Assets.Area as area, Assets.Sequence as seq, Users.Name as userName, Assets.Priority as priority, Assets.Status as status, Assets.TimeStart as timeStart, Assets.TimeEnd as timeEnd FROM Assets INNER JOIN Users ON Assets.UserId = Users.Id WHERE UserId=:user", {"user": userId})        
			con.commit()
			tasks = []
			for t in cur.fetchall():
				notes = self.getNotesForAsset( t['name'], t['area'], t['seq'] )
				print notes
				tasks.append( task.Task( t, notes ) )
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

	def addNote(self, note, user, asset, area, seq = '' ):
		"""add note to database"""
		userId = self.getUserIdFromName( user )
		assetId = self.getAssetIdFromName( asset, area, seq )
		date = strftime("%Y-%m-%d %H:%M:%S", gmtime())
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
			cur.execute("SELECT Note as note, Users.Name as userName, Assets.Name as assetName, Date as date FROM Notes INNER JOIN Users ON Notes.UserId = Users.Id INNER JOIN Assets ON Notes.AssetId = Assets.Id WHERE Notes.AssetId=:name", {"name": assetId})        
			con.commit()
			notes = cur.fetchall()
			print notes
			return [note.Note( n ) for n in notes]

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
		
