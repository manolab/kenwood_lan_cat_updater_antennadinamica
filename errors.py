class AuthException(Exception):
    """Raised when authentication fails"""

    def __init__(self, errorcode="Unknown") -> None:
        self.message = f"Authentication failed with code {errorcode}"
        super().__init__(self.message, errorcode)
