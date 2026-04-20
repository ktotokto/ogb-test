from flask import request as flask_request
from flask_socketio import emit, join_room, leave_room, rooms
from flask_jwt_extended import decode_token
from functools import wraps
from models import db, GameSession, SessionPlayer, User
import json

# SocketIO instance will be set from app.py
socketio = None


def init_socketio(sio):
    global socketio
    socketio = sio
    register_events()


def get_user_from_token(token):
    """Extract user ID from JWT token."""
    try:
        decoded = decode_token(token)
        return decoded['sub']
    except Exception:
        return None


def authenticated_only(f):
    """Decorator to require authentication for SocketIO events."""

    @wraps(f)
    def wrapped(*args, **kwargs):
        token = kwargs.pop('token', None)
        if not token:
            token = flask_request.args.get('token')

        user_id = get_user_from_token(token)
        if not user_id:
            emit('error', {'message': 'Authentication required'})
            return
        kwargs['user_id'] = user_id
        return f(*args, **kwargs)

    return wrapped


def register_events():
    """Register all SocketIO event handlers."""

    @socketio.on('connect')
    def handle_connect():
        token = flask_request.args.get('token')
        user_id = get_user_from_token(token)
        if user_id:
            emit('connected', {'userId': user_id})

    @socketio.on('disconnect')
    def handle_disconnect(reason=None):  # ← FIX: добавить параметр
        """Handle client disconnect — properly"""
        sid = flask_request.sid
        if not sid:
            return

        # ✅ rooms() returns list[str], not dict!
        user_rooms = rooms(sid)  # Get rooms for this socket

        for room_id in user_rooms:
            # Skip personal room (sid == room_id)
            if room_id == sid:
                continue

            # Notify others in this session that player left
            session = GameSession.query.get(room_id)
            if session:
                player = SessionPlayer.query.filter_by(
                    session_id=room_id,
                    user_id=get_user_from_token(flask_request.args.get('token'))
                ).first()

                if player:
                    emit('player-offline', {
                        'userId': player.user_id,
                        'username': player.user.username if player.user else 'Unknown'
                    }, room=room_id, include_self=False)

    @socketio.on('join-session')
    def handle_join_session(data):
        token = flask_request.args.get('token')
        user_id = get_user_from_token(token)
        if not user_id:
            emit('error', {'message': 'Authentication required'})
            return

        session_id = data.get('sessionId')
        if not session_id:
            emit('error', {'message': 'Session ID required'})
            return

        session = GameSession.query.get(session_id)
        if not session:
            emit('error', {'message': 'Session not found'})
            return

        association = SessionPlayer.query.filter_by(
            session_id=session_id, user_id=user_id
        ).first()
        if not association:
            emit('error', {'message': 'Not a member of this session'})
            return

        join_room(session_id)

        emit('session-state', {
            'sessionId': session_id,
            'state': json.loads(session.state) if session.state else {},
            'players': [p.to_dict() for p in session.players]
        })

        user = User.query.get(user_id)
        emit('player-online', {
            'user': user.to_dict() if user else {'id': user_id}
        }, room=session_id, include_self=False)

    @socketio.on('leave-session')
    def handle_leave_session(data):
        session_id = data.get('sessionId')
        if session_id:
            leave_room(session_id)

    # --- Real-time game events ---

    @socketio.on('object-move')
    def handle_object_move(data):
        token = flask_request.args.get('token')
        user_id = get_user_from_token(token)
        if not user_id:
            return

        session_id = data.get('sessionId')
        if session_id:
            data['userId'] = user_id
            emit('object-move', data, room=session_id, include_self=False)

    @socketio.on('object-select')
    def handle_object_select(data):
        token = flask_request.args.get('token')
        user_id = get_user_from_token(token)
        if not user_id:
            return

        session_id = data.get('sessionId')
        if session_id:
            data['userId'] = user_id
            emit('object-select', data, room=session_id, include_self=False)

    @socketio.on('object-flip')
    def handle_object_flip(data):
        token = flask_request.args.get('token')
        user_id = get_user_from_token(token)
        if not user_id:
            return

        session_id = data.get('sessionId')
        if session_id:
            data['userId'] = user_id
            emit('object-flip', data, room=session_id, include_self=False)

    @socketio.on('object-rotate')
    def handle_object_rotate(data):
        token = flask_request.args.get('token')
        user_id = get_user_from_token(token)
        if not user_id:
            return

        session_id = data.get('sessionId')
        if session_id:
            data['userId'] = user_id
            emit('object-rotate', data, room=session_id, include_self=False)

    @socketio.on('object-delete')
    def handle_object_delete(data):
        token = flask_request.args.get('token')
        user_id = get_user_from_token(token)
        if not user_id:
            return

        session_id = data.get('sessionId')
        if session_id:
            data['userId'] = user_id
            emit('object-delete', data, room=session_id, include_self=False)

    @socketio.on('object-add')
    def handle_object_add(data):
        token = flask_request.args.get('token')
        user_id = get_user_from_token(token)
        if not user_id:
            return

        session_id = data.get('sessionId')
        if session_id:
            data['userId'] = user_id
            emit('object-add', data, room=session_id, include_self=False)

    @socketio.on('stack-add')
    def handle_stack_add(data):
        token = flask_request.args.get('token')
        user_id = get_user_from_token(token)
        if not user_id:
            return

        session_id = data.get('sessionId')
        if session_id:
            data['userId'] = user_id
            emit('stack-add', data, room=session_id, include_self=False)

    @socketio.on('stack-remove')
    def handle_stack_remove(data):
        token = flask_request.args.get('token')
        user_id = get_user_from_token(token)
        if not user_id:
            return

        session_id = data.get('sessionId')
        if session_id:
            data['userId'] = user_id
            emit('stack-remove', data, room=session_id, include_self=False)

    @socketio.on('draw-update')
    def handle_draw_update(data):
        token = flask_request.args.get('token')
        user_id = get_user_from_token(token)
        if not user_id:
            return

        session_id = data.get('sessionId')
        if session_id:
            data['userId'] = user_id
            emit('draw-update', data, room=session_id, include_self=False)

    @socketio.on('draw-clear')
    def handle_draw_clear(data):
        token = flask_request.args.get('token')
        user_id = get_user_from_token(token)
        if not user_id:
            return

        session_id = data.get('sessionId')
        if session_id:
            data['userId'] = user_id
            emit('draw-clear', data, room=session_id, include_self=False)

    @socketio.on('zoom-change')
    def handle_zoom_change(data):
        token = flask_request.args.get('token')
        user_id = get_user_from_token(token)
        if not user_id:
            return

        session_id = data.get('sessionId')
        if session_id:
            data['userId'] = user_id
            emit('zoom-change', data, room=session_id, include_self=False)

    @socketio.on('pan-change')
    def handle_pan_change(data):
        token = flask_request.args.get('token')
        user_id = get_user_from_token(token)
        if not user_id:
            return

        session_id = data.get('sessionId')
        if session_id:
            data['userId'] = user_id
            emit('pan-change', data, room=session_id, include_self=False)

    @socketio.on('save-state')
    def handle_save_state(data):
        token = flask_request.args.get('token')
        user_id = get_user_from_token(token)
        if not user_id:
            return

        session_id = data.get('sessionId')
        state = data.get('state')
        if not session_id or not state:
            emit('error', {'message': 'Session ID and state required'})
            return

        session = GameSession.query.get(session_id)
        if not session:
            emit('error', {'message': 'Session not found'})
            return

        session.state = json.dumps(state)
        db.session.commit()

        emit('state-saved', {'sessionId': session_id}, room=session_id)

    @socketio.on('chat-message')
    def handle_chat_message(data):
        token = flask_request.args.get('token')
        user_id = get_user_from_token(token)
        if not user_id:
            return

        session_id = data.get('sessionId')
        message = data.get('message', '').strip()
        if not session_id or not message:
            return

        user = User.query.get(user_id)
        emit('chat-message', {
            'userId': user_id,
            'username': user.username if user else 'Unknown',
            'message': message,
            'timestamp': __import__('datetime').datetime.utcnow().isoformat()
        }, room=session_id)