from flask_sqlalchemy import SQLAlchemy
from datetime import datetime
import uuid
import json

db = SQLAlchemy()


class User(db.Model):
    __tablename__ = 'users'

    id = db.Column(db.String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    username = db.Column(db.String(50), unique=True, nullable=False)
    email = db.Column(db.String(100), unique=True, nullable=False)
    password_hash = db.Column(db.String(255), nullable=False)
    avatar_url = db.Column(db.String(500))
    banner_url = db.Column(db.String(500))
    bio = db.Column(db.Text)
    is_online = db.Column(db.Boolean, default=False)
    last_seen = db.Column(db.DateTime, default=datetime.utcnow)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    def to_dict(self):
        return {
            'id': self.id,
            'username': self.username,
            'email': self.email,
            'avatar_url': self.avatar_url,
            'banner_url': self.banner_url,
            'bio': self.bio,
            'is_online': self.is_online,
            'last_seen': self.last_seen.isoformat() if self.last_seen else None
        }


class GameSession(db.Model):
    __tablename__ = 'game_sessions'

    id = db.Column(db.String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    creator_id = db.Column(db.String(36), db.ForeignKey('users.id'), nullable=False)
    name = db.Column(db.String(100))
    is_private = db.Column(db.Boolean, default=False)
    state = db.Column(db.Text)
    max_players = db.Column(db.Integer, default=8)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    players = db.relationship(
        'SessionPlayer',
        back_populates='session',
        lazy=True,
        cascade='all, delete-orphan'
    )

    def to_dict(self):
        return {
            'id': self.id,
            'name': self.name,
            'creator_id': self.creator_id,
            'is_private': self.is_private,
            'state': json.loads(self.state) if self.state else {},
            'max_players': self.max_players,
            'players': [p.to_dict() for p in self.players],
            'created_at': self.created_at.isoformat(),
            'updated_at': self.updated_at.isoformat()
        }

    def get_player_count(self):
        return len([p for p in self.players if p.is_active])

    def is_full(self):
        return self.get_player_count() >= self.max_players


class SessionPlayer(db.Model):
    __tablename__ = 'session_players'

    id = db.Column(db.String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    session_id = db.Column(db.String(36), db.ForeignKey('game_sessions.id'), nullable=False)
    user_id = db.Column(db.String(36), db.ForeignKey('users.id'), nullable=False)
    role = db.Column(db.String(20), default='player')
    is_active = db.Column(db.Boolean, default=True)
    joined_at = db.Column(db.DateTime, default=datetime.utcnow)

    session = db.relationship('GameSession', back_populates='players')
    user = db.relationship('User', backref='session_participations')

    __table_args__ = (db.UniqueConstraint('session_id', 'user_id', name='_session_user_uc'),)

    def to_dict(self):
        return {
            'id': self.id,
            'session_id': self.session_id,
            'user_id': self.user_id,
            'user': self.user.to_dict() if self.user else None,
            'role': self.role,
            'is_active': self.is_active,
            'joined_at': self.joined_at.isoformat()
        }


class Friendship(db.Model):
    __tablename__ = 'friendships'

    id = db.Column(db.String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    requester_id = db.Column(db.String(36), db.ForeignKey('users.id'), nullable=False)
    accepter_id = db.Column(db.String(36), db.ForeignKey('users.id'), nullable=False)
    status = db.Column(db.String(20), default='pending')
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    def to_dict(self):
        return {
            'id': self.id,
            'requester_id': self.requester_id,
            'accepter_id': self.accepter_id,
            'status': self.status,
            'created_at': self.created_at.isoformat()
        }


class GameInvitation(db.Model):
    __tablename__ = 'game_invitations'

    id = db.Column(db.String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    session_id = db.Column(db.String(36), db.ForeignKey('game_sessions.id'), nullable=False)
    sender_id = db.Column(db.String(36), db.ForeignKey('users.id'), nullable=False)
    receiver_id = db.Column(db.String(36), db.ForeignKey('users.id'), nullable=False)
    status = db.Column(db.String(20), default='pending')
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    def to_dict(self):
        return {
            'id': self.id,
            'session_id': self.session_id,
            'sender_id': self.sender_id,
            'receiver_id': self.receiver_id,
            'status': self.status,
            'created_at': self.created_at.isoformat()
        }


class CardDeck(db.Model):
    __tablename__ = 'card_decks'

    id = db.Column(db.String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    name = db.Column(db.String(100), nullable=False)
    description = db.Column(db.Text)
    owner_id = db.Column(db.String(36), db.ForeignKey('users.id'))
    cards = db.Column(db.Text)
    is_public = db.Column(db.Boolean, default=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    def to_dict(self):
        return {
            'id': self.id,
            'name': self.name,
            'description': self.description,
            'owner_id': self.owner_id,
            'cards': json.loads(self.cards) if self.cards else [],
            'is_public': self.is_public,
            'created_at': self.created_at.isoformat()
        }