"This program connects to a Kenwood receiver and gets current frequency"

import argparse
import getpass
import os
import time
from tenacity import retry
from tenacity.wait import wait_fixed

from kenwood_lan import KenwoodLan


def get_frequency(k: KenwoodLan) -> str:
    "Query radio for frequency"

    resp = k.send_command("FA;")

    frequency = resp.decode('utf-8')[2:].lstrip("0")[0:-3]+'00'
    return frequency


def save_frequency(path, data) -> None:
    "Save frequency in a text file, overwriting it"

    with open(path, "w", encoding="utf-8") as outfile:
        outfile.write(data)


@retry(wait=wait_fixed(5))
def main(host, port, outpath, user, password):
    "Main function"
    with KenwoodLan(host, port, user, password) as k:
        while True:
            frequency = get_frequency(k)
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
