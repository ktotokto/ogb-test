import os
from datetime import timedelta
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent


class Config:
    SECRET_KEY = os.environ.get('SECRET_KEY', '5pS')

    JWT_SECRET_KEY = os.environ.get('JWT_SECRET_KEY', SECRET_KEY)
    JWT_ACCESS_TOKEN_EXPIRES = timedelta(hours=24)
    JWT_TOKEN_LOCATION = ['headers', 'query_string']
    JWT_HEADER_NAME = 'Authorization'
    JWT_HEADER_TYPE = 'Bearer'

    INSTANCE_DIR = BASE_DIR / 'instance'
    INSTANCE_DIR.mkdir(exist_ok=True)

    SQLALCHEMY_DATABASE_URI = f'sqlite:///{INSTANCE_DIR / "ogb.db"}'
    SQLALCHEMY_TRACK_MODIFICATIONS = False

    SOCKETIO_CORS = {
        'origins': ['http://localhost:5173', 'http://127.0.0.1:5173'],
        'methods': ['GET', 'POST'],
        'credentials': True
    }