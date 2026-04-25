"""
Módulo de autenticação e autorização
"""
from functools import wraps
from flask import redirect, url_for, flash
from flask_login import current_user


def requer_perfil(*perfis):
    """
    Decorator para restringir acesso por perfil.

    Args:
        *perfis: Perfis permitidos (ex: 'admin', 'gerente')

    Returns:
        Função decorada com verificação de permissão
    """
    def decorator(f):
        @wraps(f)
        def decorated(*args, **kwargs):
            if not current_user.is_authenticated:
                return redirect(url_for('auth.login'))
            if current_user.perfil not in perfis:
                flash('Você não tem permissão para acessar esta página.', 'danger')
                return redirect(url_for('main.index'))
            return f(*args, **kwargs)
        return decorated
    return decorator


def requer_admin(f):
    """Decorator específico para acesso apenas de admin"""
    return requer_perfil('admin')(f)


def requer_gerente_ou_admin(f):
    """Decorator para acesso de gerente ou admin"""
    return requer_perfil('gerente', 'admin')(f)