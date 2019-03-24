from functools import wraps

from flask import make_response


def JSON(f):
    """This decorator passes Content-Type: application/json header"""
    @wraps(f)
    @add_response_headers({'Content-Type': 'application/json'})
    def decorated_function(*args, **kwargs):
        return f(*args, **kwargs)
    return decorated_function


def add_response_headers(headers={}):
    """This decorator adds the headers passed in to the response"""
    def decorator(f):
        @wraps(f)
        def decorated_function(*args, **kwargs):
            resp = make_response(f(*args, **kwargs))
            h = resp.headers
            for header, value in headers.items():
                h[header] = value
            return resp
        return decorated_function
    return decorator