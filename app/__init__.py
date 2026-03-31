import os
from flask import Flask
from app.extensions import db, migrate
from app.logging_config import setup_logging
from config import config_map


def create_app(config_name=None):
    app = Flask(__name__)

    if config_name is None:
        config_name = os.environ.get("FLASK_ENV", "development")

    app.config.from_object(config_map.get(config_name, config_map["development"]))

    db.init_app(app)
    migrate.init_app(app, db)

    setup_logging(app)

    app.logger.info("Aplikacja PZW uruchomiona w trybie: %s", config_name)

    return app
