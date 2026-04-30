"""
Rotas de gerenciamento de lojas
"""
from flask import Blueprint, render_template, request, redirect, url_for, flash
from flask_login import login_required
from models import Loja, Produto, EstoqueLoja, db
from forms import LojaForm, EstoqueLojaForm
from auth import requer_admin

lojas_bp = Blueprint('lojas', __name__, url_prefix='/lojas')


@lojas_bp.route('/')
@login_required
def index():
    """Lista todas as lojas"""
    lojas = Loja.query.order_by(Loja.nome).all()
    return render_template('lojas.html', lojas=lojas)


@lojas_bp.route('/produto/venda')
@login_required
def produto_venda():
    """Página para saída de produto de loja"""
    return render_template('produto_venda.html')


@lojas_bp.route('/produto/movimentar')
@login_required
def produto_movimentar():
    """Página para movimentar produto entre lojas"""
    return render_template('produto_movimentar.html')


@lojas_bp.route('/produto/chegada')
@login_required
def produto_chegada():
    """Página para registrar chegada de produto"""
    return render_template('produto_chegada.html')


@lojas_bp.route('/novo', methods=['GET', 'POST'])
@login_required
@requer_admin
def novo():
    """Criar nova loja"""
    form = LojaForm()
    if form.validate_on_submit():
        loja = Loja(
            nome=form.nome.data,
            endereco=form.endereco.data,
            telefone=form.telefone.data,
            email=form.email.data
        )

        db.session.add(loja)
        db.session.commit()

        flash('Loja criada com sucesso!', 'success')
        return redirect(url_for('lojas.index'))

    return render_template('loja_form.html', form=form, titulo='Nova Loja')


@lojas_bp.route('/editar/<int:id>', methods=['GET', 'POST'])
@login_required
@requer_admin
def editar(id):
    """Editar loja existente"""
    loja = Loja.query.get_or_404(id)
    form = LojaForm(obj=loja)

    if form.validate_on_submit():
        loja.nome = form.nome.data
        loja.endereco = form.endereco.data
        loja.telefone = form.telefone.data
        loja.email = form.email.data

        db.session.commit()
        flash('Loja atualizada com sucesso!', 'success')
        return redirect(url_for('lojas.index'))

    return render_template('loja_form.html', form=form, titulo='Editar Loja')


def _load_estoque_choices(form):
    form.loja_id.choices = [(loja.id, loja.nome) for loja in Loja.query.order_by(Loja.nome).all()]
    form.produto_id.choices = [
        (produto.id, f"{produto.nome} ({produto.tipo})")
        for produto in Produto.query.order_by(Produto.nome).all()
    ]
    return form


@lojas_bp.route('/estoque')
@login_required
def estoque():
    """Lista todos os estoques por loja"""
    loja_id = request.args.get('loja', type=int)
    produto_id = request.args.get('produto', type=int)
    query = EstoqueLoja.query.join(Loja).join(Produto)

    if loja_id:
        query = query.filter(EstoqueLoja.loja_id == loja_id)
    if produto_id:
        query = query.filter(EstoqueLoja.produto_id == produto_id)

    estoques = query.order_by(Loja.nome, Produto.nome).all()
    lojas = Loja.query.order_by(Loja.nome).all()
    produtos = Produto.query.order_by(Produto.nome).all()

    return render_template(
        'estoques_lojas.html',
        estoques=estoques,
        lojas=lojas,
        produtos=produtos,
        loja_id=loja_id,
        produto_id=produto_id
    )


@lojas_bp.route('/estoque/novo', methods=['GET', 'POST'])
@login_required
@requer_admin
def estoque_novo():
    """Criar novo registro de estoque por loja"""
    form = _load_estoque_choices(EstoqueLojaForm())

    if form.validate_on_submit():
        estoque = EstoqueLoja(
            loja_id=form.loja_id.data,
            produto_id=form.produto_id.data,
            quantidade=form.quantidade.data
        )
        db.session.add(estoque)
        db.session.commit()

        flash('Estoque por loja cadastrado com sucesso!', 'success')
        return redirect(url_for('lojas.estoque'))

    return render_template('estoque_loja_form.html', form=form, titulo='Novo estoque por loja')


@lojas_bp.route('/estoque/editar/<int:id>', methods=['GET', 'POST'])
@login_required
@requer_admin
def estoque_editar(id):
    """Editar estoque por loja existente"""
    estoque = EstoqueLoja.query.get_or_404(id)
    form = _load_estoque_choices(EstoqueLojaForm(obj=estoque))

    if form.validate_on_submit():
        estoque.loja_id = form.loja_id.data
        estoque.produto_id = form.produto_id.data
        estoque.quantidade = form.quantidade.data
        db.session.commit()

        flash('Estoque por loja atualizado com sucesso!', 'success')
        return redirect(url_for('lojas.estoque'))

    return render_template('estoque_loja_form.html', form=form, titulo='Editar estoque por loja')


@lojas_bp.route('/estoque/excluir/<int:id>', methods=['POST'])
@login_required
@requer_admin
def estoque_excluir(id):
    """Excluir registro de estoque por loja"""
    estoque = EstoqueLoja.query.get_or_404(id)
    db.session.delete(estoque)
    db.session.commit()

    flash('Registro de estoque excluído com sucesso!', 'warning')
    return redirect(url_for('lojas.estoque'))


@lojas_bp.route('/toggle/<int:id>', methods=['POST'])
@login_required
@requer_admin
def toggle(id):
    """Ativar/desativar loja"""
    loja = Loja.query.get_or_404(id)

    loja.ativo = not loja.ativo
    db.session.commit()

    status = 'ativada' if loja.ativo else 'desativada'
    flash(f'Loja {status} com sucesso!', 'success')
    return redirect(url_for('lojas.index'))


@lojas_bp.route('/excluir/<int:id>', methods=['POST'])
@login_required
@requer_admin
def excluir(id):
    """Excluir loja"""
    loja = Loja.query.get_or_404(id)

    # Verificar se há estoques associados
    if loja.estoques:
        flash('Não é possível excluir uma loja que possui produtos em estoque.', 'danger')
        return redirect(url_for('lojas.index'))

    db.session.delete(loja)
    db.session.commit()

    flash('Loja excluída com sucesso!', 'warning')
    return redirect(url_for('lojas.index'))