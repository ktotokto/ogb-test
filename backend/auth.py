from flask import Blueprint, request, jsonify
from flask_jwt_extended import create_access_token, jwt_required, get_jwt_identity
from werkzeug.security import generate_password_hash, check_password_hash
from sqlalchemy import or_
from models import db, User
import uuid
import re

auth_bp = Blueprint('auth', __name__, url_prefix='/api/auth')


def validate_email(email):
    pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
    return re.match(pattern, email) is not None


@auth_bp.route('/register', methods=['POST'])
def register():
    try:
        data = request.get_json()
        if not data:
            return jsonify({'error': 'No data provided'}), 400

        username = data.get('username', '').strip()
        email = data.get('email', '').strip().lower()
        password = data.get('password', '')

        if not username or not email or not password:
            return jsonify({'error': 'All fields are required'}), 400

        if len(username) < 3:
            return jsonify({'error': 'Username must be at least 3 characters'}), 400

        if len(password) < 6:
            return jsonify({'error': 'Password must be at least 6 characters'}), 400

        if not validate_email(email):
            return jsonify({'error': 'Invalid email format'}), 400

        if User.query.filter(
                or_(User.username == username, User.email == email)
        ).first():
            return jsonify({'error': 'Username or email already exists'}), 409

        user_id = str(uuid.uuid4())
        user = User(
            id=user_id,
            username=username,
            email=email,
            password_hash=generate_password_hash(password)
        )

        db.session.add(user)
        db.session.commit()

        access_token = create_access_token(identity=user_id)

        return jsonify({
            'accessToken': access_token,
            'user': user.to_dict()
        }), 201
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': 'Registration failed', 'details': str(e)}), 500


@auth_bp.route('/login', methods=['POST'])
def login():
    try:
        data = request.get_json()
        if not data:
            return jsonify({'error': 'No data provided'}), 400

        username = data.get('username', '').strip()
        password = data.get('password', '')

        if not username or not password:
            return jsonify({'error': 'Username and password are required'}), 400

        user = User.query.filter(User.username == username).first()

        if not user or not check_password_hash(user.password_hash, password):
            return jsonify({'error': 'Invalid credentials'}), 401

        access_token = create_access_token(identity=user.id)

        return jsonify({
            'accessToken': access_token,
            'user': user.to_dict()
        }), 200
    except Exception as e:
        return jsonify({'error': 'Login failed', 'details': str(e)}), 500


@auth_bp.route('/me', methods=['GET'])
@jwt_required()
def get_current_user():
    try:
        user_id = get_jwt_identity()
        user = User.query.get(user_id)

        if not user:
            return jsonify({'error': 'User not found'}), 404

        return jsonify({
            'accessToken': request.headers.get('Authorization', '').replace('Bearer ', ''),
            'user': user.to_dict()
        }), 200
    except Exception as e:
        return jsonify({'error': 'Failed to fetch user', 'details': str(e)}), 500


@auth_bp.route('/user/profile', methods=['GET'])
@jwt_required()
def get_profile():
    try:
        user_id = get_jwt_identity()
        user = User.query.get(user_id)

        if not user:
            return jsonify({'error': 'User not found'}), 404

        return jsonify(user.to_dict()), 200
    except Exception as e:
        return jsonify({'error': 'Failed to fetch profile', 'details': str(e)}), 500


@auth_bp.route('/user/profile', methods=['PUT'])
@jwt_required()
def update_profile():
    try:
        user_id = get_jwt_identity()
        user = User.query.get(user_id)

        if not user:
            return jsonify({'error': 'User not found'}), 404

        data = request.get_json()

        if 'username' in data:
            existing = User.query.filter_by(username=data['username']).first()
            if existing and existing.id != user_id:
                return jsonify({'error': 'Username already taken'}), 400
            if len(data['username'].strip()) < 3:
                return jsonify({'error': 'Username must be at least 3 characters'}), 400
            user.username = data['username'].strip()

        if 'email' in data:
            existing = User.query.filter_by(email=data['email'].lower()).first()
            if existing and existing.id != user_id:
                return jsonify({'error': 'Email already registered'}), 400
            if not validate_email(data['email']):
                return jsonify({'error': 'Invalid email format'}), 400
            user.email = data['email'].lower()

        if 'avatar_url' in data:
            user.avatar_url = data['avatar_url']

        if 'banner_url' in data:
            user.banner_url = data['banner_url']

        if 'bio' in data:
            user.bio = data['bio']

        db.session.commit()

        return jsonify(user.to_dict()), 200
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': 'Failed to update profile', 'details': str(e)}), 500


@auth_bp.route('/users', methods=['GET'])
@jwt_required()
def search_users():
    try:
        query = request.args.get('q', '').strip()

        if not query or len(query) < 2:
            return jsonify({'users': []}), 200

        current_user_id = get_jwt_identity()

        users = User.query.filter(
            or_(
                User.username.ilike(f'%{query}%'),
                User.email.ilike(f'%{query}%')
            ),
            User.id != current_user_id
        ).limit(20).all()

        return jsonify({'users': [u.to_dict() for u in users]}), 200
    except Exception as e:
        return jsonify({'error': 'Search failed', 'details': str(e)}), 500