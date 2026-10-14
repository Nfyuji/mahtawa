import os
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent


def _database_url() -> str:
    url = os.getenv("DATABASE_URL", "").strip()
    if not url:
        return f"sqlite:///{BASE_DIR / 'instance' / 'contentforge.db'}"
    # Render Postgres URLs sometimes use postgres:// which SQLAlchemy rejects
    if url.startswith("postgres://"):
        url = url.replace("postgres://", "postgresql://", 1)
    return url


class Config:
    SECRET_KEY = os.getenv("SECRET_KEY", "contentforge-dev-secret")
    SQLALCHEMY_DATABASE_URI = _database_url()
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    OPENAI_API_KEY = os.getenv("OPENAI_API_KEY", "")
    OPENAI_BASE_URL = os.getenv("OPENAI_BASE_URL", "https://api.openai.com/v1")
    OPENAI_MODEL = os.getenv("OPENAI_MODEL", "gpt-4o-mini")
    YOUTUBE_API_KEY = os.getenv("YOUTUBE_API_KEY", "")
    FLASK_VERIFY_SSL = os.getenv("FLASK_VERIFY_SSL", "false").lower() == "true"
    DEBUG = os.getenv("FLASK_DEBUG", "false").lower() == "true"
    # Needed behind Render's HTTPS proxy so secure cookies / URLs work
    PREFERRED_URL_SCHEME = "https"
    SESSION_COOKIE_SECURE = os.getenv("SESSION_COOKIE_SECURE", "false").lower() == "true"
