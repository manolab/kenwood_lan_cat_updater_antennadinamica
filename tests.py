"Run tests to check correct behaviour"

from unittest import TestCase
from unittest.mock import Mock
from cat_updater_lan890 import authenticate, get_frequency
from exceptions import AuthenticationException

class TestProtocol(TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        # This code is run before every test
        cls.sock = Mock()
        cls.sock.recv = Mock()

    def test_login_success(self):
        "Check authentication continues on good output"
        self.sock.recv.side_effect = [b"##ID1;"]

        res = authenticate(self.sock, "user", "password")

        self.assertIsNone(res)

    def test_login_fail(self):
        "Check authentication continues on good output"
        self.sock.recv.side_effect = [b"fail;"]

        self.assertRaises(AuthenticationException, authenticate, self.sock, "user", "password")

    def test_frequency_query_response(self):
        "Check correct parsing of frequency"
        self.sock.recv.side_effect = [b"FA00007135250;"]

        frequency = get_frequency(self.sock)

        self.assertEqual(frequency, "7135200")
