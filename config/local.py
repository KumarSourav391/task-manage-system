from config.base import BaseConfig

class LocalConfig(BaseConfig):
    SQLALCHEMY_DATABASE_URI = 'sqlite:///task.db'
