from flask_socketio import emit, join_room, leave_room, rooms
from flask_jwt_extended import decode_token
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

            notify_friends_status(user.id, True)
        else:
            emit('error', {'message': 'Authentication required'})
            return False

    @socketio.on('disconnect')
    def handle_disconnect(reason=None):
        user = get_current_user()
        if user:
            try:
                user.is_online = False
                user.last_seen = datetime.utcnow()
                db.session.commit()

                for room_id in rooms(flask_request.sid):
                    if room_id != flask_request.sid:
                        leave_room(room_id)

                notify_friends_status(user.id, False)
            except:
                pass

    @socketio.on('session:create')
    def handle_session_create(data):
        try:
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

            session_player = SessionPlayer(
                session_id=session.id,
                user_id=user.id,
                role='creator',
                is_active=True
            )
            db.session.add(session_player)
            db.session.commit()

            join_room(session.id)

            emit('session:created', {
                'session': session.to_dict()
            })
        except Exception as e:
            print(f"Session create error: {e}")
            emit('error', {'message': str(e)})

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
        try:
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

            receiver = User.query.get(receiver_id)
            if receiver and receiver.is_online:
                socketio.emit('invitation:received', {
                    'invitation': invitation.to_dict(),
                    'session': session.to_dict(),
                    'sender': user.to_dict()
                }, room=receiver_id)

            emit('invitation:sent', {
                'invitation': invitation.to_dict()
            })
        except Exception as e:
            print(f"Invite error: {e}")
            emit('error', {'message': str(e)})

    @socketio.on('invitation:accept')
    def handle_invitation_accept(data):
        try:
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
        except Exception as e:
            print(f"Accept invite error: {e}")
            emit('error', {'message': str(e)})

    @socketio.on('invitation:decline')
    def handle_invitation_decline(data):
        try:
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
        except Exception as e:
            print(f"Decline invite error: {e}")

    # === Real-time game synchronization ===

    @socketio.on('object:create')
    def handle_object_create(data):
        try:
            user = get_current_user()
            if not user:
                return

            session_id = data.get('sessionId')
            obj_data = data.get('object')

            if not session_id or not obj_data:
                return

            obj_data['ownerId'] = user.id
            obj_data['createdAt'] = datetime.utcnow().isoformat()

            session = GameSession.query.get(session_id)
            if session:
                state = json.loads(session.state) if session.state else {}
                if 'objects' not in state:
                    state['objects'] = []
                state['objects'].append(obj_data)
                session.state = json.dumps(state)
                session.updated_at = datetime.utcnow()
                db.session.commit()

            emit('object:created', {
                'object': obj_data,
                'sessionId': session_id
            }, room=session_id)
        except Exception as e:
            print(f"Object create error: {e}")

    @socketio.on('object:update')
    def handle_object_update(data):
        try:
            user = get_current_user()
            if not user:
                return

            session_id = data.get('sessionId')
            object_id = data.get('objectId')
            updates = data.get('updates', {})

            if not session_id or not object_id:
                return

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

            emit('object:updated', {
                'objectId': object_id,
                'updates': updates,
                'sessionId': session_id
            }, room=session_id)
        except Exception as e:
            print(f"Object update error: {e}")

    @socketio.on('object:delete')
    def handle_object_delete(data):
        try:
            user = get_current_user()
            if not user:
                return

            session_id = data.get('sessionId')
            object_id = data.get('objectId')

            if not session_id or not object_id:
                return

            session = GameSession.query.get(session_id)
            if session:
                state = json.loads(session.state) if session.state else {}
                if 'objects' in state:
                    state['objects'] = [obj for obj in state['objects'] if obj.get('id') != object_id]
                session.state = json.dumps(state)
                session.updated_at = datetime.utcnow()
                db.session.commit()

            emit('object:deleted', {
                'objectId': object_id,
                'sessionId': session_id
            }, room=session_id)
        except Exception as e:
            print(f"Object delete error: {e}")

    @socketio.on('object:sync')
    def handle_object_sync(data):
        """ОПТИМИЗИРОВАНО: Без записи в БД для производительности"""
        try:
            user = get_current_user()
            if not user:
                return

            session_id = data.get('sessionId')
            update_data = data.get('update', {})

            if not session_id or not update_data:
                return

            # Просто пересылаем всем в комнате БЕЗ сохранения в БД
            emit('object:sync', {
                'userId': user.id,
                'username': user.username,
                'update': update_data,
                'sessionId': session_id
            }, room=session_id, include_self=False)

        except Exception as e:
            print(f"❌ Object sync error: {e}")

    @socketio.on('drawing:create')
    def handle_drawing_create(data):
        try:
            user = get_current_user()
            if not user:
                return

            session_id = data.get('sessionId')
            drawing = data.get('drawing')

            if not session_id or not drawing:
                return

            drawing['userId'] = user.id
            drawing['createdAt'] = datetime.utcnow().isoformat()

            session = GameSession.query.get(session_id)
            if session:
                state = json.loads(session.state) if session.state else {}
                if 'drawings' not in state:
                    state['drawings'] = []
                state['drawings'].append(drawing)
                session.state = json.dumps(state)
                session.updated_at = datetime.utcnow()
                db.session.commit()

            emit('drawing:created', {
                'drawing': drawing,
                'sessionId': session_id
            }, room=session_id)
        except Exception as e:
            print(f"Drawing create error: {e}")

    @socketio.on('drawing:sync')
    def handle_drawing_sync(data):
        """Синхронизация рисования в реальном времени"""
        try:
            user = get_current_user()
            if not user:
                return

            session_id = data.get('sessionId')
            drawing_data = data.get('drawing', {})

            if not session_id or not drawing_data:
                return

            emit('drawing:sync', {
                'userId': user.id,
                'drawing': drawing_data,
                'sessionId': session_id
            }, room=session_id)

        except Exception as e:
            print(f"❌ Drawing sync error: {e}")

    @socketio.on('friend:request')
    def handle_friend_request(data):
        try:
            user = get_current_user()
            if not user:
                emit('error', {'message': 'Authentication required'})
                return

            receiver_id = data.get('receiverId')

            if receiver_id == user.id:
                emit('error', {'message': 'Cannot add yourself'})
                return

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

            receiver = User.query.get(receiver_id)
            if receiver and receiver.is_online:
                socketio.emit('friend:request_received', {
                    'friendship': friendship.to_dict(),
                    'requester': user.to_dict()
                }, room=receiver_id)

            emit('friend:request_sent', {
                'friendship': friendship.to_dict()
            })
        except Exception as e:
            print(f"Friend request error: {e}")
            emit('error', {'message': str(e)})

    @socketio.on('friend:accept')
    def handle_friend_accept(data):
        try:
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

            requester = User.query.get(friendship.requester_id)
            if requester and requester.is_online:
                socketio.emit('friend:accepted', {
                    'friendship': friendship.to_dict(),
                    'accepter': user.to_dict()
                }, room=requester.id)

            emit('friend:accepted', {
                'friendship': friendship.to_dict()
            })
        except Exception as e:
            print(f"Friend accept error: {e}")

    @socketio.on('friend:decline')
    def handle_friend_decline(data):
        try:
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
        except Exception as e:
            print(f"Friend decline error: {e}")

    @socketio.on('friend:remove')
    def handle_friend_remove(data):
        try:
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
        except Exception as e:
            print(f"Friend remove error: {e}")

    @socketio.on('friends:get_list')
    def handle_get_friends(data=None):
        try:
            user = get_current_user()
            if not user:
                emit('error', {'message': 'Authentication required'})
                return

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

            emit('friends:list', {'friends': friends})
        except Exception as e:
            print(f"Get friends error: {e}")
            emit('error', {'message': str(e)})

    @socketio.on('friends:get_requests')
    def handle_get_friend_requests(data=None):
        try:
            user = get_current_user()
            if not user:
                emit('error', {'message': 'Authentication required'})
                return

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
        except Exception as e:
            print(f"Get friend requests error: {e}")
            emit('error', {'message': str(e)})

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

    # === Deck Management ===

    @socketio.on('deck:create')
    def handle_deck_create(data):
        try:
            user = get_current_user()
            if not user: return
            session_id = data.get('sessionId')
            deck = data.get('deck')
            if not session_id or not deck: return

            deck['createdBy'] = user.id
            session = GameSession.query.get(session_id)
            if session:
                state = json.loads(session.state) if session.state else {}
                if 'decks' not in state: state['decks'] = []
                state['decks'].append(deck)
                session.state = json.dumps(state)
                db.session.commit()

            emit('deck:create', {
                'deck': deck, 'userId': user.id, 'sessionId': session_id
            }, room=session_id, include_self=False)
        except Exception as e:
            print(f"Deck create error: {e}")

    @socketio.on('deck:update')
    def handle_deck_update(data):
        try:
            user = get_current_user()
            if not user: return
            session_id = data.get('sessionId')
            deck = data.get('deck')
            if not session_id or not deck: return

            session = GameSession.query.get(session_id)
            if session:
                state = json.loads(session.state) if session.state else {}
                if 'decks' in state:
                    state['decks'] = [d if d.get('id') != deck['id'] else deck for d in state['decks']]
                session.state = json.dumps(state)
                db.session.commit()

            emit('deck:update', {
                'deck': deck, 'userId': user.id, 'sessionId': session_id
            }, room=session_id, include_self=False)
        except Exception as e:
            print(f"Deck update error: {e}")

    @socketio.on('deck:delete')
    def handle_deck_delete(data):
        try:
            user = get_current_user()
            if not user: return
            session_id = data.get('sessionId')
            deck_id = data.get('deckId')
            if not session_id or not deck_id: return

            session = GameSession.query.get(session_id)
            if session:
                state = json.loads(session.state) if session.state else {}
                if 'decks' in state:
                    state['decks'] = [d for d in state['decks'] if d.get('id') != deck_id]
                session.state = json.dumps(state)
                db.session.commit()

            emit('deck:delete', {
                'deckId': deck_id, 'userId': user.id, 'sessionId': session_id
            }, room=session_id, include_self=False)
        except Exception as e:
            print(f"Deck delete error: {e}")

    @socketio.on('deck:addCard')
    def handle_deck_add_card(data):
        try:
            user = get_current_user()
            if not user: return
            session_id = data.get('sessionId')
            deck_id = data.get('deckId')
            card = data.get('card')
            if not session_id or not deck_id or not card: return

            session = GameSession.query.get(session_id)
            if session:
                state = json.loads(session.state) if session.state else {}
                if 'objects' in state:
                    for obj in state['objects']:
                        if obj.get('id') == deck_id and obj.get('type') == 'deck':
                            if not obj.get('cards'): obj['cards'] = []
                            if not any(c.get('id') == card['id'] for c in obj['cards']):
                                obj['cards'].append(card)
                                obj['cardCount'] = len(obj['cards'])
                            break
                session.state = json.dumps(state)
                db.session.commit()

            emit('deck:addCard', {
                'deckId': deck_id, 'card': card, 'userId': user.id, 'sessionId': session_id
            }, room=session_id, include_self=False)
        except Exception as e:
            print(f"Deck add card error: {e}")

    @socketio.on('deck:shuffle')
    def handle_deck_shuffle(data):
        try:
            user = get_current_user()
            if not user: return
            session_id = data.get('sessionId')
            deck_id = data.get('deckId')
            if not session_id or not deck_id: return

            session = GameSession.query.get(session_id)
            if session:
                state = json.loads(session.state) if session.state else {}
                if 'objects' in state:
                    for obj in state['objects']:
                        if obj.get('id') == deck_id and obj.get('type') == 'deck' and obj.get('cards'):
                            import random
                            random.shuffle(obj['cards'])
                            break
                session.state = json.dumps(state)
                db.session.commit()

            emit('deck:shuffle', {
                'deckId': deck_id, 'userId': user.id, 'sessionId': session_id
            }, room=session_id, include_self=False)
        except Exception as e:
            print(f"Deck shuffle error: {e}")

    @socketio.on('deck:draw')
    def handle_deck_draw(data):
        try:
            user = get_current_user()
            if not user: return
            session_id = data.get('sessionId')
            deck_id = data.get('deckId')
            new_card = data.get('newCard')
            deck_state = data.get('deckState')
            if not session_id or not deck_id: return

            session = GameSession.query.get(session_id)
            if session:
                state = json.loads(session.state) if session.state else {}

                if 'objects' in state:
                    for obj in state['objects']:
                        if obj.get('id') == deck_id:
                            if deck_state:
                                obj['cards'] = deck_state.get('cards', [])
                                obj['cardCount'] = deck_state.get('cardCount', 0)
                            break

                if new_card:
                    if 'objects' not in state: state['objects'] = []
                    state['objects'].append(new_card)

                session.state = json.dumps(state)
                db.session.commit()

            emit('deck:draw', {
                'deckId': deck_id,
                'newCard': new_card,
                'deckState': deck_state,
                'userId': user.id,
                'sessionId': session_id
            }, room=session_id, include_self=False)
        except Exception as e:
            print(f"Deck draw error: {e}")

    # === Helper Functions ===

    def notify_friends_status(user_id, is_online):
        """Notify all friends about user's online status"""
        try:
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
        except:
            pass