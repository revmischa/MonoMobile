import os

class Config(object):
    DEBUG = os.environ.get("DEBUG", default=False)
    TESTING = False
    SQLALCHEMY_DATABASE_URI = os.getenv('DATABASE_URL', 'postgresql:///mm')
    SECRET_KEY = os.environ.get("SECRET_KEY", default="SET ME")
    SQLALCHEMY_TRACK_MODIFICATIONS = False

    # set these!
    TWILIO_ACCT_SID = os.environ.get("TWILIO_ACCT_SID")
    TWILIO_AUTH_TOKEN = os.environ.get("TWILIO_AUTH_TOKEN")

    # dialplan
    DIALPLAN_EXT_DIAL_PREFIX = '#'  # prefix for dialing subscribers by extension

    # set this to a string to make dev or single-network deployments simple
    DEFAULT_NETWORK = None
    RATE_PLAN = os.environ.get('RATE_PLAN', 'WP983c32f8439200744d4a45992864e9df')
    MASTER_PHONE_NUMBER = '+18774197477'

class ProductionConfig(Config):
    DEBUG = False

class DevelopmentConfig(Config):
    DEFAULT_NETWORK = 'development'
    DEBUG = True

class TestingConfig(Config):
    TESTING = True
