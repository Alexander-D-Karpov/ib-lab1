from flask import Flask

from app.config import Config
from app.models import db
from app.routes import api
from app.seed import seed_data


def create_app(config_class=Config):
    app = Flask(__name__)
    app.config.from_object(config_class)

    db.init_app(app)
    app.register_blueprint(api)

    with app.app_context():
        db.create_all()
        seed_data()

    return app
