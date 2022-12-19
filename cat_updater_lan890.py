"This program connects to a Kenwood receiver and gets current frequency"

import os
import socket
import time
import configparser
from tenacity import retry
from tenacity.wait import wait_fixed

OUTPATHFR = '/usr/local/share/ad/frequency.txt'
OUTPATHST = '/usr/local/share/ad/cat_status.txt'

class AuthenticationException(Exception):
    "Raised when authentication fails"

    def __init__(self, errorcode="unknown") -> None:
        self.message = f"Authentication failed with code {errorcode}"
        super().__init__(errorcode)

def authenticate(sock, user, password) -> None:
    "Authenticates to radio"

    auth_string = f"##ID0{str(len(user)).zfill(2)}{str(len(password)).zfill(2)}{user}{password};"
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
    #frequency = data.decode('utf-8')[2:].lstrip("0")[0:-4]+'000'
    frequency = data.decode('utf-8')[2:].lstrip("0")[0:-3]+'00'
    return frequency

def get_power(sock) -> bool:
    "Query radio for power status"

    sock.sendall(b"PS;")
    data = sock.recv(1024)
    #print(f"Received {data!r}")
    if data.decode('utf-8') == 'PS1;':
        return True
    return False


def save_data(path, data) -> None:
    "Save frequency in a text file, overwriting it"

    with open(path, "w", encoding="utf-8") as outfile:
        outfile.write(data)


@retry(wait=wait_fixed(5))
def main(host, user, password):
    "Main function"
    save_data(OUTPATHST, '-5')
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as sock:
        sock.settimeout(5)
        start_connection(sock, host, 60000)
        authenticate(sock, user, password)
        while get_power(sock):
            frequency = get_frequency(sock)
            save_data(OUTPATHFR, frequency)
            save_data(OUTPATHST, '0')
            time.sleep(1)
    raise ConnectionError


if __name__ == '__main__':
    config = configparser.ConfigParser()
    config.read('/etc/cat_updater_lan890')

    # Call main passing configuration
    main(config['DEFAULT']['Host'], config['DEFAULT']['User'],config['DEFAULT']['Password'])
