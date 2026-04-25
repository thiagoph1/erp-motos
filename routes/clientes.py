"""
Rotas de clientes
"""
from flask import Blueprint, render_template
from flask_login import login_required

clientes_bp = Blueprint('clientes', __name__, url_prefix='/clientes')


@clientes_bp.route('/')
@login_required
def index():
    """Página de clientes"""
    return render_template('clientes.html', titulo='Clientes')