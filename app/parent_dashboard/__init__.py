from flask import Blueprint

parent_bp = Blueprint('parent', __name__)

from app.parent_dashboard import routes
