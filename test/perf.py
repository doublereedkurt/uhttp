'''
Module for comparing the performance of various WSGI containers.
'''
import thread
import urllib2
import time


IP = '127.1.2.3'


def make_client_requests(n=100, thread=thread):
    times = []
    lock = thread.allocate_lock()
    lock.acquire()
    def run():
        for i in range(n):
            start = time.time()
            urllib2.urlopen('http://' + IP + ':8080').read()
            times.append(time.time() - start)
    thread.start_new_thread(run, ())
    lock.acquire()
    return times



def hello_wsgi(environ, start_response):
    start_response(200)
    return ["hello world!"]


def test_gevent():
    from gevent import pywsgi
    import gevent.threading
    import gevent

    server = pywsgi.WSGIServer((IP, 8080), hello_wsgi)
    server.start()
    t = make_client_requests(thread=gevent.thread)
    server.stop()
    print "avg latency {0.03f}ms".format(1000 * sum(t) / len(t))


def main():
    test_gevent()


if __name__ == "__main__":
    main()
