from flask import Blueprint

bp = Blueprint("zawodnicy", __name__, template_folder="../../templates/zawodnicy")

from app.blueprints.zawodnicy import routes  # noqa: E402, F401
