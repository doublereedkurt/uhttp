import ssl
import socket

import http_parser
import buffered_socket
from dictutils import OrderedMultiDict


class WSGIServer(object):
	def __init__(self, app, recv_chunk=32 * 1024, timeout=None):
		self.recv_chunk = recv_chunk
		self.app = app

	def handle(self, sock, addr):
		handler = _WSGIHandler(sock, addr, self)
		handler.do_requests()


class _WSGIHandler(object):
	def __init__(self, sock, addr, server):
		self.sock = buffered_socket.BufferedSocket(sock)
		self.parser = http_parser.HttpParser()
		self.server = server

	def do_requests(self):
		connection_close = False
		while not connection_close:
			sent_headers = False
			self.response_started = False
			while not parser.is_headers_complete():
				data = self.sock.peek(self.server.recv_chunk)
				# get from 1 to recv_chunk bytes, or whatever is available
				self.sock.recv(parser.execute(data, len(data)))
				# remove whatever bytes are used by the parser from the buffer
			environ = parser.get_wsgi_environ()
			if isinstance(self.sock.sock, ssl.SSLSocket):
				environ['wsgi.url_scheme'] = 'https'
			else:
				environ['wsgi.url_scheme'] = 'http'
			iter_response = self.server.app(environ, self.start_response)
			for chunk in iter_response:
				if not self.response_started:
					raise NoStartResponse('app did not call start_response()')
				if not chunk:
					continue
				if not sent_headers:
					headers = [
					]
					sent_headers = True
				self.sock.sendall(chunk)
		self.sock.shutdown(socket.SHUT_RDWR)
		self.sock.close()

	def start_response(self, status, response_headers, exc_info=None):
		self.response_started = True
		if exc_info:
			try:
				# extract useful parts of exc_info
				status = "500 Internal Server Error"
			finally:
				exc_info = None
		self.status = status
		self.response_headers = OrderedMultiDict(response_headers)
		return self.write

	def write(self, *a, **kw):
		raise NotImplemented("not bothering to support write() callable")


class HTTPError(Exception):
	pass


class WSGIAppError(HTTPError):
	pass


class NoStartResponse(WSGIAppError):
	pass

