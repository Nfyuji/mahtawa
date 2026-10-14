import os
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent


class Config:
    SECRET_KEY = os.getenv("SECRET_KEY", "contentforge-dev-secret")
    SQLALCHEMY_DATABASE_URI = os.getenv(
        "DATABASE_URL",
        f"sqlite:///{BASE_DIR / 'instance' / 'contentforge.db'}",
    )
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    OPENAI_API_KEY = os.getenv("OPENAI_API_KEY", "")
    OPENAI_BASE_URL = os.getenv("OPENAI_BASE_URL", "https://api.openai.com/v1")
    OPENAI_MODEL = os.getenv("OPENAI_MODEL", "gpt-4o")
    YOUTUBE_API_KEY = os.getenv("YOUTUBE_API_KEY", "")
    FLASK_VERIFY_SSL = os.getenv("FLASK_VERIFY_SSL", "false").lower() == "true"
    DEBUG = os.getenv("FLASK_DEBUG", "false").lower() == "true"
