from flask import Blueprint, request, jsonify
from extensions import db
from models.user import User
from utils.jwt import generate_token

auth_bp = Blueprint('auth_bp', __name__)

@auth_bp.route('/register', methods=['POST'])
def register():
    data = request.get_json()
    if not data or not data.get('username') or not data.get('password'):
        return jsonify({"message": "Username and password required"}), 400
    if len(data['username']) < 3 or len(data['password']) < 6:
        return jsonify({"message": "Username min 3 chars, password min 6 chars"}), 400
    if User.query.filter_by(username=data['username']).first():
        return jsonify({"message": "User already exists"}), 400
    user = User(username=data['username'], role=data.get('role', 'user'))
    user.set_password(data['password'])
    db.session.add(user)
    db.session.commit()
    return jsonify({"message": "User registered"}), 201

@auth_bp.route('/login', methods=['POST'])
def login():
    data = request.get_json()
    if not data or not data.get('username') or not data.get('password'):
        return jsonify({"message": "Username and password required"}), 400
    user = User.query.filter_by(username=data['username']).first()
    if not user or not user.check_password(data['password']):
        return jsonify({"message": "Invalid credentials"}), 401
    token = generate_token(user)
    return jsonify({"token": token})