from flask_socketio import emit, join_room, leave_room, rooms
from flask_jwt_extended import decode_token
from functools import wraps
from models import db, GameSession, SessionPlayer
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
            # Try from request headers or query params
            from flask import request as flask_request
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
        from flask import request as flask_request
        token = flask_request.args.get('token')
        user_id = get_user_from_token(token)
        if user_id:
            emit('connected', {'userId': user_id})

    @socketio.on('disconnect')
    def handle_disconnect():
        # Remove user from active players in rooms
        from flask import request as flask_request
        sid = flask_request.sid if hasattr(flask_request, 'sid') else None
        if sid:
            # Notify rooms that user left
            for room_id, sids in rooms().items():
                if room_id != sid:  # Skip personal room
                    session = GameSession.query.get(room_id)
                    if session:
                        player = SessionPlayer.query.filter_by(
                            session_id=room_id
                        ).first()
                        if player:
                            user = player.user if hasattr(player, 'user') else None
                            emit('player-offline', {
                                'userId': player.user_id
                            }, room=room_id, include_self=False)

    @socketio.on('join-session')
    def handle_join_session(data):
        from flask import request as flask_request
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

        # Check membership
        association = SessionPlayer.query.filter_by(
            session_id=session_id, user_id=user_id
        ).first()
        if not association:
            emit('error', {'message': 'Not a member of this session'})
            return

        join_room(session_id)

        # Send current state to joining user
        emit('session-state', {
            'sessionId': session_id,
            'state': json.loads(session.state) if session.state else {},
            'players': [p.to_dict() for p in session.players]
        })

        # Notify others
        user = User.query.get(user_id)
        emit('player-online', {
            'user': user.to_dict() if user else {'id': user_id}
        }, room=session_id, include_self=False)

    @socketio.on('leave-session')
    def handle_leave_session(data):
        from flask import request as flask_request
        session_id = data.get('sessionId')
        if session_id:
            leave_room(session_id)

    # --- Real-time game events ---

    @socketio.on('object-move')
    def handle_object_move(data):
        """Broadcast object movement to all players in session."""
        from flask import request as flask_request
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
        """Broadcast object selection."""
        from flask import request as flask_request
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
        """Broadcast card flip."""
        from flask import request as flask_request
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
        """Broadcast object rotation."""
        from flask import request as flask_request
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
        """Broadcast object deletion."""
        from flask import request as flask_request
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
        """Broadcast new object addition."""
        from flask import request as flask_request
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
        """Broadcast stack formation."""
        from flask import request as flask_request
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
        """Broadcast stack removal."""
        from flask import request as flask_request
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
        """Broadcast drawing updates."""
        from flask import request as flask_request
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
        """Broadcast drawing clear."""
        from flask import request as flask_request
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
        """Broadcast zoom level (optional - clients may not need this)."""
        from flask import request as flask_request
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
        """Broadcast pan position (optional)."""
        from flask import request as flask_request
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
        """Save game state to database and broadcast."""
        from flask import request as flask_request
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
        """Broadcast chat messages."""
        from flask import request as flask_request
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


# Need User import
from models import User
