import secrets


class Config:
    SECRET_KEY = secrets.token_bytes(32)


class ProductionConfig(Config):
    BOOTSTRAP_BOOTSWATCH_THEME = 'LITERA'


class DevelopConfig(Config):
    SECRET_KEY = 'dev'
    BOOTSTRAP_BOOTSWATCH_THEME = 'LITERA'


config = {
    'production': ProductionConfig(),
    'development': DevelopConfig(),
    'default': ProductionConfig(),
}
