class ProcrastinationError(Exception):

    def __init__(self, error_message: str):
        self.error_message = error_message
        super(ProcrastinationError, self).__init__(error_message)

    def __str__(self):
        return f'Something is wrong with your data: {self.error_message}'


class PasswordError(ProcrastinationError):
    pass


class LoginError(ProcrastinationError):
    pass


class AuthorizationError(ProcrastinationError):
    pass
