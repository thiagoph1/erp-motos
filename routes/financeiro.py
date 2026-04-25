"""
Rotas financeiras
"""
from flask import Blueprint, render_template
from flask_login import login_required
from auth import requer_gerente_ou_admin

financeiro_bp = Blueprint('financeiro', __name__, url_prefix='/financeiro')


@financeiro_bp.route('/')
@login_required
@requer_gerente_ou_admin
def index():
    """Página financeira"""
    return render_template('financeiro.html', titulo='Financeiro')