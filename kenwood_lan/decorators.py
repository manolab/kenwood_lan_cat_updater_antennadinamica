"Decorators file for KenwoodLan"

#pylint: disable=no-self-argument,not-callable
def reconnect_if_needed(func):
    "Decorator to re-establish connection in case it breaks"
    def wrapper(self, *args, **kwargs):
        try:
            return func(self, *args, **kwargs)
        except (EOFError, BrokenPipeError, AttributeError):
            self.open_connection()
            return func(self, *args, **kwargs)

    return wrapper
