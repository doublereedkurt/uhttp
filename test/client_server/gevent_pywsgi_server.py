import sys
from gevent import pywsgi
import time


port = int(sys.argv[1])


def hello_world_app(environ, start_response):
	start_response('200 OK', [('Content-type', 'text/plain')])
	return [str(time.time())]


server = pywsgi.WSGIServer(('127.0.0.1', port), hello_world_app, log=None)
server.serve_forever()
