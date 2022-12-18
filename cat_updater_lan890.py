"This program connects to a Kenwood receiver and gets current frequency"

import socket
import time
from exceptions import AuthenticationException

HOST = "192.168.1.16"
PORT = 60000
USER = "admin"
PASSWORD = "normando"

CAT_STATUS_PATH = "/usr/local/share/ad/cat_status.txt"
FREQUENCY_PATH = "/usr/local/share/ad/frequency.txt"


def authenticate(sock, user, password) -> None:
    "Authenticates to radio"

    auth_string = f"##ID00508{user}{password};"
    sock.sendall(auth_string.encode('utf-8'))
    data = sock.recv(1024)
    if data.decode('utf-8') != '##ID1;':
        raise AuthenticationException(data.decode('utf-8'))

    sock.sendall(b"AI0;")


def start_connection(sock, host, port) -> None:
    "Check connection to radio is available"

    sock.connect((host, port))
    sock.sendall(b"##CN;")
    data = sock.recv(1024)
    if data.decode('utf-8') != '##CN1;':
        raise ConnectionError


def get_frequency(sock) -> str:
    "Query radio for frequency"

    sock.sendall(b"FA;")
    data = sock.recv(1024)
    #print(f"Received {data!r}")
    frequency = data.decode('utf-8')[2:].lstrip("0")[0:-3]+'00'
    return frequency


def save_frequency(path, data) -> None:
    "Save frequency in a text file, overwriting it"

    with open(path, "w", encoding="utf-8") as outfile:
        outfile.write(data)


def main():
    "Main function"
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as sock:
        start_connection(socket, HOST, PORT)
        authenticate(sock, USER, PASSWORD)
        while True:
            frequency = get_frequency(sock)
            save_frequency(FREQUENCY_PATH, frequency)
            time.sleep(1)


if __name__ == '__main__':
    main()
