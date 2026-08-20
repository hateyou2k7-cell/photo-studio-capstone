# Middleware functions for processing requests and responses

from flask import request, jsonify
from werkzeug.exceptions import HTTPException

def log_request_info(app):
    app.logger.debug('Headers: %s', request.headers)
    app.logger.debug('Body: %s', request.get_data())

def handle_options_request():
    return jsonify({'message': 'CORS preflight response'}), 200

def error_handling_middleware(error):
    status_code = error.code if isinstance(error, HTTPException) else 500
    response = jsonify({'error': str(error)})
    response.status_code = status_code
    return response

def add_custom_headers(response):
    response.headers['X-Custom-Header'] = 'Value'
    return response

def middleware(app):
    @app.before_request
    def before_request():
        log_request_info(app)

    @app.after_request
    def after_request(response):
        return add_custom_headers(response)

    @app.errorhandler(Exception)
    def handle_exception(error):
        return error_handling_middleware(error)

    @app.route('/options', methods=['OPTIONS'])
    def options_route():
        return handle_options_request()