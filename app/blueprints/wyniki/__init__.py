from flask import Blueprint

bp = Blueprint('wyniki', __name__)

from . import routes
