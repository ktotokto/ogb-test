from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from models import db, User, Friendship

friends_bp = Blueprint('friends', __name__, url_prefix='/api/friends')

@friends_bp.route('', methods=['GET'])
@jwt_required()
def get_friends():
    user_id = get_jwt_identity()
    
    friendships = Friendship.query.filter(
        ((Friendship.requester_id == user_id) | (Friendship.accepter_id == user_id)) &
        (Friendship.status == 'accepted')
    ).all()
    
    friends = []
    for f in friendships:
        friend_id = f.accepter_id if f.requester_id == user_id else f.requester_id
        friend = User.query.get(friend_id)
        if friend:
            friends.append({
                'user': friend.to_dict(),
                'friendship': f.to_dict()
            })
    
    return jsonify(friends)

@friends_bp.route('/requests', methods=['GET'])
@jwt_required()
def get_friend_requests():
    user_id = get_jwt_identity()
    
    requests = Friendship.query.filter_by(
        accepter_id=user_id,
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
    
    return jsonify(friend_requests)

@friends_bp.route('/request', methods=['POST'])
@jwt_required()
def send_friend_request():
    user_id = get_jwt_identity()
    data = request.get_json()
    receiver_id = data.get('receiverId')
    
    if not receiver_id:
        return jsonify({'message': 'receiverId required'}), 400
    
    if receiver_id == user_id:
        return jsonify({'message': 'Cannot add yourself'}), 400
    
    existing = Friendship.query.filter(
        ((Friendship.requester_id == user_id) & (Friendship.accepter_id == receiver_id)) |
        ((Friendship.requester_id == receiver_id) & (Friendship.accepter_id == user_id))
    ).first()
    
    if existing:
        return jsonify({'message': 'Already friends or request pending'}), 409
    
    friendship = Friendship(
        requester_id=user_id,
        accepter_id=receiver_id,
        status='pending'
    )
    
    db.session.add(friendship)
    db.session.commit()
    
    return jsonify({
        'message': 'Friend request sent',
        'friendship': friendship.to_dict()
    }), 201

@friends_bp.route('/accept/<friendship_id>', methods=['POST'])
@jwt_required()
def accept_friend_request(friendship_id):
    user_id = get_jwt_identity()
    
    friendship = Friendship.query.get(friendship_id)
    
    if not friendship or friendship.accepter_id != user_id:
        return jsonify({'message': 'Invalid request'}), 404
    
    friendship.status = 'accepted'
    db.session.commit()
    
    return jsonify({
        'message': 'Friend request accepted',
        'friendship': friendship.to_dict()
    })

@friends_bp.route('/decline/<friendship_id>', methods=['POST'])
@jwt_required()
def decline_friend_request(friendship_id):
    user_id = get_jwt_identity()
    
    friendship = Friendship.query.get(friendship_id)
    
    if friendship and friendship.accepter_id == user_id:
        db.session.delete(friendship)
        db.session.commit()
        return jsonify({'message': 'Friend request declined'})
    
    return jsonify({'message': 'Invalid request'}), 404

@friends_bp.route('/<friend_id>', methods=['DELETE'])
@jwt_required()
def remove_friend(friend_id):
    user_id = get_jwt_identity()
    
    friendship = Friendship.query.filter(
        ((Friendship.requester_id == user_id) & (Friendship.accepter_id == friend_id)) |
        ((Friendship.requester_id == friend_id) & (Friendship.accepter_id == user_id))
    ).first()
    
    if friendship:
        db.session.delete(friendship)
        db.session.commit()
        return jsonify({'message': 'Friend removed'})
    
    return jsonify({'message': 'Friend not found'}), 404