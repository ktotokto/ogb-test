from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from models import db, GameSession, User, SessionPlayer, CardDeck
import uuid
import json

game_bp = Blueprint('game', __name__, url_prefix='/api/game')


@game_bp.route('/sessions', methods=['POST'])
@jwt_required()
def create_session():
    data = request.get_json()
    if not data or not data.get('name'):
        return jsonify({'error': 'Session name is required'}), 400

    user_id = get_jwt_identity()
    session_id = str(uuid.uuid4())

    session = GameSession(
        id=session_id,
        name=data['name'].strip(),
        created_by=user_id,
        state=json.dumps({'objects': [], 'drawings': [], 'cardDeck': []})
    )

    # Add creator as admin
    association = SessionPlayer(
        session_id=session_id,
        user_id=user_id,
        role='admin'
    )

    db.session.add(session)
    db.session.add(association)
    db.session.commit()

    return jsonify({'session': session.to_dict()}), 201


@game_bp.route('/sessions', methods=['GET'])
@jwt_required()
def list_sessions():
    user_id = get_jwt_identity()

    # Sessions user is part of
    sessions = GameSession.query.join(SessionPlayer).filter(
        SessionPlayer.user_id == user_id
    ).all()

    # Public sessions (optional - for lobby)
    all_sessions = GameSession.query.order_by(GameSession.updated_at.desc()).limit(50).all()

    return jsonify({
        'mySessions': [s.to_dict() for s in sessions],
        'allSessions': [s.to_dict() for s in all_sessions]
    }), 200


@game_bp.route('/sessions/<session_id>', methods=['GET'])
@jwt_required()
def get_session(session_id):
    session = GameSession.query.get(session_id)
    if not session:
        return jsonify({'error': 'Session not found'}), 404

    return jsonify({'session': session.to_dict()}), 200


@game_bp.route('/sessions/<session_id>/join', methods=['POST'])
@jwt_required()
def join_session(session_id):
    user_id = get_jwt_identity()
    session = GameSession.query.get(session_id)
    if not session:
        return jsonify({'error': 'Session not found'}), 404

    # Check if already in session
    existing = SessionPlayer.query.filter_by(
        session_id=session_id, user_id=user_id
    ).first()
    if existing:
        return jsonify({'session': session.to_dict()}), 200

    association = SessionPlayer(
        session_id=session_id,
        user_id=user_id,
        role='player'
    )

    db.session.add(association)
    db.session.commit()

    return jsonify({'session': session.to_dict()}), 200


@game_bp.route('/sessions/<session_id>/state', methods=['PUT'])
@jwt_required()
def update_session_state(session_id):
    user_id = get_jwt_identity()
    session = GameSession.query.get(session_id)
    if not session:
        return jsonify({'error': 'Session not found'}), 404

    # Check if user is in session
    association = SessionPlayer.query.filter_by(
        session_id=session_id, user_id=user_id
    ).first()
    if not association:
        return jsonify({'error': 'Not a member of this session'}), 403

    data = request.get_json()
    if not data or 'state' not in data:
        return jsonify({'error': 'State is required'}), 400

    session.state = json.dumps(data['state'])
    db.session.commit()

    return jsonify({'session': session.to_dict()}), 200


@game_bp.route('/sessions/<session_id>/leave', methods=['POST'])
@jwt_required()
def leave_session(session_id):
    user_id = get_jwt_identity()

    association = SessionPlayer.query.filter_by(
        session_id=session_id, user_id=user_id
    ).first()
    if not association:
        return jsonify({'error': 'Not in this session'}), 404

    db.session.delete(association)
    db.session.commit()

    return jsonify({'message': 'Left session'}), 200


@game_bp.route('/sessions/<session_id>/players', methods=['GET'])
@jwt_required()
def get_session_players(session_id):
    session = GameSession.query.get(session_id)
    if not session:
        return jsonify({'error': 'Session not found'}), 404

    return jsonify({'players': [p.to_dict() for p in session.players]}), 200


# --- Card Decks ---

@game_bp.route('/sessions/<session_id>/decks', methods=['GET'])
@jwt_required()
def get_decks(session_id):
    decks = CardDeck.query.filter_by(session_id=session_id).all()
    return jsonify({'decks': [d.to_dict() for d in decks]}), 200


@game_bp.route('/sessions/<session_id>/decks', methods=['POST'])
@jwt_required()
def create_deck(session_id):
    data = request.get_json()
    if not data or not data.get('name') or not data.get('cardData'):
        return jsonify({'error': 'Name and cardData are required'}), 400

    deck_id = str(uuid.uuid4())
    deck = CardDeck(
        id=deck_id,
        session_id=session_id,
        name=data['name'],
        card_data=json.dumps(data['cardData'])
    )

    db.session.add(deck)
    db.session.commit()

    return jsonify({'deck': deck.to_dict()}), 201


@game_bp.route('/decks/<deck_id>', methods=['PUT'])
@jwt_required()
def update_deck(deck_id):
    deck = CardDeck.query.get(deck_id)
    if not deck:
        return jsonify({'error': 'Deck not found'}), 404

    data = request.get_json()
    if 'name' in data:
        deck.name = data['name']
    if 'cardData' in data:
        deck.card_data = json.dumps(data['cardData'])

    db.session.commit()

    return jsonify({'deck': deck.to_dict()}), 200
