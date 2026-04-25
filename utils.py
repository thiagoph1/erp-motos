"""
Funções utilitárias da aplicação
"""
from datetime import datetime
from flask import current_app
from models import Produto, EstoqueLoja


def contar_alertas_estoque():
    """
    Conta quantos produtos estão abaixo do estoque mínimo em qualquer loja

    Returns:
        int: Número de produtos com alerta de estoque
    """
    return EstoqueLoja.query.filter(EstoqueLoja.quantidade <= EstoqueLoja.estoque_minimo).count()


def formatar_moeda(valor):
    """
    Formata um valor numérico para moeda brasileira

    Args:
        valor: Valor numérico

    Returns:
        str: Valor formatado como moeda
    """
    if valor is None:
        return "R$ 0,00"
    return f"R$ {valor:,.2f}".replace(",", "X").replace(".", ",").replace("X", ".")


def formatar_data(data):
    """
    Formata uma data para o padrão brasileiro

    Args:
        data: Objeto datetime ou date

    Returns:
        str: Data formatada
    """
    if isinstance(data, datetime):
        return data.strftime('%d/%m/%Y %H:%M')
    elif hasattr(data, 'strftime'):
        return data.strftime('%d/%m/%Y')
    return str(data)


def calcular_totais_dashboard():
    """
    Calcula os totais para exibição no dashboard

    Returns:
        dict: Dicionário com totais calculados
    """
    from models import Produto, Cliente, Usuario, Venda, Lancamento, db
    from datetime import date

    hoje = date.today()

    # Contadores básicos
    totais = {
        'total_motos': db.session.query(db.func.sum(EstoqueLoja.quantidade)).filter(
            EstoqueLoja.produto.has(tipo='moto')
        ).scalar() or 0,
        'total_pecas': db.session.query(db.func.sum(EstoqueLoja.quantidade)).filter(
            EstoqueLoja.produto.has(tipo='peca')
        ).scalar() or 0,
        'total_clientes': Cliente.query.count(),
        'total_usuarios': Usuario.query.count(),
    }

    # Vendas do mês
    totais['vendas_mes'] = Venda.query.filter(
        db.extract('month', Venda.criado_em) == hoje.month,
        db.extract('year', Venda.criado_em) == hoje.year,
        Venda.status == 'concluida'
    ).count()

    # Receitas e despesas do mês
    totais['receitas_mes'] = db.session.query(db.func.sum(Lancamento.valor)).filter(
        Lancamento.tipo == 'receita',
        db.extract('month', Lancamento.data) == hoje.month,
        db.extract('year', Lancamento.data) == hoje.year
    ).scalar() or 0

    totais['despesas_mes'] = db.session.query(db.func.sum(Lancamento.valor)).filter(
        Lancamento.tipo == 'despesa',
        db.extract('month', Lancamento.data) == hoje.month,
        db.extract('year', Lancamento.data) == hoje.year
    ).scalar() or 0

    # Saldo do mês
    totais['saldo_mes'] = totais['receitas_mes'] - totais['despesas_mes']

    return totais