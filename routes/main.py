"""
Rotas principais da aplicação (dashboard e outras)
"""
from flask import Blueprint, render_template, request, redirect, url_for, flash
from flask_login import login_required
from models import Produto, Venda, Cliente, Usuario, EstoqueLoja
from utils import calcular_totais_dashboard

main_bp = Blueprint('main', __name__)


@main_bp.route('/')
@login_required
def index():
    """Página inicial (dashboard)"""
    hoje = request.args.get('data', None)

    # Calcula totais
    totais = calcular_totais_dashboard()

    # Últimas vendas
    ultimas_vendas = Venda.query.order_by(Venda.criado_em.desc()).limit(5).all()

    # Produtos com alerta de estoque (agora por loja)
    produtos_alerta = EstoqueLoja.query.filter(
        EstoqueLoja.quantidade <= EstoqueLoja.estoque_minimo
    ).join(Produto).order_by(Produto.nome).limit(5).all()

    return render_template('index.html',
        total_motos=totais['total_motos'],
        total_pecas=totais['total_pecas'],
        total_clientes=totais['total_clientes'],
        total_usuarios=totais['total_usuarios'],
        vendas_mes=totais['vendas_mes'],
        receitas_mes=totais['receitas_mes'],
        despesas_mes=totais['despesas_mes'],
        saldo_mes=totais['saldo_mes'],
        ultimas_vendas=ultimas_vendas,
        produtos_alerta=produtos_alerta
    )