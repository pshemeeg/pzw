from flask import Blueprint

bp = Blueprint("uzytkownicy", __name__, template_folder="../../templates/uzytkownicy")

from app.blueprints.uzytkownicy import routes  # noqa: E402, F401
