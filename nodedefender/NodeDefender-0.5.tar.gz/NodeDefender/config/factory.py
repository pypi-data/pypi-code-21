import NodeDefender

class Config:
    DEBUG = False
    TESTING = False
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    SECRET_KEY = NodeDefender.config.general.secret_key()
    SECRET_SALT = NodeDefender.config.general.secret_salt()
    SERVER_NAME = NodeDefender.config.general.server_name()
    PORT = int(NodeDefender.config.general.server_port())
    SELF_REGISTRATION = NodeDefender.config.general.self_registration()
    WTF_CSRF_ENABLED = False
    
    DATABASE = NodeDefender.config.database.enabled()
    if DATABASE:
        DATABASE_ENGINE = NodeDefender.config.database.engine()
        SQLALCHEMY_DATABASE_URI = NodeDefender.config.database.uri()

    LOGGING = NodeDefender.config.logging.enabled()
    if LOGGING:
        LOGGING_LEVEL = NodeDefender.config.logging.level()
        LOGGING_TYPE = NodeDefender.config.logging.type()
        LOGGING_NAME = NodeDefender.config.logging.name()
        LOGGING_SERVER = NodeDefender.config.logging.server()
        LOGGING_PORT = NodeDefender.config.logging.port()


    MAIL = NodeDefender.config.mail.enabled()
    if MAIL:
        MAIL_SERVER = NodeDefender.config.mail.server()
        MAIL_PORT = NodeDefender.config.mail.port()
        MAIL_USE_TLS = NodeDefender.config.mail.tls()
        MAIL_USE_SSL = NodeDefender.config.mail.ssl()
        MAIL_USERNAME = NodeDefender.config.mail.username()
        MAIL_PASSWORD = NodeDefender.config.mail.password()

    CELERY = NodeDefender.config.celery.enabled()
    if CELERY:
        CELERY_BROKER = NodeDefender.config.celery.broker()
        CELERY_BROKER_URI = NodeDefender.config.celery.broker_uri()
        CELERY_BACKEND_URI = NodeDefender.config.celery.backend_uri()

class ProductionConfig(Config):
    pass

class DevelopmentConfig(Config):
    DEBUG = True
 
class TestingConfig(Config):
    TESTING = True
    DATABASE = False
    LOGGING = False
    MAIL = False
    CELERY = False
