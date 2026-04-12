from flask import Blueprint

bp = Blueprint("profil", __name__, template_folder="../../templates/profil")

from app.blueprints.profil import routes  # noqa: E402, F401
