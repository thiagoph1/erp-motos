"""
Aplicação principal ERP Motos
"""
from flask import Flask
from flask_login import LoginManager
from datetime import datetime

# Importações locais
from config import Config
from models import db
from utils import contar_alertas_estoque

# Blueprints
from routes.auth import auth_bp
from routes.main import main_bp
from routes.usuarios import usuarios_bp
from routes.produtos import produtos_bp


def create_app():
    """Factory function para criar a aplicação Flask"""
    app = Flask(__name__)
    app.config.from_object(Config)

    # Inicializar extensões
    db.init_app(app)

    login_manager = LoginManager()
    login_manager.init_app(app)
    login_manager.login_view = Config.LOGIN_VIEW
    login_manager.login_message = Config.LOGIN_MESSAGE
    login_manager.login_message_category = Config.LOGIN_MESSAGE_CATEGORY

    # Registrar blueprints
    app.register_blueprint(auth_bp)
    app.register_blueprint(main_bp)
    app.register_blueprint(usuarios_bp)
    app.register_blueprint(produtos_bp)

    # Configurar login manager
    from models import Usuario
    @login_manager.user_loader
    def load_user(user_id):
        return Usuario.query.get(int(user_id))

    # Context processor para variáveis globais
    @app.context_processor
    def inject_globals():
        from flask_wtf.csrf import generate_csrf
        alertas = 0
        try:
            alertas = contar_alertas_estoque()
        except:
            pass  # Em caso de erro no banco, retorna 0
        return dict(
            now=datetime.now(),
            alertas_estoque=alertas,
            csrf_token=generate_csrf
        )

    # Criar tabelas e usuário admin se necessário
    with app.app_context():
        db.create_all()
        criar_usuario_admin()

    return app


def criar_usuario_admin():
    """Cria o usuário admin padrão se não existir"""
    from models import Usuario

    if not Usuario.query.first():
        admin = Usuario(
            nome='Administrador',
            username='admin',
            email='admin@motochefe.com',
            perfil='admin',
            ativo=True
        )
        admin.set_senha('Admin@123')
        db.session.add(admin)
        db.session.commit()
        print('✅ Usuário admin criado. Login: admin | Senha: Admin@123')
        print('⚠️  Troque a senha após o primeiro acesso!')


# Criar instância da aplicação
app = create_app()


if __name__ == '__main__':
    app.run(debug=True)