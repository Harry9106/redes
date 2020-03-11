#!/usr/bin/env python
# encoding: utf-8
# Revisión 2014 Carlos Bederián
# Revisión 2011 Nicolás Wolovick
# Copyright 2008-2010 Natalia Bidart y Daniel Moisset
# $Id: asyncserver.py 656 2013-03-18 23:49:11Z bc $

import optparse
import select
import socket
import sys
import Queue
import connection
from constants import *


class AsyncServer(object):
    """
    El servidor, que crea y atiende el socket en la dirección y puerto
    especificados donde se reciben nuevas conexiones de clientes.
    """

    def __init__(self, addr=DEFAULT_ADDR, port=DEFAULT_PORT,
                 directory=DEFAULT_DIR):
        print "Serving %s on %s:%s." % (directory, addr, port)
        self.directory = directory
        self.srsocket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.srsocket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        self.srsocket.setblocking(0)
        self.srsocket.bind((addr, port))
        self.srsocket.listen(5)
        self.messages_queues = {}
        print 'listening...'

        print(select.POLLIN)
        print(select.POLLOUT)
        print(select.POLLIN | select.POLLOUT)

    def serve(self):
        """
        Loop principal del servidor. Se acepta una conexión a la vez
        y se espera a que concluya antes de seguir.
        """
        # Set up the poller
        p = select.poll()
        p.register(self.srsocket, select.POLLIN)
        clients = {}
        while True:
            events = p.poll()
            print events
            for fileno, event in events:
                if fileno == self.srsocket.fileno():
                    if event & select.POLLIN:
                        c_socket, c_adress = self.srsocket.accept()
                        c_socket.setblocking(0)
                        p.register(c_socket, select.POLLIN)
                        c_fileno = c_socket.fileno()
                        clients[c_fileno] = connection.Connection(
                            c_socket, self.directory
                        )
                        print('New client: ' + str(c_adress))
                else:
                    if event & select.POLLIN:
                        conn = clients[fileno]
                        conn.handle_input()
                        if conn.remove:
                            p.unregister(fileno)
                            del clients[fileno]
                            conn.socket.close()
                        else:
                            p.modify(fileno, select.POLLIN | select.POLLOUT)
                            print (fileno, select.POLLIN | select.POLLOUT)


                    elif event & select.POLLOUT:
                        conn = clients[fileno]
                        conn.handle_output()
                        if conn.remove:
                            p.unregister(fileno)
                            del clients[fileno]
                            conn.socket.close()
                        else:
                            p.modify(fileno, select.POLLIN)
                            print p

def main():
    """Parsea los argumentos y lanza el server"""

    parser = optparse.OptionParser()
    parser.add_option(
        "-p", "--port",
        help=u"Número de puerto TCP donde escuchar", default=DEFAULT_PORT)
    parser.add_option(
        "-a", "--address",
        help=u"Dirección donde escuchar", default=DEFAULT_ADDR)
    parser.add_option(
        "-d", "--datadir",
        help=u"Directorio compartido", default=DEFAULT_DIR)

    options, args = parser.parse_args()
    if len(args) > 0:
        parser.print_help()
        sys.exit(1)
    try:
        port = int(options.port)
    except ValueError:
        sys.stderr.write(
            "Numero de puerto invalido: %s\n" % repr(options.port))
        parser.print_help()
        sys.exit(1)

    asyncserver = AsyncServer(options.address, port, options.datadir)
    asyncserver.serve()

if __name__ == '__main__':
    main()
