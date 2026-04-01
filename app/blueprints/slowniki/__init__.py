from flask import Blueprint

bp = Blueprint("slowniki", __name__, template_folder="../../templates/slowniki")

from app.blueprints.slowniki import routes  # noqa: E402, F401
