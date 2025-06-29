import os

class BaseConfig:
    SECRET_KEY = os.environ.get('SECRET_KEY', 'super-secret-key')
    SQLALCHEMY_TRACK_MODIFICATIONS = False