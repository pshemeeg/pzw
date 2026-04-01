from flask import Blueprint

bp = Blueprint("sedziowie", __name__, template_folder="../../templates/sedziowie")

from app.blueprints.sedziowie import routes  # noqa: E402, F401
