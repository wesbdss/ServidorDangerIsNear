import sys
sys.path.insert(1, './Servidores/')
from webService import WebHandle
from webSocketPlay import SocketPlay
import json
import tornado.httpserver
import tornado.websocket
import tornado.ioloop
import tornado.web
import socket
import os


"""
estrutura json:

[
    {
        "function":"login",
        "username":"$username",
        "pass":"$password"
    },
    {
        "function":"login",
        "username":"$username",
        "pass":"$password"
    }
]

"""


def main():
    application = tornado.web.Application([
        (r'/event', SocketPlay), (r'/', WebHandle)])

    if __name__ == "__main__":
        port = int(os.environ.get("PORT", 8080))
        http_server = tornado.httpserver.HTTPServer(application)
        http_server.listen(port)
        myIP = socket.gethostbyname(socket.gethostname())
        print('*** Websocket Server Started at %s ***' % myIP)
        tornado.ioloop.IOLoop.instance().start()


main()
