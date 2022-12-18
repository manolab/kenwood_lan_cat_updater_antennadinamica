# boh

import atexit
import socket
import time
from errors import AuthException


def do_auth(my_socket, user, password) -> None:
    """Authentication"""

    auth = f"##ID00508{user}{password};"
    my_socket.sendall(auth.encode('utf-8'))
    socket_data = my_socket.recv(1024)
    if socket_data.decode('utf-8') != '##ID1;':
        raise AuthException(socket_data.decode('utf-8'))

    print("Authenticated")
    my_socket.sendall(b"AI0;")
    # data = s.recv(1024)
    # print(f"Received {data!r}")


def do_connection(my_socket, host, port) -> None:
    """Socket connection"""

    my_socket.connect((host, int(port)))
    my_socket.sendall(b"##CN;")
    socket_data = my_socket.recv(1024)
    if socket_data.decode('utf-8') != '##CN1;':
        raise ConnectionError


def do_other_stuff(my_socket) -> str:
    """Do other stuff"""

    my_socket.sendall(b"FA;")
    socket_data = my_socket.recv(1024)
    decoded = socket_data.decode('utf-8')[2:].lstrip("0")[0:-3] + '00'
    print(decoded)
    return decoded


def write_results(path, results) -> None:
    """Write results"""

    file = open(path, "w+", encoding="utf-8")
    file.write(results)


def start(host, port, output, user, password):
    """Main logic"""

    resulting_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    do_connection(resulting_socket, host, port)
    do_auth(resulting_socket, user, password)
    while True:
        results = do_other_stuff(resulting_socket)
        write_results(output, results)
        time.sleep(1)


def exit_handler():
    print('\nThe application is terminating... writing to file...\n')
    file = open('test_on_exit_file', 'w+')
    file.write('Bye!')


atexit.register(exit_handler)
