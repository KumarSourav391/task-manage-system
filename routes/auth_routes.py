from flask import Blueprint, request, jsonify
from extensions import db
from models.user import User
from utils.jwt import generate_token

auth_bp = Blueprint('auth_bp', __name__)

@auth_bp.route('/register', methods=['POST'])
def register():
    data = request.get_json()
    if User.query.filter_by(username=data['username']).first():
        return jsonify({"message": "User already exists"}), 400
    user = User(username=data['username'], password=data['password'], role=data.get('role', 'user'))
    db.session.add(user)
    db.session.commit()
    return jsonify({"message": "User registered"}), 201

@auth_bp.route('/login', methods=['POST'])
def login():
    data = request.get_json()
    user = User.query.filter_by(username=data['username'], password=data['password']).first()
    if not user:
        return jsonify({"message": "Invalid credentials"}), 401
    token = generate_token(user)
    return jsonify({"token": token})