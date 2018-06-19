import twilio.rest
from mm import app


class Twil(twilio.rest.Client):
    def __init__(self, sid=None, secret=None):
        if not sid and not secret:
            sid = app.config.get('TWILIO_ACCT_SID')
            secret = app.config.get('TWILIO_AUTH_TOKEN')
        super().__init__(sid, secret)
