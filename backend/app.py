import os
import logging
from flask import Flask
from flask_socketio import SocketIO
from flask_jwt_extended import JWTManager
from flask_cors import CORS
from config import Config
from models import db

logging.basicConfig(
    level=logging.DEBUG,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

socketio = SocketIO(
    cors_allowed_origins="*",
    async_mode='threading',
    max_http_buffer_size=1e8,
    ping_timeout=60,
    ping_interval=25,
    logger=False,
    engineio_logger=False
)
jwt = JWTManager()


def create_app(config_class=Config):
    app = Flask(__name__)
    app.config.from_object(config_class)

    db.init_app(app)
    jwt.init_app(app)
    CORS(app, supports_credentials=True, resources={
        r"/api/*": {"origins": "*"},
        r"/socket.io/*": {"origins": "*"}
    })
    socketio.init_app(app, async_mode='eventlet', cors_allowed_origins="*")

    from auth import auth_bp
    from game import game_bp
    from routes.friends import friends_bp
    from routes.users import users_bp

    app.register_blueprint(auth_bp)
    app.register_blueprint(game_bp)
    app.register_blueprint(friends_bp)
    app.register_blueprint(users_bp)

    from events import init_socketio
    init_socketio(socketio)

    with app.app_context():
        try:
            db.create_all()
            logger.info("Database tables created")
        except Exception as e:
            logger.error(f"Failed to create tables: {e}")

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

    print(f"\n{'=' * 50}")
    print(f"  OGB Game Server")
    print(f"  Running on http://0.0.0.0:{port}")
    print(f"  WebSocket: ws://0.0.0.0:{port}")
    print(f"{'=' * 50}\n")

    socketio.run(app, host='0.0.0.0', port=port, debug=True, allow_unsafe_werkzeug=True)