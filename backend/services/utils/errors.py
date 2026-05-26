from flask import jsonify

class APIError(Exception):
    """Base API Exception for structured error returns"""
    def __init__(self, message, status_code=500, code="INTERNAL_ERROR"):
        super().__init__(message)
        self.message = message
        self.status_code = status_code
        self.code = code

    def to_dict(self):
        return {
            "success": False,
            "error": self.message,
            "code": self.code
        }

class BadRequestError(APIError):
    def __init__(self, message="Bad Request"):
        super().__init__(message, status_code=400, code="BAD_REQUEST")

class UnauthorizedError(APIError):
    def __init__(self, message="Unauthorized"):
        super().__init__(message, status_code=401, code="UNAUTHORIZED")

class NotFoundError(APIError):
    def __init__(self, message="Resource Not Found"):
        super().__init__(message, status_code=404, code="NOT_FOUND")

class RateLimitError(APIError):
    def __init__(self, message="Too Many Requests"):
        super().__init__(message, status_code=429, code="RATE_LIMIT_EXCEEDED")

def register_error_handlers(app):
    """Registers standard error handlers on a Flask app instance"""
    
    @app.errorhandler(APIError)
    def handle_api_error(error):
        response = jsonify(error.to_dict())
        response.status_code = error.status_code
        return response

    @app.errorhandler(400)
    def handle_bad_request(error):
        return jsonify({
            "success": False,
            "error": str(error.description) if hasattr(error, 'description') else "Bad Request",
            "code": "BAD_REQUEST"
        }), 400

    @app.errorhandler(404)
    def handle_not_found(error):
        return jsonify({
            "success": False,
            "error": "The requested resource could not be found.",
            "code": "NOT_FOUND"
        }), 404

    @app.errorhandler(429)
    def handle_rate_limit(error):
        return jsonify({
            "success": False,
            "error": "Rate limit exceeded. Please try again later.",
            "code": "RATE_LIMIT_EXCEEDED"
        }), 429

    @app.errorhandler(500)
    def handle_internal_server_error(error):
        return jsonify({
            "success": False,
            "error": "An internal server error occurred.",
            "code": "INTERNAL_SERVER_ERROR"
        }), 500

    @app.errorhandler(Exception)
    def handle_unhandled_exception(error):
        # Log the detailed exception here if a logger is set up
        import traceback
        traceback.print_exc()
        return jsonify({
            "success": False,
            "error": "An unexpected error occurred.",
            "code": "INTERNAL_SERVER_ERROR"
        }), 500
