import os


class Config:
    SECRET_KEY = os.environ.get("SECRET_KEY", "dev-secret-change-me-0123456789abcdef")
    JWT_SECRET = os.environ.get("JWT_SECRET", "dev-jwt-secret-change-me-0123456789abcdef")
    JWT_EXP_MINUTES = int(os.environ.get("JWT_EXP_MINUTES", "60"))
    SQLALCHEMY_DATABASE_URI = os.environ.get("DATABASE_URL", "sqlite:///app.db")
    SQLALCHEMY_TRACK_MODIFICATIONS = False
