import os
from flask import Flask
from app.extensions import db, migrate, login_manager
from app.logging_config import setup_logging
from config import config_map


def create_app(config_name=None):
    app = Flask(__name__)

    if config_name is None:
        config_name = os.environ.get("FLASK_ENV", "development")

    app.config.from_object(config_map.get(config_name, config_map["development"]))

    db.init_app(app)
    migrate.init_app(app, db)

    login_manager.init_app(app)
    login_manager.login_view = "auth.login"  # type: ignore[assignment]

    @login_manager.user_loader
    def load_user(user_id):
        from app.models import Uzytkownik

        return db.session.get(Uzytkownik, int(user_id))

    setup_logging(app)

    @app.template_filter("display_name")
    def display_name_filter(zawodnik):
        from flask_login import current_user
        return zawodnik.display_name(current_user.is_authenticated)

    from app.blueprints.auth import bp as auth_bp

    app.register_blueprint(auth_bp, url_prefix="/auth")

    from app.blueprints.main import bp as main_bp

    app.register_blueprint(main_bp)

    from app.blueprints.zawody import bp as zawody_bp

    app.register_blueprint(zawody_bp, url_prefix="/zawody")

    from app.blueprints.slowniki import bp as slowniki_bp

    app.register_blueprint(slowniki_bp, url_prefix="/slowniki")

    from app.blueprints.sedziowie import bp as sedziowie_bp

    app.register_blueprint(sedziowie_bp, url_prefix="/sedziowie")

    from app.blueprints.uzytkownicy import bp as uzytkownicy_bp

    app.register_blueprint(uzytkownicy_bp, url_prefix="/uzytkownicy")

    from app.blueprints.zawodnicy import bp as zawodnicy_bp

    app.register_blueprint(zawodnicy_bp, url_prefix="/zawodnicy")

    from app.blueprints.wyniki import bp as wyniki_bp

    app.register_blueprint(wyniki_bp, url_prefix="/wyniki")

    from app.blueprints.cms import bp as cms_bp

    app.register_blueprint(cms_bp, url_prefix="/strony")

    app.logger.info("Aplikacja PZW uruchomiona w trybie: %s", config_name)

    return app
