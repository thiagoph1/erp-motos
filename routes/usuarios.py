"""
Rotas de gerenciamento de usuários
"""
from flask import Blueprint, render_template, request, redirect, url_for, flash
from flask_login import login_required
from models import Usuario, db
from forms import UsuarioForm
from auth import requer_admin

usuarios_bp = Blueprint('usuarios', __name__, url_prefix='/usuarios')


@usuarios_bp.route('/')
@login_required
@requer_admin
def index():
    """Lista todos os usuários"""
    lista = Usuario.query.order_by(Usuario.nome).all()
    return render_template('usuarios.html', usuarios=lista)


@usuarios_bp.route('/novo', methods=['GET', 'POST'])
@login_required
@requer_admin
def novo():
    """Criar novo usuário"""
    form = UsuarioForm()
    if form.validate_on_submit():
        # Verifica se username já existe
        if Usuario.query.filter_by(username=form.username.data).first():
            flash('Este nome de usuário já está em uso.', 'danger')
            return render_template('usuario_form.html', form=form)

        user = Usuario(
            nome=form.nome.data,
            username=form.username.data,
            email=form.email.data,
            perfil=form.perfil.data
        )
        user.set_senha(form.senha.data)

        db.session.add(user)
        db.session.commit()

        flash('Usuário criado com sucesso!', 'success')
        return redirect(url_for('usuarios.index'))

    return render_template('usuario_form.html', form=form, titulo='Novo Usuário')


@usuarios_bp.route('/editar/<int:id>', methods=['GET', 'POST'])
@login_required
@requer_admin
def editar(id):
    """Editar usuário existente"""
    user = Usuario.query.get_or_404(id)
    form = UsuarioForm(obj=user)

    if form.validate_on_submit():
        # Verifica se username já existe (exceto para o próprio usuário)
        existing = Usuario.query.filter_by(username=form.username.data).first()
        if existing and existing.id != user.id:
            flash('Este nome de usuário já está em uso.', 'danger')
            return render_template('usuario_form.html', form=form, titulo='Editar Usuário')

        user.nome = form.nome.data
        user.username = form.username.data
        user.email = form.email.data
        user.perfil = form.perfil.data

        if form.senha.data:
            user.set_senha(form.senha.data)

        db.session.commit()
        flash('Usuário atualizado com sucesso!', 'success')
        return redirect(url_for('usuarios.index'))

    return render_template('usuario_form.html', form=form, titulo='Editar Usuário')


@usuarios_bp.route('/toggle/<int:id>', methods=['POST'])
@login_required
@requer_admin
def toggle(id):
    """Ativar/desativar usuário"""
    user = Usuario.query.get_or_404(id)

    if user.id == request.form.get('current_user_id', type=int):
        flash('Você não pode desativar seu próprio usuário.', 'danger')
        return redirect(url_for('usuarios.index'))

    user.ativo = not user.ativo
    db.session.commit()

    status = 'ativado' if user.ativo else 'desativado'
    flash(f'Usuário {status} com sucesso!', 'success')
    return redirect(url_for('usuarios.index'))


@usuarios_bp.route('/excluir/<int:id>', methods=['POST'])
@login_required
@requer_admin
def excluir(id):
    """Excluir usuário"""
    user = Usuario.query.get_or_404(id)

    if user.id == request.form.get('current_user_id', type=int):
        flash('Você não pode excluir seu próprio usuário.', 'danger')
        return redirect(url_for('usuarios.index'))

    db.session.delete(user)
    db.session.commit()

    flash('Usuário excluído com sucesso!', 'warning')
    return redirect(url_for('usuarios.index'))