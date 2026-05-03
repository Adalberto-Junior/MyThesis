from flask import Blueprint

casaViva_bp = Blueprint('home', __name__, url_prefix='/home')

from . import routes

# Importar e registrar o auth_bp dentro deste blueprint
from .auth import auth_bp
casaViva_bp.register_blueprint(auth_bp)