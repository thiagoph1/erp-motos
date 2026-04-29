"""
Modelos do banco de dados
"""
from datetime import datetime, date
from flask_sqlalchemy import SQLAlchemy
from flask_login import UserMixin
from werkzeug.security import generate_password_hash, check_password_hash

db = SQLAlchemy()

class Usuario(UserMixin, db.Model):
    """Modelo de usuário do sistema"""
    __tablename__ = 'usuario'

    id = db.Column(db.Integer, primary_key=True)
    nome = db.Column(db.String(100), nullable=False)
    username = db.Column(db.String(50), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True)
    senha_hash = db.Column(db.String(256), nullable=False)
    perfil = db.Column(db.String(20), nullable=False, default='vendedor')
    ativo = db.Column(db.Boolean, default=True)
    criado_em = db.Column(db.DateTime, default=datetime.utcnow)

    # Relacionamentos
    vendas = db.relationship('Venda', backref='vendedor', foreign_keys='Venda.usuario_id')
    lancamentos = db.relationship('Lancamento', backref='autor', foreign_keys='Lancamento.usuario_id')

    def set_senha(self, senha):
        """Define a senha do usuário (com hash)"""
        self.senha_hash = generate_password_hash(senha)

    def check_senha(self, senha):
        """Verifica se a senha está correta"""
        return check_password_hash(self.senha_hash, senha)

    def __repr__(self):
        return f'<Usuario {self.username} [{self.perfil}]>'


class Produto(db.Model):
    """Modelo de produto (moto ou peça)"""
    __tablename__ = 'produto'

    id = db.Column(db.Integer, primary_key=True)
    nome = db.Column(db.String(100), nullable=False)
    tipo = db.Column(db.String(20), nullable=False, default='peca')  # 'moto' | 'peca'
    marca = db.Column(db.String(50))
    modelo = db.Column(db.String(50))
    descricao = db.Column(db.Text)
    preco_custo = db.Column(db.Float, default=0.0)
    preco_venda = db.Column(db.Float, nullable=False)
    criado_em = db.Column(db.DateTime, default=datetime.utcnow)

    # Relacionamentos
    itens_venda = db.relationship('ItemVenda', backref='produto', lazy=True)

    @property
    def quantidade(self):
        """Quantidade total sincronizada de todas as lojas"""
        return sum(estoque.quantidade for estoque in self.estoques_loja) if self.estoques_loja else 0

    @property
    def abaixo_minimo(self):
        """Verifica se o produto está abaixo do estoque mínimo em alguma loja"""
        return any(estoque.abaixo_minimo for estoque in self.estoques_loja) if self.estoques_loja else False

    @property
    def margem(self):
        """Calcula a margem de lucro em porcentagem"""
        if self.preco_custo and self.preco_custo > 0:
            return ((self.preco_venda - self.preco_custo) / self.preco_custo) * 100
        return None

    @property
    def estoques_por_loja(self):
        """Retorna dicionário com quantidade por loja"""
        return {estoque.loja.nome: estoque.quantidade for estoque in self.estoques_loja}

    def __repr__(self):
        return f'<Produto {self.nome} ({self.tipo}) - Total: {self.quantidade}>'


class Cliente(db.Model):
    """Modelo de cliente"""
    __tablename__ = 'cliente'

    id = db.Column(db.Integer, primary_key=True)
    nome = db.Column(db.String(100), nullable=False)
    cpf = db.Column(db.String(14))
    telefone = db.Column(db.String(20))
    email = db.Column(db.String(120))
    endereco = db.Column(db.String(200))
    criado_em = db.Column(db.DateTime, default=datetime.utcnow)

    # Relacionamentos
    vendas = db.relationship('Venda', backref='cliente', lazy=True)

    def __repr__(self):
        return f'<Cliente {self.nome}>'


class Venda(db.Model):
    """Modelo de venda"""
    __tablename__ = 'venda'

    id = db.Column(db.Integer, primary_key=True)
    cliente_id = db.Column(db.Integer, db.ForeignKey('cliente.id'))
    usuario_id = db.Column(db.Integer, db.ForeignKey('usuario.id'))  # quem registrou
    total = db.Column(db.Float, nullable=False)
    desconto = db.Column(db.Float, default=0.0)
    forma_pagamento = db.Column(db.String(30))
    status = db.Column(db.String(20), default='concluida')  # concluida | cancelada
    observacao = db.Column(db.Text)
    criado_em = db.Column(db.DateTime, default=datetime.utcnow)

    # Relacionamentos
    itens = db.relationship('ItemVenda', backref='venda', lazy=True)

    def __repr__(self):
        return f'<Venda {self.id} - R$ {self.total:.2f}>'


class ItemVenda(db.Model):
    """Modelo de item de venda"""
    __tablename__ = 'item_venda'

    id = db.Column(db.Integer, primary_key=True)
    venda_id = db.Column(db.Integer, db.ForeignKey('venda.id'), nullable=False)
    produto_id = db.Column(db.Integer, db.ForeignKey('produto.id'), nullable=False)
    quantidade = db.Column(db.Integer, nullable=False)
    preco_unitario = db.Column(db.Float, nullable=False)  # preço no momento da venda

    def __repr__(self):
        return f'<ItemVenda {self.produto_id} x{self.quantidade}>'


class Lancamento(db.Model):
    """Modelo de lançamento financeiro"""
    __tablename__ = 'lancamento'

    id = db.Column(db.Integer, primary_key=True)
    descricao = db.Column(db.String(200), nullable=False)
    tipo = db.Column(db.String(10), nullable=False)  # 'receita' | 'despesa'
    valor = db.Column(db.Float, nullable=False)
    categoria = db.Column(db.String(50))
    data = db.Column(db.Date, default=date.today)
    usuario_id = db.Column(db.Integer, db.ForeignKey('usuario.id'))
    criado_em = db.Column(db.DateTime, default=datetime.utcnow)

    def __repr__(self):
        return f'<Lancamento {self.descricao} - R$ {self.valor:.2f}>'


class Loja(db.Model):
    """Modelo de loja"""
    __tablename__ = 'loja'

    id = db.Column(db.Integer, primary_key=True)
    nome = db.Column(db.String(100), nullable=False)
    endereco = db.Column(db.String(200))
    telefone = db.Column(db.String(20))
    email = db.Column(db.String(120))
    ativo = db.Column(db.Boolean, default=True)
    criado_em = db.Column(db.DateTime, default=datetime.utcnow)

    # Relacionamentos
    estoques = db.relationship('EstoqueLoja', backref='loja', lazy=True)

    @property
    def total_produtos(self):
        """Total de produtos em estoque nesta loja"""
        return sum(estoque.quantidade for estoque in self.estoques if estoque.quantidade > 0)

    def __repr__(self):
        return f'<Loja {self.nome}>'


class EstoqueLoja(db.Model):
    """Modelo de estoque por loja"""
    __tablename__ = 'estoque_loja'

    id = db.Column(db.Integer, primary_key=True)
    loja_id = db.Column(db.Integer, db.ForeignKey('loja.id'), nullable=False)
    produto_id = db.Column(db.Integer, db.ForeignKey('produto.id'), nullable=False)
    quantidade = db.Column(db.Integer, default=0)
    ultima_atualizacao = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relacionamentos
    produto = db.relationship('Produto', backref='estoques_loja')

    __table_args__ = (
        db.UniqueConstraint('loja_id', 'produto_id', name='unique_loja_produto'),
    )

    @property
    def valor_total(self):
        """Calcula o valor total do estoque (preço de venda)"""
        return self.quantidade * self.produto.preco_venda

    def __repr__(self):
        return f'<EstoqueLoja {self.loja.nome} - {self.produto.nome}: {self.quantidade}>'