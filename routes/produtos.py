"""
Rotas de gerenciamento de produtos
"""
from flask import Blueprint, render_template, request, redirect, url_for, flash
from flask_login import login_required
from models import Produto, db
from forms import ProdutoForm
from auth import requer_gerente_ou_admin

produtos_bp = Blueprint('produtos', __name__, url_prefix='/produtos')


@produtos_bp.route('/')
@login_required
def index():
    """Lista todos os produtos"""
    tipo_filtro = request.args.get('tipo')
    busca = request.args.get('busca')

    query = Produto.query

    if tipo_filtro:
        query = query.filter_by(tipo=tipo_filtro)

    if busca:
        query = query.filter(Produto.nome.contains(busca))

    produtos = query.order_by(Produto.nome).all()
    return render_template('produtos.html', produtos=produtos, tipo_filtro=tipo_filtro, busca=busca)


@produtos_bp.route('/novo', methods=['GET', 'POST'])
@login_required
@requer_gerente_ou_admin
def novo():
    """Criar novo produto"""
    form = ProdutoForm()
    if form.validate_on_submit():
        produto = Produto(
            nome=form.nome.data,
            tipo=form.tipo.data,
            marca=form.marca.data,
            modelo=form.modelo.data,
            descricao=form.descricao.data,
            preco_custo=form.preco_custo.data or 0,
            preco_venda=form.preco_venda.data
        )

        db.session.add(produto)
        db.session.commit()

        flash('Produto criado com sucesso!', 'success')
        return redirect(url_for('produtos.index'))

    return render_template('produto_form.html', form=form, titulo='Novo Produto')


@produtos_bp.route('/editar/<int:id>', methods=['GET', 'POST'])
@login_required
@requer_gerente_ou_admin
def editar(id):
    """Editar produto existente"""
    produto = Produto.query.get_or_404(id)
    form = ProdutoForm(obj=produto)

    if form.validate_on_submit():
        produto.nome = form.nome.data
        produto.tipo = form.tipo.data
        produto.marca = form.marca.data
        produto.modelo = form.modelo.data
        produto.descricao = form.descricao.data
        produto.preco_custo = form.preco_custo.data or 0
        produto.preco_venda = form.preco_venda.data

        db.session.commit()
        flash('Produto atualizado com sucesso!', 'success')
        return redirect(url_for('produtos.index'))

    return render_template('produto_form.html', form=form, titulo='Editar Produto')


@produtos_bp.route('/excluir/<int:id>', methods=['POST'])
@login_required
@requer_gerente_ou_admin
def excluir(id):
    """Excluir produto"""
    produto = Produto.query.get_or_404(id)
    db.session.delete(produto)
    db.session.commit()

    flash('Produto excluído com sucesso!', 'warning')
    return redirect(url_for('produtos.index'))