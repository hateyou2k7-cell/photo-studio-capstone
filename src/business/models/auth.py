from datetime import date


class Auth:
    def __init__(self, username: str, password: str, passwordcomfirm: str = '', email: str = '', id=None, role: str = 'user'):
        self.username = username
        self.password = password
        self.passwordcomfirm = passwordcomfirm
        self.email = email
        self.id = id
        self.role = role