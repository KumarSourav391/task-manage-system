import jwt
from flask import request, jsonify
from functools import wraps
from config.local import LocalConfig

SECRET_KEY = LocalConfig.SECRET_KEY

def generate_token(user):
    payload = {"id": user.id, "username": user.username, "role": user.role}
    return jwt.encode(payload, SECRET_KEY, algorithm="HS256")

def decode_token(token):
    return jwt.decode(token, SECRET_KEY, algorithms=["HS256"])

def token_required(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        token = None
        if 'Authorization' in request.headers:
            token = request.headers['Authorization'].split(" ")[1]
        if not token:
            return jsonify({"message": "Token is missing"}), 401
        try:
            current_user = decode_token(token)
        except:
            return jsonify({"message": "Token is invalid"}), 401
        return f(current_user, *args, **kwargs)
    return decorated