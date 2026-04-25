from dotenv import load_dotenv
load_dotenv()  # carrega o .env automaticamente se existir
from flask import Flask, render_template, request, redirect, url_for, flash, abort
from flask_sqlalchemy import SQLAlchemy
from flask_wtf import FlaskForm
from flask_login import LoginManager, UserMixin, login_user, login_required, logout_user, current_user
from wtforms import StringField, PasswordField, SubmitField, FloatField, IntegerField, SelectField, TextAreaField
from wtforms.validators import DataRequired, Length, Optional, Email
from werkzeug.security import generate_password_hash, check_password_hash
from datetime import datetime, date
from functools import wraps
import os

app = Flask(__name__)
app.config['SECRET_KEY'] = os.environ.get('SECRET_KEY', 'troque-esta-chave-em-producao')
app.config['SQLALCHEMY_DATABASE_URI'] = os.environ.get('DATABASE_URL', 'sqlite:///erp_motos.db')
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app)
login_manager = LoginManager(app)
login_manager.login_view = 'login'
login_manager.login_message = 'Por favor, faça login para acessar esta página.'
login_manager.login_message_category = 'warning'

# ──────────────────────────────────────────────
# PERFIS DE ACESSO
# admin    → acesso total (gerencia usuários, financeiro, tudo)
# gerente  → acesso a tudo exceto gerenciamento de usuários
# vendedor → apenas vendas, clientes e visualizar estoque
# ──────────────────────────────────────────────

PERFIS = ['admin', 'gerente', 'vendedor']

def requer_perfil(*perfis):
    """Decorator para restringir acesso por perfil."""
    def decorator(f):
        @wraps(f)
        def decorated(*args, **kwargs):
            if not current_user.is_authenticated:
                return redirect(url_for('login'))
            if current_user.perfil not in perfis:
                flash('Você não tem permissão para acessar esta página.', 'danger')
                return redirect(url_for('index'))
            return f(*args, **kwargs)
        return decorated
    return decorator


# ──────────────────────────────────────────────
# MODELOS
# ──────────────────────────────────────────────

class Usuario(UserMixin, db.Model):
    __tablename__ = 'usuario'
    id          = db.Column(db.Integer, primary_key=True)
    nome        = db.Column(db.String(100), nullable=False)
    username    = db.Column(db.String(50), unique=True, nullable=False)
    email       = db.Column(db.String(120), unique=True)
    senha_hash  = db.Column(db.String(256), nullable=False)
    perfil      = db.Column(db.String(20), nullable=False, default='vendedor')
    ativo       = db.Column(db.Boolean, default=True)
    criado_em   = db.Column(db.DateTime, default=datetime.utcnow)

    def set_senha(self, senha):
        self.senha_hash = generate_password_hash(senha)

    def check_senha(self, senha):
        return check_password_hash(self.senha_hash, senha)

    def __repr__(self):
        return f'<Usuario {self.username} [{self.perfil}]>'


class Produto(db.Model):
    __tablename__ = 'produto'
    id              = db.Column(db.Integer, primary_key=True)
    nome            = db.Column(db.String(100), nullable=False)
    tipo            = db.Column(db.String(20), nullable=False, default='peca')  # 'moto' | 'peca'
    marca           = db.Column(db.String(50))
    modelo          = db.Column(db.String(50))
    descricao       = db.Column(db.Text)
    preco_custo     = db.Column(db.Float, default=0.0)
    preco_venda     = db.Column(db.Float, nullable=False)
    quantidade      = db.Column(db.Integer, default=0)
    estoque_minimo  = db.Column(db.Integer, default=1)
    criado_em       = db.Column(db.DateTime, default=datetime.utcnow)
    itens_venda     = db.relationship('ItemVenda', backref='produto', lazy=True)

    @property
    def abaixo_minimo(self):
        return self.quantidade <= self.estoque_minimo

    @property
    def margem(self):
        if self.preco_custo and self.preco_custo > 0:
            return ((self.preco_venda - self.preco_custo) / self.preco_custo) * 100
        return None


class Cliente(db.Model):
    __tablename__ = 'cliente'
    id          = db.Column(db.Integer, primary_key=True)
    nome        = db.Column(db.String(100), nullable=False)
    cpf         = db.Column(db.String(14))
    telefone    = db.Column(db.String(20))
    email       = db.Column(db.String(120))
    endereco    = db.Column(db.String(200))
    criado_em   = db.Column(db.DateTime, default=datetime.utcnow)
    vendas      = db.relationship('Venda', backref='cliente', lazy=True)


class Venda(db.Model):
    __tablename__ = 'venda'
    id              = db.Column(db.Integer, primary_key=True)
    cliente_id      = db.Column(db.Integer, db.ForeignKey('cliente.id'))
    usuario_id      = db.Column(db.Integer, db.ForeignKey('usuario.id'))  # quem registrou
    total           = db.Column(db.Float, nullable=False)
    desconto        = db.Column(db.Float, default=0.0)
    forma_pagamento = db.Column(db.String(30))
    status          = db.Column(db.String(20), default='concluida')  # concluida | cancelada
    observacao      = db.Column(db.Text)
    criado_em       = db.Column(db.DateTime, default=datetime.utcnow)
    itens           = db.relationship('ItemVenda', backref='venda', lazy=True)
    vendedor        = db.relationship('Usuario', backref='vendas', foreign_keys=[usuario_id])


class ItemVenda(db.Model):
    __tablename__ = 'item_venda'
    id              = db.Column(db.Integer, primary_key=True)
    venda_id        = db.Column(db.Integer, db.ForeignKey('venda.id'), nullable=False)
    produto_id      = db.Column(db.Integer, db.ForeignKey('produto.id'), nullable=False)
    quantidade      = db.Column(db.Integer, nullable=False)
    preco_unitario  = db.Column(db.Float, nullable=False)   # preço no momento da venda


class Lancamento(db.Model):
    __tablename__ = 'lancamento'
    id          = db.Column(db.Integer, primary_key=True)
    descricao   = db.Column(db.String(200), nullable=False)
    tipo        = db.Column(db.String(10), nullable=False)   # 'receita' | 'despesa'
    valor       = db.Column(db.Float, nullable=False)
    categoria   = db.Column(db.String(50))
    data        = db.Column(db.Date, default=date.today)
    usuario_id  = db.Column(db.Integer, db.ForeignKey('usuario.id'))
    criado_em   = db.Column(db.DateTime, default=datetime.utcnow)
    autor       = db.relationship('Usuario', backref='lancamentos', foreign_keys=[usuario_id])


# ──────────────────────────────────────────────
# FORMULÁRIOS
# ──────────────────────────────────────────────

class LoginForm(FlaskForm):
    username = StringField('Usuário', validators=[DataRequired()])
    password = PasswordField('Senha', validators=[DataRequired()])
    submit   = SubmitField('Entrar')


class UsuarioForm(FlaskForm):
    nome     = StringField('Nome completo', validators=[DataRequired(), Length(2, 100)])
    username = StringField('Usuário (login)', validators=[DataRequired(), Length(3, 50)])
    email    = StringField('E-mail', validators=[Optional(), Email()])
    perfil   = SelectField('Perfil', choices=[('vendedor','Vendedor'), ('gerente','Gerente'), ('admin','Administrador')])
    senha    = PasswordField('Senha', validators=[Optional(), Length(6)])
    submit   = SubmitField('Salvar')


class ProdutoForm(FlaskForm):
    nome           = StringField('Nome', validators=[DataRequired()])
    tipo           = SelectField('Tipo', choices=[('moto','Motocicleta'), ('peca','Peça / Acessório')])
    marca          = StringField('Marca', validators=[Optional()])
    modelo         = StringField('Modelo', validators=[Optional()])
    descricao      = TextAreaField('Descrição', validators=[Optional()])
    preco_custo    = FloatField('Preço de custo (R$)', validators=[Optional()])
    preco_venda    = FloatField('Preço de venda (R$)', validators=[DataRequired()])
    quantidade     = IntegerField('Quantidade em estoque', validators=[DataRequired()])
    estoque_minimo = IntegerField('Estoque mínimo', validators=[DataRequired()])
    submit         = SubmitField('Salvar')


class ClienteForm(FlaskForm):
    nome     = StringField('Nome', validators=[DataRequired()])
    cpf      = StringField('CPF', validators=[Optional()])
    telefone = StringField('Telefone', validators=[Optional()])
    email    = StringField('E-mail', validators=[Optional()])
    endereco = StringField('Endereço', validators=[Optional()])
    submit   = SubmitField('Salvar')


class LancamentoForm(FlaskForm):
    descricao = StringField('Descrição', validators=[DataRequired()])
    tipo      = SelectField('Tipo', choices=[('receita','Receita'), ('despesa','Despesa')])
    valor     = FloatField('Valor (R$)', validators=[DataRequired()])
    categoria = StringField('Categoria', validators=[Optional()])
    data      = StringField('Data', validators=[DataRequired()])
    submit    = SubmitField('Salvar')


# ──────────────────────────────────────────────
# LOGIN MANAGER
# ──────────────────────────────────────────────

@login_manager.user_loader
def load_user(user_id):
    return Usuario.query.get(int(user_id))


# ──────────────────────────────────────────────
# CONTEXT PROCESSOR (disponibiliza variáveis globais nos templates)
# ──────────────────────────────────────────────

@app.context_processor
def inject_globals():
    alertas = 0
    if current_user.is_authenticated:
        alertas = Produto.query.filter(Produto.quantidade <= Produto.estoque_minimo).count()
    return dict(now=datetime.now(), alertas_estoque=alertas)


# ──────────────────────────────────────────────
# ROTAS: AUTH
# ──────────────────────────────────────────────

@app.route('/login', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('index'))
    form = LoginForm()
    if form.validate_on_submit():
        user = Usuario.query.filter_by(username=form.username.data).first()
        if user and user.ativo and user.check_senha(form.password.data):
            login_user(user)
            flash(f'Bem-vindo, {user.nome}!', 'success')
            return redirect(request.args.get('next') or url_for('index'))
        flash('Usuário ou senha inválidos.', 'danger')
    return render_template('login.html', form=form)


@app.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('login'))


# ──────────────────────────────────────────────
# ROTAS: DASHBOARD
# ──────────────────────────────────────────────

@app.route('/')
@login_required
def index():
    hoje = date.today()

    total_motos = Produto.query.filter_by(tipo='moto').count()
    total_pecas = Produto.query.filter_by(tipo='peca').count()
    total_clientes = Cliente.query.count()
    total_usuarios = Usuario.query.count()

    vendas_mes = Venda.query.filter(
        db.extract('month', Venda.criado_em) == hoje.month,
        db.extract('year', Venda.criado_em) == hoje.year,
        Venda.status == 'concluida'
    ).count()

    receitas_mes = db.session.query(db.func.sum(Lancamento.valor)).filter(
        Lancamento.tipo == 'receita',
        db.extract('month', Lancamento.data) == hoje.month,
        db.extract('year', Lancamento.data) == hoje.year
    ).scalar() or 0

    despesas_mes = db.session.query(db.func.sum(Lancamento.valor)).filter(
        Lancamento.tipo == 'despesa',
        db.extract('month', Lancamento.data) == hoje.month,
        db.extract('year', Lancamento.data) == hoje.year
    ).scalar() or 0

    ultimas_vendas = Venda.query.order_by(Venda.criado_em.desc()).limit(5).all()
    produtos_alerta = Produto.query.filter(Produto.quantidade <= Produto.estoque_minimo).limit(5).all()

    return render_template('index.html',
        total_motos=total_motos, total_pecas=total_pecas,
        total_clientes=total_clientes, total_usuarios=total_usuarios,
        vendas_mes=vendas_mes, receitas_mes=receitas_mes,
        despesas_mes=despesas_mes, saldo_mes=receitas_mes - despesas_mes,
        ultimas_vendas=ultimas_vendas, produtos_alerta=produtos_alerta
    )


# ──────────────────────────────────────────────
# ROTAS: USUÁRIOS (somente admin)
# ──────────────────────────────────────────────

@app.route('/usuarios')
@login_required
@requer_perfil('admin')
def usuarios():
    lista = Usuario.query.order_by(Usuario.nome).all()
    return render_template('usuarios.html', usuarios=lista)


@app.route('/usuarios/novo', methods=['GET', 'POST'])
@login_required
@requer_perfil('admin')
def usuario_novo():
    form = UsuarioForm()
    if form.validate_on_submit():
        if Usuario.query.filter_by(username=form.username.data).first():
            flash('Este nome de usuário já existe.', 'danger')
            return render_template('usuario_form.html', form=form, titulo='Novo usuário')
        u = Usuario(nome=form.nome.data, username=form.username.data,
                    email=form.email.data or None, perfil=form.perfil.data)
        if form.senha.data:
            u.set_senha(form.senha.data)
        else:
            flash('Informe uma senha para o novo usuário.', 'danger')
            return render_template('usuario_form.html', form=form, titulo='Novo usuário')
        db.session.add(u)
        db.session.commit()
        flash(f'Usuário {u.username} criado com sucesso!', 'success')
        return redirect(url_for('usuarios'))
    return render_template('usuario_form.html', form=form, titulo='Novo usuário')


@app.route('/usuarios/editar/<int:id>', methods=['GET', 'POST'])
@login_required
@requer_perfil('admin')
def usuario_editar(id):
    u = Usuario.query.get_or_404(id)
    form = UsuarioForm(obj=u)
    if form.validate_on_submit():
        u.nome = form.nome.data
        u.username = form.username.data
        u.email = form.email.data or None
        u.perfil = form.perfil.data
        if form.senha.data:
            u.set_senha(form.senha.data)
        db.session.commit()
        flash('Usuário atualizado!', 'success')
        return redirect(url_for('usuarios'))
    return render_template('usuario_form.html', form=form, titulo='Editar usuário', usuario=u)


@app.route('/usuarios/desativar/<int:id>', methods=['POST'])
@login_required
@requer_perfil('admin')
def usuario_desativar(id):
    u = Usuario.query.get_or_404(id)
    if u.id == current_user.id:
        flash('Você não pode desativar sua própria conta.', 'danger')
    else:
        u.ativo = not u.ativo
        db.session.commit()
        acao = 'ativado' if u.ativo else 'desativado'
        flash(f'Usuário {acao}.', 'warning')
    return redirect(url_for('usuarios'))


# ──────────────────────────────────────────────
# ROTAS: PRODUTOS / ESTOQUE
# ──────────────────────────────────────────────

@app.route('/produtos')
@login_required
def produtos():
    tipo  = request.args.get('tipo', '')
    busca = request.args.get('busca', '')
    query = Produto.query
    if tipo:
        query = query.filter_by(tipo=tipo)
    if busca:
        query = query.filter(Produto.nome.ilike(f'%{busca}%'))
    lista = query.order_by(Produto.nome).all()
    return render_template('produtos.html', produtos=lista, tipo=tipo, busca=busca)


@app.route('/produtos/novo', methods=['GET', 'POST'])
@login_required
@requer_perfil('admin', 'gerente')
def produto_novo():
    form = ProdutoForm()
    if form.validate_on_submit():
        p = Produto(
            nome=form.nome.data, tipo=form.tipo.data,
            marca=form.marca.data, modelo=form.modelo.data,
            descricao=form.descricao.data,
            preco_custo=form.preco_custo.data or 0,
            preco_venda=form.preco_venda.data,
            quantidade=form.quantidade.data,
            estoque_minimo=form.estoque_minimo.data
        )
        db.session.add(p)
        db.session.commit()
        flash('Produto cadastrado!', 'success')
        return redirect(url_for('produtos'))
    return render_template('produto_form.html', form=form, titulo='Novo produto')


@app.route('/produtos/editar/<int:id>', methods=['GET', 'POST'])
@login_required
@requer_perfil('admin', 'gerente')
def produto_editar(id):
    p = Produto.query.get_or_404(id)
    form = ProdutoForm(obj=p)
    if form.validate_on_submit():
        p.nome = form.nome.data; p.tipo = form.tipo.data
        p.marca = form.marca.data; p.modelo = form.modelo.data
        p.descricao = form.descricao.data
        p.preco_custo = form.preco_custo.data or 0
        p.preco_venda = form.preco_venda.data
        p.quantidade = form.quantidade.data
        p.estoque_minimo = form.estoque_minimo.data
        db.session.commit()
        flash('Produto atualizado!', 'success')
        return redirect(url_for('produtos'))
    return render_template('produto_form.html', form=form, titulo='Editar produto', produto=p)


@app.route('/produtos/excluir/<int:id>', methods=['POST'])
@login_required
@requer_perfil('admin')
def produto_excluir(id):
    p = Produto.query.get_or_404(id)
    db.session.delete(p)
    db.session.commit()
    flash('Produto removido.', 'warning')
    return redirect(url_for('produtos'))


# ──────────────────────────────────────────────
# ROTAS: CLIENTES
# ──────────────────────────────────────────────

@app.route('/clientes')
@login_required
def clientes():
    busca = request.args.get('busca', '')
    query = Cliente.query
    if busca:
        query = query.filter(Cliente.nome.ilike(f'%{busca}%'))
    lista = query.order_by(Cliente.nome).all()
    return render_template('clientes.html', clientes=lista, busca=busca)


@app.route('/clientes/novo', methods=['GET', 'POST'])
@login_required
def cliente_novo():
    form = ClienteForm()
    if form.validate_on_submit():
        c = Cliente(nome=form.nome.data, cpf=form.cpf.data,
                    telefone=form.telefone.data, email=form.email.data,
                    endereco=form.endereco.data)
        db.session.add(c)
        db.session.commit()
        flash('Cliente cadastrado!', 'success')
        return redirect(url_for('clientes'))
    return render_template('cliente_form.html', form=form, titulo='Novo cliente')


@app.route('/clientes/editar/<int:id>', methods=['GET', 'POST'])
@login_required
def cliente_editar(id):
    c = Cliente.query.get_or_404(id)
    form = ClienteForm(obj=c)
    if form.validate_on_submit():
        c.nome = form.nome.data; c.cpf = form.cpf.data
        c.telefone = form.telefone.data; c.email = form.email.data
        c.endereco = form.endereco.data
        db.session.commit()
        flash('Cliente atualizado!', 'success')
        return redirect(url_for('clientes'))
    return render_template('cliente_form.html', form=form, titulo='Editar cliente', cliente=c)


# ──────────────────────────────────────────────
# ROTAS: VENDAS
# ──────────────────────────────────────────────

@app.route('/vendas')
@login_required
def vendas():
    lista = Venda.query.order_by(Venda.criado_em.desc()).all()
    return render_template('vendas.html', vendas=lista)


@app.route('/vendas/nova', methods=['GET', 'POST'])
@login_required
def venda_nova():
    clientes_lista = Cliente.query.order_by(Cliente.nome).all()
    produtos_lista = Produto.query.filter(Produto.quantidade > 0).order_by(Produto.nome).all()

    if request.method == 'POST':
        cliente_id = request.form.get('cliente_id') or None
        forma      = request.form.get('forma_pagamento', '')
        desconto   = float(request.form.get('desconto') or 0)
        obs        = request.form.get('observacao', '')
        prod_ids   = request.form.getlist('produto_id[]')
        quantidades = request.form.getlist('quantidade[]')

        if not prod_ids:
            flash('Adicione pelo menos um produto.', 'danger')
            return render_template('venda_form.html', clientes=clientes_lista, produtos=produtos_lista)

        total = 0
        itens = []
        erro  = False
        for pid, qty_str in zip(prod_ids, quantidades):
            prod = Produto.query.get(int(pid))
            qty  = int(qty_str or 0)
            if not prod or qty <= 0:
                continue
            if qty > prod.quantidade:
                flash(f'Estoque insuficiente para "{prod.nome}" (disponível: {prod.quantidade}).', 'danger')
                erro = True
                break
            subtotal = prod.preco_venda * qty
            total += subtotal
            itens.append((prod, qty))

        if erro:
            return render_template('venda_form.html', clientes=clientes_lista, produtos=produtos_lista)

        total_final = max(total - desconto, 0)
        venda = Venda(cliente_id=cliente_id, usuario_id=current_user.id,
                      total=total_final, desconto=desconto,
                      forma_pagamento=forma, observacao=obs)
        db.session.add(venda)
        db.session.flush()

        for prod, qty in itens:
            item = ItemVenda(venda_id=venda.id, produto_id=prod.id,
                             quantidade=qty, preco_unitario=prod.preco_venda)
            db.session.add(item)
            prod.quantidade -= qty

        # Lança automaticamente como receita
        db.session.add(Lancamento(
            descricao=f'Venda #{venda.id}', tipo='receita',
            valor=total_final, categoria='vendas',
            data=date.today(), usuario_id=current_user.id
        ))
        db.session.commit()
        flash(f'Venda #{ venda.id } registrada! Total: R$ {total_final:.2f}', 'success')
        return redirect(url_for('vendas'))

    return render_template('venda_form.html', clientes=clientes_lista, produtos=produtos_lista)


@app.route('/vendas/cancelar/<int:id>', methods=['POST'])
@login_required
@requer_perfil('admin', 'gerente')
def venda_cancelar(id):
    v = Venda.query.get_or_404(id)
    if v.status == 'concluida':
        v.status = 'cancelada'
        for item in v.itens:
            item.produto.quantidade += item.quantidade
        db.session.commit()
        flash('Venda cancelada e estoque reposto.', 'warning')
    return redirect(url_for('vendas'))


# ──────────────────────────────────────────────
# ROTAS: FINANCEIRO (admin e gerente)
# ──────────────────────────────────────────────

@app.route('/financeiro')
@login_required
@requer_perfil('admin', 'gerente')
def financeiro():
    mes   = request.args.get('mes', date.today().strftime('%Y-%m'))
    ano, m = map(int, mes.split('-'))
    lancamentos = Lancamento.query.filter(
        db.extract('month', Lancamento.data) == m,
        db.extract('year', Lancamento.data) == ano
    ).order_by(Lancamento.data.desc()).all()
    receitas  = sum(l.valor for l in lancamentos if l.tipo == 'receita')
    despesas  = sum(l.valor for l in lancamentos if l.tipo == 'despesa')
    return render_template('financeiro.html',
        lancamentos=lancamentos, receitas=receitas,
        despesas=despesas, saldo=receitas - despesas, mes=mes)


@app.route('/financeiro/novo', methods=['GET', 'POST'])
@login_required
@requer_perfil('admin', 'gerente')
def lancamento_novo():
    form = LancamentoForm()
    if not form.data.get('data'):
        form.data['data'] = date.today().strftime('%Y-%m-%d')
    if form.validate_on_submit():
        l = Lancamento(
            descricao=form.descricao.data, tipo=form.tipo.data,
            valor=form.valor.data, categoria=form.categoria.data,
            data=datetime.strptime(form.data.data, '%Y-%m-%d').date(),
            usuario_id=current_user.id
        )
        db.session.add(l)
        db.session.commit()
        flash('Lançamento registrado!', 'success')
        return redirect(url_for('financeiro'))
    return render_template('lancamento_form.html', form=form)


@app.route('/financeiro/excluir/<int:id>', methods=['POST'])
@login_required
@requer_perfil('admin')
def lancamento_excluir(id):
    l = Lancamento.query.get_or_404(id)
    db.session.delete(l)
    db.session.commit()
    flash('Lançamento removido.', 'warning')
    return redirect(url_for('financeiro'))


# ──────────────────────────────────────────────
# SEED INICIAL
# ──────────────────────────────────────────────

def seed_inicial():
    """Cria o usuário admin padrão se o banco estiver vazio."""
    if not Usuario.query.first():
        admin = Usuario(nome='Administrador', username='admin',
                        email='admin@motochefe.com', perfil='admin', ativo=True)
        admin.set_senha('Admin@123')
        db.session.add(admin)
        db.session.commit()
        print('✅ Usuário admin criado. Login: admin | Senha: Admin@123')
        print('⚠️  Troque a senha após o primeiro acesso!')


with app.app_context():
    db.create_all()
    seed_inicial()

if __name__ == '__main__':
    app.run(debug=True)