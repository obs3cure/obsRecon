import BaseHTTPServer  # Built-in library we use to build simple HTTP server
import urlparse, json

trap = 1


class MyHandler(
    BaseHTTPServer.BaseHTTPRequestHandler):  # MyHandler defines what we should do when we receive a GET/POST request
    # from the client / target



    def do_GET(s):
        global trap
        trap = trap + 1
        trapak = trap // 5
        fopen = open('loghoney80.txt', 'a', 0)

        

        data='-----------------------------------------------------'

        fopen.write('%d,%s,%s,%s\n' %
                    (trapak, s.client_address[0], s.headers, data))
        s.send_response(200)  # return HTML status 200 (OK)
        s.send_header("Content-type", "text/html")  # Inform the target that content type header is  "text/html"
        s.end_headers()

        s.wfile.write("<html><head><title>Under Construction</title></head>")

        s.wfile.write("<body><p>Economic Paper of tygadruty</p>")
        # If someone went to "http://something.somewhere.net/foo/bar/",
        # then s.path equals "/foo/bar/".

        s.wfile.write("<p>We are on fase  %s</p>" % trapak)

        s.wfile.write("</body></html>")
        fopen.close()
