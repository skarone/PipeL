import socket
import uuid
import getpass
import coder

SERVER = 'localhost'
PORT   = 8081

def sendToServer( data ):
	"""docstring for sendToServer"""
	s = socket.socket( socket.AF_INET, socket.SOCK_STREAM )
	try:
		s.connect(( SERVER, PORT ))
		s.send( data )
		data = s.recv(1024)
		s.close()
	except:
		data = False
	return data

def sendClientInfo( serial ):
	"""get mac, user name, serial and send encrypted data to server, and recieve result to use"""
	mac     = str( uuid.getnode() )
	usr     = getpass.getuser()
	data    = mac+'/'+usr+'/'+serial
	data    = coder.encode( 'monigota', data )
	newData = sendToServer( data )
	return newData


	
