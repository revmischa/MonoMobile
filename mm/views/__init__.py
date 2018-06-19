from mm import app
from flask import jsonify

class APIError(Exception):
    """Generic API exception."""

    def __init__(self, message, code=None, payload=None):
        """Init with message, status code, payload."""
        Exception.__init__(self)
        if not message and hasattr(self.__class__, 'message'):
            self.message = self.__class__.message
        else:
            self.message = message
        self.code = code
        self.payload = payload

    def to_dict(self):
        """Serialize for return."""
        rv = dict(self.payload or ())
        rv['message'] = self.message
        rv['is_error'] = True
        return rv


class APIBadRequestError(APIError):
    """Resource not found."""
    message = "Bad request"

    def __init__(self, message=None, payload=None):
        """HTTP 400: Bad request."""
        APIError.__init__(self, message, code=400, payload=payload)

@app.errorhandler(APIError)
def handle_api_error(error):
    """Handle when APIError is raised during a request."""
    response = jsonify(error.to_dict())
    response.code = error.code if error.code else 400
    return response
