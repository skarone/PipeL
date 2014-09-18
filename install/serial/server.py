import socket
import sys

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
	print 'Received ', repr( data )

	#send it back nicely formatted
	data = data.rstrip()
	connection.send( "%s\n%s\n%s\n" % ( '-'*80, data.center( 80 ), '-'*80))
	print 'Response sent!'
	
	# close the connection from our side
	connection.shutdown( socket.SHUT_RD | socket.SHUT_WR )
	connection.close()
	print "Connection closed."
# And stop listening
server.close()
