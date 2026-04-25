"""
Rotas de autenticação
"""
from flask import Blueprint, render_template, redirect, url_for, flash, request
from flask_login import login_user, logout_user, current_user
from forms import LoginForm
from models import Usuario

auth_bp = Blueprint('auth', __name__, url_prefix='/auth')


@auth_bp.route('/login', methods=['GET', 'POST'])
def login():
    """Página de login"""
    if current_user.is_authenticated:
        return redirect(url_for('main.index'))

    form = LoginForm()
    if form.validate_on_submit():
        user = Usuario.query.filter_by(username=form.username.data).first()
        if user and user.ativo and user.check_senha(form.password.data):
            login_user(user)
            flash(f'Bem-vindo, {user.nome}!', 'success')
            return redirect(request.args.get('next') or url_for('main.index'))
        flash('Usuário ou senha inválidos.', 'danger')

    return render_template('login.html', form=form)


@auth_bp.route('/logout')
def logout():
    """Logout do usuário"""
    logout_user()
    return redirect(url_for('auth.login'))