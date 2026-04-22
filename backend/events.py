from flask_socketio import emit, join_room, leave_room, rooms
from flask_jwt_extended import decode_token, verify_jwt_in_request
from flask import request as flask_request
from models import db, User, GameSession, SessionPlayer, Friendship, GameInvitation
from datetime import datetime
import json

socketio = None


def init_socketio(sio):
    global socketio
    socketio = sio
    register_events()


def get_current_user():
    """Get current user from JWT token"""
    try:
        token = flask_request.args.get('token')
        if not token:
            # Try from Authorization header
            auth_header = flask_request.headers.get('Authorization')
            if auth_header and auth_header.startswith('Bearer '):
                token = auth_header[7:]

        if not token:
            return None

        decoded = decode_token(token)
        user_id = decoded.get('sub')
        return User.query.get(user_id) if user_id else None
    except:
        return None


def register_events():
    @socketio.on('connect')
    def handle_connect():
        user = get_current_user()
        if user:
            user.is_online = True
            user.last_seen = datetime.utcnow()
            db.session.commit()

            emit('connected', {
                'userId': user.id,
                'username': user.username
            })

            # Notify friends that user is online
            notify_friends_status(user.id, True)
        else:
            emit('error', {'message': 'Authentication required'})
            return False

    @socketio.on('disconnect')
    def handle_disconnect(reason=None):
        user = get_current_user()
        if user:
            user.is_online = False
            user.last_seen = datetime.utcnow()
            db.session.commit()

            # Leave all rooms
            for room_id in rooms(flask_request.sid):
                if room_id != flask_request.sid:
                    leave_room(room_id)

            # Notify friends that user is offline
            notify_friends_status(user.id, False)

    @socketio.on('session:create')
    def handle_session_create(data):
        user = get_current_user()
        if not user:
            emit('error', {'message': 'Authentication required'})
            return

        session_name = data.get('name', f"{user.username}'s Game")
        is_private = data.get('isPrivate', False)
        max_players = data.get('maxPlayers', 8)

        session = GameSession(
            creator_id=user.id,
            name=session_name,
            is_private=is_private,
            max_players=max_players,
            state=json.dumps({
                'objects': [],
                'drawings': [],
                'settings': {
                    'gridEnabled': True,
                    'gridSize': 50
                }
            })
        )

        db.session.add(session)
        db.session.commit()

        # Add creator as player
        session_player = SessionPlayer(
            session_id=session.id,
            user_id=user.id,
            role='creator',
            is_active=True
        )
        db.session.add(session_player)
        db.session.commit()

        # Join the room
        join_room(session.id)

        emit('session:created', {
            'session': session.to_dict()
        })

    @socketio.on('session:join')
    def handle_session_join(data):
        try:
            user = get_current_user()
            if not user:
                emit('error', {'message': 'Authentication required'})
                return

            session_id = data.get('sessionId')
            if not session_id:
                emit('error', {'message': 'sessionId required'})
                return

            session = GameSession.query.get(session_id)
            if not session:
                emit('error', {'message': 'Session not found'})
                return

            if session.is_full():
                emit('error', {'message': 'Session is full'})
                return

            existing_player = SessionPlayer.query.filter_by(
                session_id=session_id,
                user_id=user.id
            ).first()

            if not existing_player:
                session_player = SessionPlayer(
                    session_id=session_id,
                    user_id=user.id,
                    role='player',
                    is_active=True
                )
                db.session.add(session_player)
                db.session.commit()
                print(f"Player {user.username} added to session {session_id}")
            else:
                existing_player.is_active = True
                db.session.commit()
                print(f"Player {user.username} reactivated in session {session_id}")

            join_room(session_id)
            print(f"User {user.id} joined room {session_id}")

            session_data = session.to_dict()
            emit('session:joined', {
                'session': session_data,
                'players': session_data.get('players', []),
                'currentUserId': user.id
            })

            emit('player:joined', {
                'user': user.to_dict(),
                'player': {
                    'user_id': user.id,
                    'username': user.username,
                    'role': existing_player.role if existing_player else 'player',
                    'joined_at': datetime.utcnow().isoformat()
                },
                'sessionId': session_id
            }, room=session_id, include_self=False)

            print(f"Broadcasted player:joined to {session_id}")

        except Exception as e:
            print(f"Session join error: {e}")
            import traceback
            traceback.print_exc()
            emit('error', {'message': str(e)})

    @socketio.on('session:leave')
    def handle_session_leave(data):
        try:
            user = get_current_user()
            if not user:
                return

            session_id = data.get('sessionId')
            if not session_id:
                return

            player = SessionPlayer.query.filter_by(
                session_id=session_id,
                user_id=user.id
            ).first()

            if player:
                player.is_active = False
                db.session.commit()

            leave_room(session_id)

            emit('player:left', {
                'userId': user.id,
                'username': user.username,
                'sessionId': session_id
            }, room=session_id, include_self=False)

            print(f"Player {user.username} left session {session_id}")

        except Exception as e:
            print(f"Session leave error: {e}")

    @socketio.on('session:invite')
    def handle_session_invite(data):
        user = get_current_user()
        if not user:
            emit('error', {'message': 'Authentication required'})
            return

        session_id = data.get('sessionId')
        receiver_id = data.get('receiverId')

        session = GameSession.query.get(session_id)
        if not session:
            emit('error', {'message': 'Session not found'})
            return

        if session.creator_id != user.id:
            emit('error', {'message': 'Only creator can invite'})
            return

        # Check if invitation already exists
        existing = GameInvitation.query.filter_by(
            session_id=session_id,
            sender_id=user.id,
            receiver_id=receiver_id,
            status='pending'
        ).first()

        if existing:
            emit('error', {'message': 'Invitation already sent'})
            return

        invitation = GameInvitation(
            session_id=session_id,
            sender_id=user.id,
            receiver_id=receiver_id,
            status='pending'
        )
        db.session.add(invitation)
        db.session.commit()

        # Notify receiver
        receiver = User.query.get(receiver_id)
        if receiver and receiver.is_online:
            socketio.emit('invitation:received', {
                'invitation': invitation.to_dict(),
                'session': session.to_dict(),
                'sender': user.to_dict()
            }, room=receiver_id)  # Send to user's personal room

        emit('invitation:sent', {
            'invitation': invitation.to_dict()
        })

    @socketio.on('invitation:accept')
    def handle_invitation_accept(data):
        user = get_current_user()
        if not user:
            emit('error', {'message': 'Authentication required'})
            return

        invitation_id = data.get('invitationId')
        invitation = GameInvitation.query.get(invitation_id)

        if not invitation:
            emit('error', {'message': 'Invitation not found'})
            return

        if invitation.receiver_id != user.id:
            emit('error', {'message': 'Not your invitation'})
            return

        invitation.status = 'accepted'
        db.session.commit()

        # Auto-join session
        session = GameSession.query.get(invitation.session_id)
        if session and not session.is_full():
            session_player = SessionPlayer(
                session_id=session.id,
                user_id=user.id,
                role='player',
                is_active=True
            )
            db.session.add(session_player)
            db.session.commit()

            join_room(session.id)

            emit('session:joined', {
                'session': session.to_dict()
            })

            emit('player:joined', {
                'user': user.to_dict(),
                'sessionId': session.id
            }, room=session.id, include_self=False)

        emit('invitation:accepted', {
            'invitationId': invitation_id
        })

    @socketio.on('invitation:decline')
    def handle_invitation_decline(data):
        user = get_current_user()
        if not user:
            return

        invitation_id = data.get('invitationId')
        invitation = GameInvitation.query.get(invitation_id)

        if invitation and invitation.receiver_id == user.id:
            invitation.status = 'declined'
            db.session.commit()

            emit('invitation:declined', {
                'invitationId': invitation_id
            })

    # --- Real-time game synchronization ---

    @socketio.on('object:create')
    def handle_object_create(data):
        user = get_current_user()
        if not user:
            return

        session_id = data.get('sessionId')
        obj_data = data.get('object')

        if not session_id or not obj_data:
            return

        # Add owner
        obj_data['ownerId'] = user.id
        obj_data['createdAt'] = datetime.utcnow().isoformat()

        # Save to session state
        session = GameSession.query.get(session_id)
        if session:
            state = json.loads(session.state) if session.state else {}
            if 'objects' not in state:
                state['objects'] = []
            state['objects'].append(obj_data)
            session.state = json.dumps(state)
            session.updated_at = datetime.utcnow()
            db.session.commit()

        # Broadcast to all players
        emit('object:created', {
            'object': obj_data,
            'sessionId': session_id
        }, room=session_id)

    @socketio.on('object:update')
    def handle_object_update(data):
        user = get_current_user()
        if not user:
            return

        session_id = data.get('sessionId')
        object_id = data.get('objectId')
        updates = data.get('updates', {})

        if not session_id or not object_id:
            return

        # Update in session state
        session = GameSession.query.get(session_id)
        if session:
            state = json.loads(session.state) if session.state else {}
            if 'objects' in state:
                for obj in state['objects']:
                    if obj.get('id') == object_id:
                        obj.update(updates)
                        obj['updatedAt'] = datetime.utcnow().isoformat()
                        break
            session.state = json.dumps(state)
            session.updated_at = datetime.utcnow()
            db.session.commit()

        # Broadcast
        emit('object:updated', {
            'objectId': object_id,
            'updates': updates,
            'sessionId': session_id
        }, room=session_id)

    @socketio.on('object:delete')
    def handle_object_delete(data):
        user = get_current_user()
        if not user:
            return

        session_id = data.get('sessionId')
        object_id = data.get('objectId')

        if not session_id or not object_id:
            return

        # Remove from session state
        session = GameSession.query.get(session_id)
        if session:
            state = json.loads(session.state) if session.state else {}
            if 'objects' in state:
                state['objects'] = [obj for obj in state['objects'] if obj.get('id') != object_id]
            session.state = json.dumps(state)
            session.updated_at = datetime.utcnow()
            db.session.commit()

        # Broadcast
        emit('object:deleted', {
            'objectId': object_id,
            'sessionId': session_id
        }, room=session_id)

    @socketio.on('drawing:create')
    def handle_drawing_create(data):
        user = get_current_user()
        if not user:
            return

        session_id = data.get('sessionId')
        drawing = data.get('drawing')

        if not session_id or not drawing:
            return

        drawing['userId'] = user.id
        drawing['createdAt'] = datetime.utcnow().isoformat()

        # Save to session state
        session = GameSession.query.get(session_id)
        if session:
            state = json.loads(session.state) if session.state else {}
            if 'drawings' not in state:
                state['drawings'] = []
            state['drawings'].append(drawing)
            session.state = json.dumps(state)
            session.updated_at = datetime.utcnow()
            db.session.commit()

        # Broadcast
        emit('drawing:created', {
            'drawing': drawing,
            'sessionId': session_id
        }, room=session_id)

    @socketio.on('friend:request')
    def handle_friend_request(data):
        user = get_current_user()
        if not user:
            emit('error', {'message': 'Authentication required'})
            return

        receiver_id = data.get('receiverId')

        if receiver_id == user.id:
            emit('error', {'message': 'Cannot add yourself'})
            return

        # Check if already friends
        existing = Friendship.query.filter(
            ((Friendship.requester_id == user.id) & (Friendship.accepter_id == receiver_id)) |
            ((Friendship.requester_id == receiver_id) & (Friendship.accepter_id == user.id))
        ).first()

        if existing:
            emit('error', {'message': 'Already friends or request pending'})
            return

        friendship = Friendship(
            requester_id=user.id,
            accepter_id=receiver_id,
            status='pending'
        )
        db.session.add(friendship)
        db.session.commit()

        # Notify receiver
        receiver = User.query.get(receiver_id)
        if receiver and receiver.is_online:
            socketio.emit('friend:request_received', {
                'friendship': friendship.to_dict(),
                'requester': user.to_dict()
            }, room=receiver_id)

        emit('friend:request_sent', {
            'friendship': friendship.to_dict()
        })

    @socketio.on('friend:accept')
    def handle_friend_accept(data):
        user = get_current_user()
        if not user:
            return

        friendship_id = data.get('friendshipId')
        friendship = Friendship.query.get(friendship_id)

        if not friendship or friendship.accepter_id != user.id:
            emit('error', {'message': 'Invalid request'})
            return

        friendship.status = 'accepted'
        db.session.commit()

        # Notify both users
        requester = User.query.get(friendship.requester_id)
        if requester and requester.is_online:
            socketio.emit('friend:accepted', {
                'friendship': friendship.to_dict(),
                'accepter': user.to_dict()
            }, room=requester.id)

        emit('friend:accepted', {
            'friendship': friendship.to_dict()
        })

    @socketio.on('friend:decline')
    def handle_friend_decline(data):
        user = get_current_user()
        if not user:
            return

        friendship_id = data.get('friendshipId')
        friendship = Friendship.query.get(friendship_id)

        if friendship and friendship.accepter_id == user.id:
            db.session.delete(friendship)
            db.session.commit()

            emit('friend:declined', {
                'friendshipId': friendship_id
            })

    @socketio.on('friend:remove')
    def handle_friend_remove(data):
        user = get_current_user()
        if not user:
            return

        friend_id = data.get('friendId')

        friendship = Friendship.query.filter(
            ((Friendship.requester_id == user.id) & (Friendship.accepter_id == friend_id)) |
            ((Friendship.requester_id == friend_id) & (Friendship.accepter_id == user.id))
        ).first()

        if friendship:
            db.session.delete(friendship)
            db.session.commit()

            emit('friend:removed', {
                'friendId': friend_id
            })

    @socketio.on('friends:get_list')
    def handle_get_friends(data):
        user = get_current_user()
        if not user:
            emit('error', {'message': 'Authentication required'})
            return

        # Get accepted friendships
        friendships = Friendship.query.filter(
            ((Friendship.requester_id == user.id) | (Friendship.accepter_id == user.id)) &
            (Friendship.status == 'accepted')
        ).all()

        friends = []
        for f in friendships:
            friend_id = f.accepter_id if f.requester_id == user.id else f.requester_id
            friend = User.query.get(friend_id)
            if friend:
                friends.append({
                    'user': friend.to_dict(),
                    'friendship': f.to_dict()
                })

        emit('friends:list', {
            'friends': friends
        })

    @socketio.on('friends:get_requests')
    def handle_get_friend_requests(data):
        user = get_current_user()
        if not user:
            emit('error', {'message': 'Authentication required'})
            return

        # Get pending requests where user is accepter
        requests = Friendship.query.filter_by(
            accepter_id=user.id,
            status='pending'
        ).all()

        friend_requests = []
        for req in requests:
            requester = User.query.get(req.requester_id)
            if requester:
                friend_requests.append({
                    'friendship': req.to_dict(),
                    'requester': requester.to_dict()
                })

        emit('friends:requests', {
            'requests': friend_requests
        })


# Helper function
    def notify_friends_status(user_id, is_online):
        """Notify all friends about user's online status"""
        user = User.query.get(user_id)
        if not user:
            return

        friendships = Friendship.query.filter(
            ((Friendship.requester_id == user_id) | (Friendship.accepter_id == user_id)) &
            (Friendship.status == 'accepted')
        ).all()

        for f in friendships:
            friend_id = f.accepter_id if f.requester_id == user_id else f.requester_id
            friend = User.query.get(friend_id)

            if friend and friend.is_online:
                socketio.emit('friend:status_changed', {
                    'userId': user_id,
                    'username': user.username,
                    'isOnline': is_online
                }, room=friend_id)

    @socketio.on('cursor:move')
    def handle_cursor_move(data):
        try:
            user = get_current_user()
            if not user:
                return

            session_id = data.get('sessionId')
            cursor_data = data.get('cursor', {})

            if not session_id or not cursor_data:
                return

            emit('cursor:move', {
                'userId': user.id,
                'username': user.username,
                'cursor': cursor_data,
                'sessionId': session_id
            }, room=session_id, include_self=False)

        except Exception as e:
            print(f"❌ Cursor move error: {e}")
            import traceback
            traceback.print_exc()

    @socketio.on('cursor:leave')
    def handle_cursor_leave(data):
        try:
            user = get_current_user()
            if not user:
                return

            session_id = data.get('sessionId')

            if session_id:
                emit('cursor:leave', {
                    'userId': user.id,
                    'sessionId': session_id
                }, room=session_id, include_self=False)
        except Exception as e:
            print(f"❌ Cursor leave error: {e}")

    @socketio.on('object:sync')
    def handle_object_sync(data):
        try:
            user = get_current_user()
            if not user:
                return

            session_id = data.get('sessionId')
            update_data = data.get('update', {})

            if not session_id or not update_data:
                return

            session = GameSession.query.get(session_id)
            if session and session.state:
                state = json.loads(session.state)

                if 'objects' in state and update_data.get('objectId'):
                    for obj in state['objects']:
                        if obj.get('id') == update_data['objectId']:
                            changes = update_data.get('changes', {})

                            if 'position' in changes:
                                obj['position'] = changes['position']

                            if 'cardData' in changes:
                                obj['cardData'] = changes['cardData']

                            if 'label' in changes:
                                obj['label'] = changes['label']

                            if 'rotation' in changes:
                                obj['rotation'] = changes['rotation']

                            if 'faceUp' in changes:
                                obj['faceUp'] = changes['faceUp']

                            if 'stackId' in changes:
                                obj['stackId'] = changes['stackId']
                            if 'stackIndex' in changes:
                                obj['stackIndex'] = changes['stackIndex']

                            obj['updatedAt'] = datetime.utcnow().isoformat()
                            break

                session.state = json.dumps(state)
                session.updated_at = datetime.utcnow()
                db.session.commit()

            emit('object:sync', {
                'userId': user.id,
                'username': user.username,
                'update': update_data,
                'sessionId': session_id
            }, room=session_id, include_self=False)

        except Exception as e:
            print(f"❌ Object sync error: {e}")
            import traceback
            traceback.print_exc()

    # === Drawing Sync ===

    @socketio.on('drawing:sync')
    def handle_drawing_sync(data):
        """Синхронизация рисования в реальном времени"""
        try:
            user_id = get_current_user()
            session_id = data.get('sessionId')
            drawing_data = data.get('drawing', {})

            if not session_id or not drawing_data:
                return

            emit('drawing:sync', {
                'userId': user_id,
                'drawing': drawing_data,
                'sessionId': session_id
            }, room=session_id)

        except Exception as e:
            print(f"❌ Drawing sync error: {e}")
