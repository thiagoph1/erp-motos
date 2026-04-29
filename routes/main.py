"""
Rotas principais da aplicação (dashboard e outras)
"""
from flask import Blueprint, render_template, request, redirect, url_for, flash
from flask_login import login_required
from models import Produto, Venda, Cliente, Usuario, EstoqueLoja, Loja
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

    # Estoque por loja (resumido)
    lojas = Loja.query.filter_by(ativo=True).order_by(Loja.nome).all()
    estoque_por_loja = []
    for loja in lojas:
        total_itens = EstoqueLoja.query.filter_by(loja_id=loja.id).count()
        total_valor = sum(e.valor_total for e in EstoqueLoja.query.filter_by(loja_id=loja.id).all())
        estoque_por_loja.append({
            'loja': loja,
            'total_itens': total_itens,
            'total_valor': total_valor
        })

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
        estoque_por_loja=estoque_por_loja
    )