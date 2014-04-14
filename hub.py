#coding: utf8
import ioloop
import socket
import logging
from handlers import *

CONFIG = {
    "listen": '0.0.0.0',
    "port": 9898
}

def main():
    io = ioloop.IOLoop()
    sock = socket.socket()
    sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    sock.setblocking(0)
    sock.bind((CONFIG["listen"], CONFIG["port"]))
    logging.info("listing on %s", str(sock.getsockname()))
    sock.listen(1024)
    io.add_handler(sock.fileno(), HubAcceptHandler(io, sock), m_read=True)
    while True:
        io.wait_events(0.1) 

if __name__ == '__main__':
    logging.basicConfig(level=logging.DEBUG,
                format='%(asctime)s %(levelname)-8s # %(message)s',
                datefmt='%Y-%m-%d %H:%M:%S', filemode='a+')
    main()
