from mm import app
import logging

log = logging.getLogger(__name__)


@app.errorhandler(500)
def internal_error(error):
    log.exception(error)
    return make_message_response("Sorry, the dialplan application had an internal error. Please try again in a bit. We'll fix it, we swear.")
