import sys
import wsgiref.simple_server
import time


port = int(sys.argv[1])


def hello_world_app(environ, start_response):
	start_response('200 OK', [('Content-type', 'text/plain')])
	return [str(time.time())]


server = wsgiref.simple_server.make_server('127.0.0.1', port, hello_world_app)
server.serve_forever()