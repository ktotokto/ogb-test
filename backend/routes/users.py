from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from models import db, User
from sqlalchemy import or_

users_bp = Blueprint('users', __name__, url_prefix='/api/users')


@users_bp.route('', methods=['GET'])
@jwt_required()
def search_users():
    try:
        current_user_id = get_jwt_identity()

        query = request.args.get('q') or request.args.get('query', '').strip()

        if len(query) < 2:
            return jsonify([]), 200

        users = User.query.filter(
            or_(
                User.username.ilike(f'%{query}%'),
                User.email.ilike(f'%{query}%')
            ),
            User.id != current_user_id
        ).limit(20).all()

        return jsonify({
            'users': [u.to_dict() for u in users]
        }), 200

    except Exception as e:
        print(f"Search error: {e}")
        return jsonify({'error': 'Search failed', 'details': str(e)}), 500


@users_bp.route('/<user_id>', methods=['GET'])
@jwt_required()
def get_user(user_id):
    try:
        user = User.query.get(user_id)

        if not user:
            return jsonify({'error': 'User not found'}), 404

        return jsonify({
            'user': user.to_dict()
        }), 200

    except Exception as e:
        print(f"Get user error: {e}")
        return jsonify({'error': 'Failed to get user', 'details': str(e)}), 500


@users_bp.route('/online', methods=['GET'])
@jwt_required()
def get_online_users():
    try:
        online_users = User.query.filter_by(is_online=True).all()

        return jsonify({
            'users': [u.to_dict() for u in online_users]
        }), 200

    except Exception as e:
        print(f"Get online users error: {e}")
        return jsonify({'error': 'Failed to get online users', 'details': str(e)}), 500