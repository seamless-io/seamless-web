import os


class Config:
    SECRET_KEY = os.environ.get('SECRET_KEY', 'hard to guess string')
    LOGIN_DISABLED = os.environ.get('LOGIN_DISABLED', False)

    @staticmethod
    def init_app(app):
        pass
