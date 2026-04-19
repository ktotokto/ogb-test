from flask_sqlalchemy import SQLAlchemy
from datetime import datetime
import json

db = SQLAlchemy()


class User(db.Model):
    __tablename__ = 'users'

    id = db.Column(db.String(36), primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False, index=True)
    email = db.Column(db.String(120), unique=True, nullable=False, index=True)
    password_hash = db.Column(db.String(256), nullable=False)
    avatar_url = db.Column(db.String(500), nullable=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    # Relationships
    sessions = db.relationship('GameSession', secondary='session_players', back_populates='players')

    def to_dict(self):
        return {
            'id': self.id,
            'username': self.username,
            'email': self.email,
            'avatarUrl': self.avatar_url,
            'createdAt': self.created_at.isoformat()
        }


class GameSession(db.Model):
    __tablename__ = 'game_sessions'

    id = db.Column(db.String(36), primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    created_by = db.Column(db.String(36), db.ForeignKey('users.id'), nullable=False)
    state = db.Column(db.Text, default='{}')  # JSON state of the board
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationships
    creator = db.relationship('User', backref='created_sessions')
    players = db.relationship('User', secondary='session_players', back_populates='sessions')

    def to_dict(self):
        return {
            'id': self.id,
            'name': self.name,
            'createdBy': self.created_by,
            'state': json.loads(self.state) if self.state else {},
            'players': [p.to_dict() for p in self.players],
            'createdAt': self.created_at.isoformat(),
            'updatedAt': self.updated_at.isoformat()
        }


class SessionPlayer(db.Model):
    """Association table for session players with roles."""
    __tablename__ = 'session_players'

    session_id = db.Column(db.String(36), db.ForeignKey('game_sessions.id'), primary_key=True)
    user_id = db.Column(db.String(36), db.ForeignKey('users.id'), primary_key=True)
    role = db.Column(db.String(20), default='player')  # admin, player
    joined_at = db.Column(db.DateTime, default=datetime.utcnow)


class CardDeck(db.Model):
    """Shared card decks for a session."""
    __tablename__ = 'card_decks'

    id = db.Column(db.String(36), primary_key=True)
    session_id = db.Column(db.String(36), db.ForeignKey('game_sessions.id'), nullable=False, index=True)
    name = db.Column(db.String(100), nullable=False)
    card_data = db.Column(db.Text, nullable=False)  # JSON
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    def to_dict(self):
        return {
            'id': self.id,
            'sessionId': self.session_id,
            'name': self.name,
            'cardData': json.loads(self.card_data) if self.card_data else [],
            'createdAt': self.created_at.isoformat()
        }
