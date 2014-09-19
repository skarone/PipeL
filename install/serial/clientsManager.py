import sqlite3 as lite
import sys

class ClientsManager(object):
	"""handle sql database of the clients"""
	def __init__(self, path):
		self._path = path

	def create(self):
		"""create clients table"""
		con = lite.connect( self._path )
		with con:
			cur = con.cursor()
			cur.execute( '''CREATE TABLE IF NOT EXISTS Clients( ID INTEGER PRIMARY KEY AUTOINCREMENT, 
																CLIENT_NAME TEXT NOT NULL, 
																SERIAL_NO TEXT UNIQUE NOT NULL, 
																LICENSE_NO INT NOT NULL DEFAULT 1, 
																VALIDATIONS_NO INT NOT NULL DEFAULT 0 );''' )

	def addClient(self, name, serial, License_number ):
		"""docstring for addClient"""
		con = lite.connect( self._path )
		with con:
			cur = con.cursor()
			cur.execute("INSERT INTO Clients(CLIENT_NAME, SERIAL_NO, LICENSE_NO ) VALUES ('" + name + "','" + serial + "'," + str(License_number) + ");")

	def clientInstall(self, serial):
		"""when client made an install, add 1 to validations_no"""
		clientData = self.getClientData( serial )
		if clientData:
			if clientData[3] == clientData[4]:
				#we reach the limit of installation
				return 'installations-reached'
			#add one to the validations limit and return True!
			con = lite.connect( self._path )
			with con:
				cur = con.cursor()
				cur.execute( "UPDATE Clients SET VALIDATIONS_NO=" +str( clientData[4] + 1 ) + " WHERE Id=" + str( clientData[0] ) + ";" )
				print clientData
			return True
		return 'wrong-serial'

	def getClientData(self, serial):
		"""return Bool if serial is exists"""
		con = lite.connect( self._path )
		with con:
			cur = con.cursor()
		cur.execute("select * from Clients where serial_no=:serial", {"serial": serial})
		return cur.fetchone()
		 
