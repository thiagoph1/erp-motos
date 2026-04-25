"""
Configurações da aplicação Flask
"""
import os
from dotenv import load_dotenv

# Carrega variáveis de ambiente
load_dotenv()

class Config:
    """Configurações base da aplicação"""

    # Flask
    SECRET_KEY = os.environ.get('SECRET_KEY', 'troque-esta-chave-em-producao')

    # SQLAlchemy
    SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URL', 'sqlite:///erp_motos.db')
    SQLALCHEMY_TRACK_MODIFICATIONS = False

    # Flask-Login
    LOGIN_VIEW = 'auth.login'
    LOGIN_MESSAGE = 'Por favor, faça login para acessar esta página.'
    LOGIN_MESSAGE_CATEGORY = 'warning'

    # Perfis de acesso
    PERFIS = ['admin', 'gerente', 'vendedor']

    # Regras de permissão por perfil
    PERMISSOES = {
        'admin': ['usuarios', 'produtos', 'clientes', 'vendas', 'financeiro'],
        'gerente': ['produtos', 'clientes', 'vendas', 'financeiro'],
        'vendedor': ['produtos_view', 'clientes', 'vendas']
    }