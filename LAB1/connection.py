# encoding: utf-8
# Copyright 2014 Carlos Bederián
# $Id: connection.py 455 2011-05-01 00:32:09Z carlos $

import socket
from constants import *
import os


class Connection(object):

    """
    Conexión punto a punto entre el servidor y un cliente.
    Se encarga de satisfacer los pedidos del cliente hasta
    que termina la conexión.
    """

    def __init__(self, socket, directory):
        """Inicialización de atributos de Connection."""
        self.s = socket
        self.dir = directory
        self.connected = True

    def listing(self, cmlist):
        """
        Envía secuencia de líneas terminadas en \r\n con
        el nombre de los archivos disponibles en el directorio compartido.
        """
        try:
            if (cmlist.count('  ') > 0):
                self.getmessage(BAD_REQUEST)
                self.s.close()
                self.connected = False
            else:
                cmlist = cmlist.split(' ')
                if len(cmlist) != 1:
                    self.getmessage(INVALID_ARGUMENTS)
                else:
                    self.getmessage(CODE_OK)
                    for item in os.listdir(self.dir):
                        self.s.send(item + " " + EOL)
                self.s.send(EOL)
        except OSError:
            self.getmessage(FILE_NOT_FOUND)

    def metadata(self, cmlist):
        """
        Envía el tamaño en bytes el archivo pedido, si éste se encuentra
        en el directorio.
        """
        try:
            if (cmlist.count('  ') > 0):
                self.getmessage(BAD_REQUEST)
                self.s.close()
                self.connected = False
            else:
                cmlist = cmlist.split(' ')
                if len(cmlist) != 2 or not self.checkfilename(cmlist[1]):
                    self.getmessage(INVALID_ARGUMENTS)
                else:
                    name = cmlist[1]
                    size = os.path.getsize(os.path.join(self.dir, name))
                    self.getmessage(CODE_OK)
                    self.s.send(str(size) + EOL)
        except OSError:
            self.getmessage(FILE_NOT_FOUND)

    def chunks(self, fpath, offset, size):
        f = open(fpath, 'r')
        f.seek(offset)
        stop = False
        if size < X4096X:
            yield f.read(size)
        else:
            while (not stop):
                chunk = f.read(X4096X)
                yield chunk
                stop = len(chunk) < X4096X or chunk == ""
        f.close()

    def slice(self, cmlist):
        """
        Envía una secuencia de dígitos indicando la longitud de la cadena
        de datos del fragmento en bytes, un espacio y la cadena de datos
        de longitud indicada, seguida de \r\n. Al finalizar envía nuevamente
        un terminador \r\n.
        """
        if (cmlist.count('  ') > 0):
                self.getmessage(BAD_REQUEST)
                self.s.close()
                self.connected = False
                return
        cmlist = cmlist.split(' ')
        if len(cmlist) != 4 or not self.checkfilename(cmlist[1]):
            self.getmessage(INVALID_ARGUMENTS)
            return

        name = cmlist[1]
        if (not os.path.exists(self.dir + "/" + name)):
            self.getmessage(FILE_NOT_FOUND)
            return

        try:
            offset = int(cmlist[2])
            size = int(cmlist[3])
            filesize = os.path.getsize(os.path.join(self.dir, name))
            if (offset < 0 or
                size <= 0 or
                offset + size > filesize):
                self.getmessage(BAD_OFFSET)
                return

            fpath = os.path.join(os.getcwd(), self.dir, name)

            self.getmessage(CODE_OK)
            for chunk in self.chunks(fpath, offset, size):
                self.s.send(str(len(chunk)) + ' ' + chunk + EOL)

            self.s.send('0' + ' ' + EOL)
        except ValueError:
            self.getmessage(INVALID_ARGUMENTS)
            return

    def quit(self, cmlist):
        """
        Cierra la conexion con el cliente.
        """
        try:
            if (cmlist.count('  ') > 0):
                self.getmessage(BAD_REQUEST)
                self.s.close()
                self.connected = False
            else:
                cmlist = cmlist.split(' ')
                if len(cmlist) != 1:
                    self.getmessage(INVALID_ARGUMENTS)
                else:
                    self.getmessage(CODE_OK)
                    self.s.close()
                    self.connected = False
        except Exception as e:
            print e

    def checkcommad(self, string):
        """
        Checkea si el comando valido.
        """
        stringlist = string.split(' ')
        command = stringlist[0]
        if (command == 'get_file_listing' or command == 'get_metadata'
           or command == 'get_slice' or command == 'quit'):
            return True
        else:
            return False

    def execute(self, string):
        """
        Ejecuta un comando.
        """
        stringlist = string.split(' ')
        command = stringlist[0]
        if command == 'get_file_listing':
            self.listing(string)
        elif command == 'get_metadata':
            self.metadata(string)
        elif command == 'get_slice':
            self.slice(string)
        elif command == 'quit':
            self.quit(string)

    def checkfilename(self, filename):
        """
        Checkea si el filename esta compuesto por caracteres validos.
        """
        for c in filename:
            if c not in VALID_CHARS:
                return False
        return True

    def getmessage(self, error):
        self.s.send(str(error) + ' ' + error_messages[error] + EOL)

    def handle(self):
        """
        Atiende eventos de la conexión hasta que termina.
        """
        messagebuffer = ''
        eolatlast = False
        while self.connected:
            message = self.s.recv(4096)
            
            if len(message) == 0:
                self.connected = False
                break

            if messagebuffer != '':
                message = messagebuffer + message
                messagebuffer = ''

            mlist = message.split(EOL)

            if (mlist[len(mlist) - 1]) == '':
                eolatlast = True

            for x in range(0, len(mlist)):
                if '\n' in mlist[x]:
                    self.getmessage(BAD_EOL)
                    self.s.close()
                    self.connected = False
                elif eolatlast is False and x == len(mlist) - 1:
                    messagebuffer = messagebuffer + (mlist[x])
                elif self.checkcommad(mlist[x]):
                    self.execute(mlist[x])
                else:
                    if (mlist[x]) != '':
                        self.getmessage(INVALID_COMMAND)

            eolatlast = False
