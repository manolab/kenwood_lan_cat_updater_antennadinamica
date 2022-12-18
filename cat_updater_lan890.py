"This program connects to a Kenwood receiver and gets current frequency"

import argparse
import getpass
import os
import socket
import time
from exceptions import AuthenticationException


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


def main(host, port, outpath, user, password):
    "Main function"
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as sock:
        start_connection(sock, host, port)
        authenticate(sock, user, password)
        while True:
            frequency = get_frequency(sock)
            save_frequency(outpath, frequency)
            time.sleep(1)


if __name__ == '__main__':
    parser = argparse.ArgumentParser(
        description="Connect to Kenwood receiver and save frequency to file"
    )
    parser.add_argument(dest='host',
                        help="Hostname or IP of receiver",
                        )
    parser.add_argument(dest='port',
                        help="Port to connect to",
                        type=int,
                        nargs="?"
                        )
    parser.add_argument(dest="outpath",
                        help="Path of file to save to. CAUTION: File will be overwritten")
    parser.add_argument('-u', "--user",
                        dest="user",
                        help='Username, or env var USER',
                        default=os.environ.get("USER")
                        )
    parser.add_argument('-p', "--password",
                        dest="password",
                        # Save as True if flag is present, otherwise use env var
                        action="store_true",
                        help="Password (interactive) or env var PASSWORD",
                        default=os.environ.get("PASSWORD")
                        )
    args_namespace = parser.parse_args()
    args = vars(args_namespace)

    if args.get("password") is True:
        # if "password" is True, user passed -p flag. Ask for password
        interactive_password = getpass.getpass()
        args.update({"password": interactive_password})

    # Call main passing dict as named args
    main(**args)