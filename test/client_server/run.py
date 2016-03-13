'''
Utility for testing different servers vs different clients

servers should be modules of the form *_server.py
they accept one positional command line argument of the port to serve on
they will be measured at serving the URL "/"

clients should be functions fo the form *_client().
they accept one positional argument of the port to communicate to
they should return a data structure summarizing the latency
(e.g. dict of mean, median, 95%)
'''
import subprocess
import atexit
import sys
import time
import glob
import os.path
import os
import re
import socket


def discover_and_run():
	servers = glob.glob('*_server.py')
	clients = []
	namespace = globals()
	for name in namespace:
		if re.match('.*_client$', name):
			clients.append(namespace[name])
	run(clients, servers)


def run(clients, servers, startup=10):
	port = 10000
	server_procs = []
	for server in servers:
		print "starting", server
		proc = subprocess.Popen([sys.executable, server, str(port)], stdout=subprocess.PIPE)
		_PROCS.append(proc)
		server_procs.append(proc)
		proc.port = port
		proc.server_name = server
		start = time.time()
		while time.time() - start < startup:
			try:
				socket.create_connection( ('localhost', port))
				break
			except socket.error:
				pass
		else:  # didn't break
			raise EnvironmentError(
				"server {0} on port {1} didn't come ready within {2}s".format(
					server, port, startup))
		port += 1

	for serv in server_procs:
		print "SERVER", serv.server_name
		for client in clients:
			print "    CLIENT", client.__name__, client(serv.port)

		serv.kill()


def urllib_client(port):
	import urllib2
	url = 'http://localhost:{0}/'.format(port)
	def inner():
		return float(urllib2.urlopen(url).read())
	return _client_helper(inner)


def requests_client(port):
	import requests
	url = 'http://localhost:{0}/'.format(port)
	def inner():
		return float(requests.get(url).text)
	return _client_helper(inner)


def tcp_client(port):
	def inner():
		s = socket.create_connection( ('localhost', port))
		s.send('GET / HTTP/1.1\r\n\r\n')
		return float(s.recv(1024).rpartition('\r\n')[2].strip())
	return _client_helper(inner)


def _client_helper(inner):
	durations = []
	for i in range(1000):
		s = time.time()
		t2 = inner()
		durations.append(time.time() - s)
		print t2 - s, time.time() - t2
	durations.sort()
	return {
		'mean': sum(durations) / len(durations),
		'median': durations[500],
		'95%': durations[950],
		'max': durations[-1]
	}


def _cleanup():
	for proc in _PROCS:
		try:
			proc.kill()
		except OSError:
			pass


_PROCS = []
atexit.register(_cleanup)


def _disable_logging():
	import logging
	logging.basicConfig(level=logging.CRITICAL)


_disable_logging()


if __name__ == "__main__":
	os.chdir(os.path.dirname(os.path.abspath(__file__)))
	discover_and_run()

