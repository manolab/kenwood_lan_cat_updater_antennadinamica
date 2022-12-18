"Run tests to check correct behaviour"

from unittest import TestCase
from unittest.mock import Mock
from cat_updater_lan890 import authenticate
from exceptions import AuthenticationException

class TestProtocol(TestCase):
    def test_login_success(self):
        "Check authentication continues on good output"
        sock = Mock()
        sock.recv = Mock()
        sock.recv.side_effect = [b"##ID1;"]

        res = authenticate(sock, "user", "password")

        self.assertIsNone(res)

    def test_login_fail(self):
        "Check authentication continues on good output"
        sock = Mock()
        sock.recv = Mock()
        sock.recv.side_effect = [b"fail;"]

        self.assertRaises(AuthenticationException, authenticate, sock, "user", "password")