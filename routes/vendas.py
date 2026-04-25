"""
Rotas de vendas
"""
from flask import Blueprint, render_template
from flask_login import login_required

vendas_bp = Blueprint('vendas', __name__, url_prefix='/vendas')


@vendas_bp.route('/')
@login_required
def index():
    """Página de vendas"""
    return render_template('vendas.html', titulo='Vendas')