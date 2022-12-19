"Library to manage connections towards Kenwood radio receivers"

from telnetlib import Telnet
from .exceptions import AuthenticationException
from .decorators import reconnect_if_needed

class KenwoodLan:
    """
    Class to talk with Kenwood radio receivers
    """

    def __init__(self, host: str, port: int, username: str, password: str) -> None:
        self.host = host
        self.port = port
        self._username = username
        self._password = password
        self._connection = Telnet()

    @reconnect_if_needed
    def send_command(self, command: str) -> str:
        """Send commands through connection

        :param command: Command as string
        :type command: str
        :return: Output of command
        :rtype: str
        """
        self._connection.write(command.encode('ascii'))
        output = self._connection.read_until(b";").decode('ascii')

        return output

    def open_connection(self) -> None:
        "Open connection, check availability and authenticate"

        self._connection.open(self.host, self.port)

        resp = self.send_command("##CN;")

        if resp != '##CN1;':
            raise ConnectionError

        auth_string = "##ID0" + \
                      str(len(self._username)).zfill(2) + \
                      str(len(self._password)).zfill(2) + \
                      self._username + self._password + ";"

        resp = self.send_command(auth_string)
        if resp != '##ID1;':
            raise AuthenticationException(resp)

        # Check effective need
        self.send_command("AI0;")

    def close_connection(self) -> None:
        "Close telnet connection"
        self._connection.close()

    def __enter__(self):
        self.open_connection()
        return self

    def __exit__(self, exc_type, exc_value, exc_traceback):
        self._connection.close()
