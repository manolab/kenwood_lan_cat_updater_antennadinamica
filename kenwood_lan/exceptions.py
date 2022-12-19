"Define exceptions for the rest of the program"

class AuthenticationException(Exception):
    "Raised when authentication fails"

    def __init__(self, errorcode="unknown") -> None:
        self.message = f"Authentication failed with code {errorcode}"
        super().__init__(errorcode)
