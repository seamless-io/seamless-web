import os


class Config:
    SECRET_KEY = os.environ.get('SECRET_KEY', 'hard to guess string')
    LOGIN_DISABLED = os.environ.get('LOGIN_DISABLED', False)
    MAX_CONTENT_LENGTH = 10 * 1024 * 1024  # 10 Mb file size limit

    @staticmethod
    def init_app(app):
        pass
