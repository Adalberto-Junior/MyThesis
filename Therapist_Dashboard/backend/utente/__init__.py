from flask import Blueprint

utente_bp = Blueprint('utente', __name__, url_prefix='/utente')

from . import routes  # Importa rotas e associa ao Blueprint