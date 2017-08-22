#!/usr/bin/env python

#import thread
import threading
import time
import socket
import BaseHTTPServer
from SimpleHTTPServer import SimpleHTTPRequestHandler
from httpTrap import MyHandler

HOST_NAME = '127.0.0.1' 
PORT_NUMBER = 80  


class honey(threading.Thread):
    """Honeypot"""
    def __init__(self, host='', port=6000, f=None):
        threading.Thread.__init__(self)
        self.host = host
        self.port = port
        self.f = f
        self.running = True

    def writelog(self, client, port, data=''):
        separator = '=' * 40
        self.f.write('%s,%d,%s,%d,%s\n' %
                            (time.ctime(), self.port, client[0], client[1], data))

    def run(self):
        if (self.port==80):
            run8(self)
        else:

            print '[*] Listening on port %d' % self.port
            s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            s.bind((self.host, self.port))
            s.listen(5)
            while self.running:
                (insock, address) = s.accept()
                print '[*] %s:%d -> %s:%d' % (address[0], address[1], self.host, self.port)
                try:
                    data = insock.recv(1024)
                    insock.close()
                except socket.error:
                    self.writelog(address, self.port)
                else:
                    self.writelog(address, self.port, data)

def run8(self):
    server_class = BaseHTTPServer.HTTPServer
    httpd = server_class((HOST_NAME, PORT_NUMBER), MyHandler)
    trap = 1
    try:
        httpd.serve_forever()  # start the HTTP server, however if we got ctrl+c we will Interrupt and stop the server
    except KeyboardInterrupt:
        print '[!] Server is terminated'
        httpd.server_close()


if __name__ == '__main__':
    host = ''
    ports = [22,23,25,443,80,8080,1025,3306,3389]
    threads = []
    fopen = open('loghoney.txt', 'a', 0)
    try:
        for port in ports:
            print '[+] Starting port %d thread...' % port
            threads.append(honey(host, port, fopen))
            threads[-1].daemon = True
            threads[-1].start()
    except BaseException, e:
        print '[-] Error: %s' % (e)
        exit(1)
    # Run forever, or until we kill it >.>
    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        print '[+] Exiting...'
        for thread in threads:
            thread.running = False
        time.sleep(3)
        fopen.close()
        exit(0)
