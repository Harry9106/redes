import socket
import select

HFTP_SERVER = 'localhost'
HFTP_PORT = 19500


def main():
    """
    Ejemplo muy basico del uso de poll().

    Recibe conexiones de multiples clientes a la vez
    y responde 'thanks for writing' por cada peticion recibida.
    """

    # Server socket
    socket_server = socket.socket()
    socket_server.setblocking(0)
    socket_server.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    socket_server.bind((HFTP_SERVER, HFTP_PORT))
    socket_server.listen(5)

    # Poll object
    p = select.poll()
    p.register(socket_server, select.POLLIN)

    clients = {}
    while True:
        events = p.poll()
        for fileno, event in events:
            if fileno == socket_server.fileno():
                if event & select.POLLIN:
                    client_socket, client_address = socket_server.accept()
                    client_socket.setblocking(0)
                    p.register(client_socket, select.POLLIN)
                    clients[client_socket.fileno()] = client_socket
                    print('New client: ' + str(client_address))
            else:
                if event & select.POLLIN:
                    data = clients[fileno].recv(4096)
                    print('Client %s says: %s' % (fileno, data))
                    p.modify(fileno, select.POLLIN | select.POLLOUT)

                if event & select.POLLOUT:
                    clients[fileno].send('Thanks for writing\r\n')
                    p.modify(fileno, select.POLLIN)


if __name__ == "__main__":
    main()
