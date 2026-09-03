import jwt
from functools import wraps
from flask import request, jsonify, current_app


def jwt_required(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        token = None
        auth_header = request.headers.get('Authorization', '')
        if auth_header.startswith('Bearer '):
            token = auth_header.split(' ')[1]
        if not token:
            return jsonify({'error': 'Missing authorization token'}), 401
        try:
            payload = jwt.decode(token, current_app.config['SECRET_KEY'], algorithms=['HS256'])
            request.current_user_id = payload.get('user_id')
            request.current_user_role = payload.get('role', 'user')
        except jwt.ExpiredSignatureError:
            return jsonify({'error': 'Token has expired'}), 401
        except jwt.InvalidTokenError:
            return jsonify({'error': 'Invalid token'}), 401
        return f(*args, **kwargs)
    return decorated


def jwt_optional(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        token = None
        auth_header = request.headers.get('Authorization', '')
        if auth_header.startswith('Bearer '):
            token = auth_header.split(' ')[1]
        request.current_user_id = None
        request.current_user_role = None
        if token:
            try:
                payload = jwt.decode(token, current_app.config['SECRET_KEY'], algorithms=['HS256'])
                request.current_user_id = payload.get('user_id')
                request.current_user_role = payload.get('role', 'user')
            except (jwt.ExpiredSignatureError, jwt.InvalidTokenError):
                pass
        return f(*args, **kwargs)
    return decorated


def role_required(*allowed_roles):
    def decorator(f):
        @wraps(f)
        def decorated(*args, **kwargs):
            role = getattr(request, 'current_user_role', None)
            if not role:
                return jsonify({'error': 'Authentication required'}), 401
            if role == 'admin' or role in allowed_roles:
                return f(*args, **kwargs)
            return jsonify({'error': f'Role {role} is not allowed. Required: {allowed_roles}'}), 403
        return decorated
    return decorator
