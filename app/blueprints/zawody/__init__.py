from flask import Blueprint

bp = Blueprint("zawody", __name__, template_folder="../../templates/zawody")

from app.blueprints.zawody import routes  # noqa: E402, F401
