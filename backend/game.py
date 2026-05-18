from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from models import db, GameSession, SessionPlayer, User, Friendship, GameInvitation, Template
import json
import uuid
from datetime import datetime

game_bp = Blueprint('game', __name__, url_prefix='/api/game')


@game_bp.route('/session/create', methods=['POST'])
@jwt_required()
def create_session():
    """Создание новой игровой сессии"""
    try:
        current_user_id = get_jwt_identity()
        data = request.get_json() or {}

        session = GameSession(
            id=str(uuid.uuid4()),
            creator_id=current_user_id,
            name=data.get('name', 'New Game'),
            is_private=data.get('isPrivate', False),
            max_players=data.get('maxPlayers', 8),
            state=json.dumps({
                'objects': [],
                'drawings': [],
                'settings': {
                    'gridEnabled': True,
                    'gridSize': 50,
                    'snapToGrid': False
                }
            })
        )

        db.session.add(session)

        # Добавляем создателя как игрока
        session_player = SessionPlayer(
            session_id=session.id,
            user_id=current_user_id,
            role='creator',
            is_active=True
        )
        db.session.add(session_player)
        db.session.commit()

        print(f"✅ Session created: {session.id} by user {current_user_id}")

        return jsonify({
            'message': 'Session created',
            'session': session.to_dict(),
            'currentUserId': current_user_id
        }), 201

    except Exception as e:
        db.session.rollback()
        print(f"❌ Create session error: {e}")
        import traceback
        traceback.print_exc()
        return jsonify({'error': 'Failed to create session', 'details': str(e)}), 500


@game_bp.route('/session/join', methods=['POST'])
@jwt_required()
def join_session():
    try:
        current_user_id = get_jwt_identity()
        data = request.get_json() or {}
        session_id = data.get('sessionId')

        if not session_id:
            return jsonify({'error': 'sessionId required'}), 400

        session = GameSession.query.get(session_id)
        if not session:
            return jsonify({'error': 'Session not found'}), 404

        if session.is_full():
            return jsonify({'error': 'Session is full'}), 409

        existing = SessionPlayer.query.filter_by(
            session_id=session_id,
            user_id=current_user_id
        ).first()

        if not existing:
            session_player = SessionPlayer(
                session_id=session_id,
                user_id=current_user_id,
                role='player',
                is_active=True
            )
            db.session.add(session_player)
            db.session.commit()
            print(f"✅ Player {current_user_id} joined session {session_id}")
        else:
            existing.is_active = True
            db.session.commit()
            print(f"✅ Player {current_user_id} reactivated in session {session_id}")

        return jsonify({
            'message': 'Joined session',
            'session': session.to_dict(),
            'currentUserId': current_user_id
        }), 200

    except Exception as e:
        print(f"❌ Join session error: {e}")
        return jsonify({'error': 'Failed to join session', 'details': str(e)}), 500


@game_bp.route('/sessions', methods=['GET'])
@jwt_required()
def get_user_sessions():
    try:
        current_user_id = get_jwt_identity()
        session_players = SessionPlayer.query.filter_by(
            user_id=current_user_id,
            is_active=True
        ).all()

        sessions = []
        for sp in session_players:
            session = GameSession.query.get(sp.session_id)
            if session:
                sessions.append(session.to_dict())

        return jsonify({'sessions': sessions}), 200

    except Exception as e:
        print(f"❌ Get sessions error: {e}")
        return jsonify({'error': 'Failed to fetch sessions', 'details': str(e)}), 500


@game_bp.route('/session/<session_id>', methods=['GET'])
@jwt_required()
def get_session(session_id):
    """Получение информации о сессии"""
    try:
        current_user_id = get_jwt_identity()
        session = GameSession.query.get(session_id)
        if not session:
            return jsonify({'error': 'Session not found'}), 404

        player = SessionPlayer.query.filter_by(
            session_id=session_id,
            user_id=current_user_id
        ).first()

        if not player and session.creator_id != current_user_id:
            return jsonify({'error': 'Access denied'}), 403

        return jsonify({'session': session.to_dict()}), 200

    except Exception as e:
        print(f"❌ Get session error: {e}")
        return jsonify({'error': 'Failed to fetch session', 'details': str(e)}), 500


@game_bp.route('/session/invite', methods=['POST'])
@jwt_required()
def invite_to_session():
    """Пригласить пользователя в сессию"""
    try:
        current_user_id = get_jwt_identity()
        data = request.get_json() or {}
        session_id = data.get('sessionId')
        receiver_id = data.get('receiverId')

        if not session_id or not receiver_id:
            return jsonify({'error': 'sessionId and receiverId required'}), 400

        session = GameSession.query.get(session_id)
        if not session:
            return jsonify({'error': 'Session not found'}), 404

        if session.creator_id != current_user_id:
            return jsonify({'error': 'Only creator can invite'}), 403

        is_friend = Friendship.query.filter(
            ((Friendship.requester_id == current_user_id) & (Friendship.accepter_id == receiver_id)) |
            ((Friendship.requester_id == receiver_id) & (Friendship.accepter_id == current_user_id)),
            Friendship.status == 'accepted'
        ).first()

        if not is_friend:
            return jsonify({'error': 'Can only invite friends'}), 400

        existing = SessionPlayer.query.filter_by(
            session_id=session_id,
            user_id=receiver_id,
            is_active=True
        ).first()

        if existing:
            return jsonify({'error': 'User already in session'}), 409

        invitation = GameInvitation(
            session_id=session_id,
            sender_id=current_user_id,
            receiver_id=receiver_id,
            status='pending'
        )
        db.session.add(invitation)
        db.session.commit()

        from events import socketio
        receiver = User.query.get(receiver_id)
        if receiver and receiver.is_online:
            socketio.emit('invitation:received', {
                'invitation': invitation.to_dict(),
                'session': session.to_dict(),
                'sender': {'id': current_user_id,
                           'username': User.query.get(current_user_id).username if current_user_id else 'Unknown'}
            }, room=receiver_id)

        print(f"✅ Invitation sent to {receiver_id} for session {session_id}")

        return jsonify({'message': 'Invitation sent', 'invitation': invitation.to_dict()}), 201

    except Exception as e:
        print(f"❌ Invite error: {e}")
        return jsonify({'error': 'Failed to send invitation', 'details': str(e)}), 500


@game_bp.route('/session/<session_id>/leave', methods=['POST'])
@jwt_required()
def leave_session(session_id):
    try:
        current_user_id = get_jwt_identity()
        player = SessionPlayer.query.filter_by(
            session_id=session_id,
            user_id=current_user_id
        ).first()

        if player:
            player.is_active = False
            db.session.commit()
            print(f"✅ Player {current_user_id} left session {session_id}")

        return jsonify({'message': 'Left session'}), 200

    except Exception as e:
        print(f"Leave session error: {e}")
        return jsonify({'error': 'Failed to leave session', 'details': str(e)}), 500


@game_bp.route('/session/<session_id>/save', methods=['POST'])
@jwt_required()
def save_session_state(session_id):
    try:
        current_user_id = get_jwt_identity()
        data = request.get_json() or {}
        state = data.get('state')

        if not state:
            return jsonify({'error': 'state required'}), 400

        session = GameSession.query.get(session_id)
        if not session:
            return jsonify({'error': 'Session not found'}), 404

        player = SessionPlayer.query.filter_by(
            session_id=session_id,
            user_id=current_user_id
        ).first()

        if not player and session.creator_id != current_user_id:
            return jsonify({'error': 'Access denied'}), 403

        session.state = json.dumps(state)
        session.updated_at = datetime.utcnow()
        db.session.commit()

        return jsonify({'message': 'Saved', 'sessionId': session_id}), 200
    except Exception as e:
        print(f"❌ Save error: {e}")
        return jsonify({'error': str(e)}), 500


@game_bp.route('/sessions', methods=['GET'])
@jwt_required()
def get_sessions():
    try:
        current_user_id = get_jwt_identity()
        session_players = SessionPlayer.query.filter_by(
            user_id=current_user_id,
            is_active=True
        ).all()
        session_ids = [sp.session_id for sp in session_players]

        created_sessions = GameSession.query.filter_by(
            creator_id=current_user_id
        ).all()
        created_ids = [s.id for s in created_sessions]

        all_session_ids = list(set(session_ids + created_ids))
        sessions = GameSession.query.filter(
            GameSession.id.in_(all_session_ids)
        ).all()

        return jsonify({'sessions': [s.to_dict() for s in sessions]}), 200
    except Exception as e:
        print(f"Get sessions error: {e}")
        return jsonify({'error': 'Failed to fetch sessions', 'details': str(e)}), 500


@game_bp.route('/session/<session_id>', methods=['PUT'])
@jwt_required()
def update_session_metadata(session_id):
    try:
        current_user_id = get_jwt_identity()
        session = GameSession.query.get(session_id)

        if not session:
            return jsonify({'error': 'Session not found'}), 404

        if session.creator_id != current_user_id:
            return jsonify({'error': 'Only creator can update session'}), 403

        data = request.get_json()

        if 'name' in data:
            session.name = data['name']
        if 'max_players' in data:
            session.max_players = data['max_players']
        if 'is_private' in data:
            session.is_private = data['is_private']

        session.updated_at = datetime.utcnow()
        db.session.commit()

        return jsonify(session.to_dict()), 200
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': 'Failed to update session', 'details': str(e)}), 500


@game_bp.route('/session/<session_id>', methods=['DELETE'])
@jwt_required()
def delete_session_endpoint(session_id):
    try:
        current_user_id = get_jwt_identity()
        session = GameSession.query.get(session_id)

        if not session:
            return jsonify({'error': 'Session not found'}), 404

        if session.creator_id != current_user_id:
            return jsonify({'error': 'Only creator can delete session'}), 403

        SessionPlayer.query.filter_by(session_id=session_id).delete()
        db.session.delete(session)
        db.session.commit()

        print(f"Session {session_id} deleted by user {current_user_id}")
        return jsonify({'message': 'Session deleted', 'sessionId': session_id}), 200

    except Exception as e:
        db.session.rollback()
        print(f"Delete session error: {e}")
        import traceback
        traceback.print_exc()
        return jsonify({'error': 'Failed to delete session', 'details': str(e)}), 500

@game_bp.route('/templates', methods=['POST'])
@jwt_required()
def save_template():
    try:
        user_id = get_jwt_identity()
        data = request.get_json() or {}

        if not data.get('name') or not data.get('state'):
            return jsonify({'error': 'Name and state are required'}), 400

        new_template = Template(
            id=str(uuid.uuid4()),
            user_id=user_id,
            name=data['name'],
            description=data.get('description', ''),
            state=json.dumps(data['state'], ensure_ascii=False)
        )

        db.session.add(new_template)
        db.session.commit()

        return jsonify({
            'success': True,
            'message': 'Template saved',
            'template': new_template.to_dict()
        }), 201

    except Exception as e:
        db.session.rollback()
        print(f"❌ Save template error: {e}")
        return jsonify({'error': 'Failed to save template', 'details': str(e)}), 500


@game_bp.route('/templates', methods=['GET'])
@jwt_required()
def get_templates():
    try:
        user_id = get_jwt_identity()
        templates = Template.query.filter_by(user_id=user_id).order_by(Template.created_at.desc()).all()

        return jsonify({
            'success': True,
            'templates': [t.to_dict() for t in templates]
        }), 200

    except Exception as e:
        print(f"❌ Get templates error: {e}")
        return jsonify({'error': 'Failed to fetch templates', 'details': str(e)}), 500


@game_bp.route('/templates/<template_id>', methods=['DELETE'])
@jwt_required()
def delete_template(template_id):
    try:
        user_id = get_jwt_identity()

        template = Template.query.filter_by(id=template_id, user_id=user_id).first()

        if not template:
            return jsonify({'error': 'Template not found or access denied'}), 404

        db.session.delete(template)
        db.session.commit()

        return jsonify({'success': True, 'message': 'Template deleted'}), 200

    except Exception as e:
        db.session.rollback()
        print(f"❌ Delete template error: {e}")
        return jsonify({'error': 'Failed to delete template', 'details': str(e)}), 500