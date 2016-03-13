import socket
import sys
import time

port = int(sys.argv[1])

conn = socket.socket()
conn.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
conn.bind( ('localhost', port))
conn.listen(500)

while 1:
	client = conn.accept()[0]
	client.recv(32 * 1024)
	client.send('HTTP/1.0 OK\r\n\r\n' + str(time.time()))
