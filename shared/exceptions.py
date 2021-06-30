class Error(Exception):
    """Password validation errors"""

    def __init__(self, error_message: str):
        self.error_message = error_message

    def __str__(self):
        return f'Something is wrong with your data: {self.error_message}'


class PasswordError(Error):
    pass


class LoginError(Error):
    pass
