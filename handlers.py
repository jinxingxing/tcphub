#coding: utf8

import ioloop
import socket
import logging
from stream import *

class HubDataHandler(ioloop.IOHandler):
    def __init__(self, accept_fd, _ioloop, _iostream):
        ioloop.IOHandler.__init__(self, _ioloop, _iostream)
        self._accept_fd = accept_fd

    def peer_fds(self):
        return [fd for fd in self._ioloop._fd_map if fd != self._fd and fd != self._accept_fd]

    def close_hs(self, type='local'):
        self._ioloop.remove_handler(self._fd)
        self._ios.close()
        if type == 'local' and len(self.peer_fds()) <= 1:
            for fd in self.peer_fds():
                self._ioloop._fd_map[fd].close_hs(type='peer')

    def send_to_peer(self, data, fds=None):
        if fds is None:
            fds = self.peer_fds()
        
        for fd in fds: 
            self._ioloop._fd_map[fd]._ios.write(data)

    def handle_read(self):
        try:
            s = self._ios.read(10240)
            if len(s) == 0:
                logging.debug('iostream[%s].read() return len(s) == 0, close it', self._fd)
                self.close_hs()
            self.send_to_peer(s)
            return s
        except socket.error, _e:
            if _e.errno in (errno.EWOULDBLOCK, errno.EAGAIN):
                logging.debug('socket error, %s', _e)
                return
            else:
                raise

class HubAcceptHandler(ioloop.BaseHandler):
    def __init__(self, ioloop, srv_socket):
        self._ioloop = ioloop
        self._srv_socket = srv_socket 

    def handle_read(self):
        cli_socket, cli_addr = self._srv_socket.accept()
        logging.debug("accept connect[%s] from %s:%s" % (
            cli_socket.fileno(), cli_addr[0], cli_addr[1]))
        cli_socket.setblocking(0)
        hs = HubStream(cli_socket)
        accept_fd = self._srv_socket.fileno()
        handler = HubDataHandler( accept_fd, self._ioloop, hs)
        self._ioloop.add_handler(cli_socket.fileno(), handler, m_read=True, m_write=True)
