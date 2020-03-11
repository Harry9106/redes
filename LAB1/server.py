#!/usr/bin/env python
# encoding: utf-8
# Revisión 2014 Carlos Bederián
# Revisión 2011 Nicolás Wolovick
# Copyright 2008-2010 Natalia Bidart y Daniel Moisset
# $Id: server.py 656 2013-03-18 23:49:11Z bc $

import optparse
import socket
import sys
import connection
from constants import *


class Server(object):
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
        self.srsocket.bind((addr, port))
        self.srsocket.listen(1)
        print 'listening...'

    def serve(self):
        """
        Loop principal del servidor. Se acepta una conexión a la vez
        y se espera a que concluya antes de seguir.
        """
        try:
		    while True:
		        (csocket, address) = self.srsocket.accept()
		        print 'client connected ... ', address
		        conn = connection.Connection(csocket, self.directory)
		        conn.handle()
		        
        except Exception:
		    self.srsocket.send(str(INTERNAL_ERROR) + ' ' + error_messages[INTERNAL_ERROR] + EOL)

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

    server = Server(options.address, port, options.datadir)
    server.serve()

if __name__ == '__main__':
    main()
