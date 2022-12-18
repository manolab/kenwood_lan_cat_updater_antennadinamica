import argparse

from cat_updater_lan890 import start

if __name__ == '__main__':
    parser = argparse.ArgumentParser(
        description="Do something I don't know..."
    )
    parser.add_argument("--host",
                        dest='host',
                        help="Hostname")
    parser.add_argument("--port",
                        dest='port',
                        help="Port")
    parser.add_argument("--output",
                        dest="output",
                        help="Path of the file to write results to")
    parser.add_argument("--user",
                        dest="user",
                        help='Username')
    parser.add_argument("--password",
                        dest="password",
                        help="Password")
    args_namespace = parser.parse_args()
    args = vars(args_namespace)

    start(**args)
