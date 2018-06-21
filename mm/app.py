from flask import Flask
import logging
import mm.log
import os
import sys
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from flask_cors import CORS

lib_path = os.path.abspath(os.path.join(__file__, '..', '..'))
sys.path.append(lib_path)

# logging
log = logging.getLogger(__name__)
log.setLevel(logging.DEBUG)

app = Flask(__name__)

# CORS
CORS(app)

# load configuration
config_obj = os.environ.get('MM_CONFIG', 'mm.config.DevelopmentConfig')
app.config.from_object(config_obj)
app.config.from_pyfile('../local.cfg', silent=True)
if not app.config.get('TWILIO_ACCT_SID') or not app.config.get('TWILIO_AUTH_TOKEN'):
    print("Please configure TWILIO_ACCT_SID and TWILIO_AUTH_TOKEN")

# database
if os.environ.get("DUMP_SQL"):
    print("Enabling query logging")
    logging.getLogger('sqlalchemy.engine').setLevel(logging.INFO)
db = SQLAlchemy(app)
Migrate(app, db)
