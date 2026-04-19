import os
from flask import Flask
from flask_socketio import SocketIO
from flask_jwt_extended import JWTManager
from flask_cors import CORS
from config import Config
from models import db

socketio = SocketIO(cors_allowed_origins="*")
jwt = JWTManager()


def create_app(config_class=Config):
    app = Flask(__name__)
    app.config.from_object(config_class)

    # Initialize extensions
    db.init_app(app)
    jwt.init_app(app)
    CORS(app, supports_credentials=True)
    socketio.init_app(app, async_mode='eventlet', cors_allowed_origins="*")

    # Import and register blueprints
    from auth import auth_bp
    from game import game_bp

    app.register_blueprint(auth_bp)
    app.register_blueprint(game_bp)

    # Initialize SocketIO events
    from events import init_socketio
    init_socketio(socketio)

    # Create database tables
    with app.app_context():
        db.create_all()

    # Health check
    @app.route('/api/health')
    def health():
        return {'status': 'ok', 'message': 'OGB Game Server'}

    @app.route('/')
    def index():
        return {'message': 'OGB Game Server - WebSocket enabled'}

    return app


if __name__ == '__main__':
    app = create_app()
    port = int(os.environ.get('PORT', 5000))
    print(f"\n{'='*50}")
    print(f"  OGB Game Server")
    print(f"  Running on http://0.0.0.0:{port}")
    print(f"  WebSocket: ws://0.0.0.0:{port}")
    print(f"{'='*50}\n")
    socketio.run(app, host='0.0.0.0', port=port, debug=True)
