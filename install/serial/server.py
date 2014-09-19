import socket
import sys
import coder

# Create a TCP/IP socket to listen on
server = socket.socket( socket.AF_INET, socket.SOCK_STREAM )

# Prevent from "address already in use" upon server restart
server.setsockopt( socket.SOL_SOCKET, socket.SO_REUSEADDR, 1 )

# Bind the socket to port 8081 on all interfaces
server_address = ( 'localhost', 8081 )
print 'starting up on %s port %s' % server_address
server.bind( server_address )

# Listen for connections
server.listen( 5 )


while 1:
	# Wait for one incomming connection
	connection, client_address = server.accept()
	print 'connection from', connection.getpeername()
	# Let's receive something
	data = connection.recv( 4096 )
	if not data: break

	#send it back nicely formatted
	data      = coder.decode('monigota', data )
	dataSplit = data.split( '/' )
	mac       = dataSplit[0]
	usr       = dataSplit[1]
	serial    = dataSplit[2]
	print 'Received ', mac,usr,serial
	#TODO
	#HERE WE HAVE TO CHECK WITH SQL IF SERIAL IS OK AND THERE ARE INSTALLATIONS AVAIABLES FOR THIS SERIAL
	finalData = serial + '+' + mac + '+' + usr + 'monigota'
	finalData = coder.encode( 'gotamoni', finalData )
	connection.send( finalData )
	print 'Response sent!'

	
	# close the connection from our side
	connection.shutdown( socket.SHUT_RD | socket.SHUT_WR )
	connection.close()
	print "Connection closed."
# And stop listening
server.close()
