from models import db
from datetime import datetime
import uuid
import json

class GameSession(db.Model):
    __tablename__ = 'game_sessions'
    
    id = db.Column(db.String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    creator_id = db.Column(db.String(36), db.ForeignKey('users.id'), nullable=False)
    name = db.Column(db.String(100))
    is_private = db.Column(db.Boolean, default=False)
    state = db.Column(db.Text)  # JSON state of the game
    max_players = db.Column(db.Integer, default=8)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    players = db.relationship('SessionPlayer', backref='session', lazy='dynamic', cascade='all, delete-orphan')
    invitations = db.relationship('GameInvitation', backref='session', lazy='dynamic', cascade='all, delete-orphan')
    
    def to_dict(self):
        return {
            'id': self.id,
            'name': self.name,
            'creator_id': self.creator_id,
            'is_private': self.is_private,
            'state': json.loads(self.state) if self.state else {},
            'max_players': self.max_players,
            'players': [p.to_dict() for p in self.players.all()],
            'created_at': self.created_at.isoformat(),
            'updated_at': self.updated_at.isoformat()
        }
    
    def get_player_count(self):
        return self.players.filter_by(is_active=True).count()
    
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
    
    __table_args__ = (db.UniqueConstraint('session_id', 'user_id', name='_session_user_uc'),)
    
    def to_dict(self):
        user = self.user
        return {
            'id': self.id,
            'session_id': self.session_id,
            'user': user.to_dict() if user else None,
            'role': self.role,
            'is_active': self.is_active,
            'joined_at': self.joined_at.isoformat()
        }