"""
Formulários WTForms da aplicação
"""
from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, SubmitField, FloatField, IntegerField, SelectField, TextAreaField
from wtforms.validators import DataRequired, Length, Optional, Email, NumberRange


class LoginForm(FlaskForm):
    """Formulário de login"""
    username = StringField('Usuário', validators=[DataRequired()])
    password = PasswordField('Senha', validators=[DataRequired()])
    submit = SubmitField('Entrar')


class UsuarioForm(FlaskForm):
    """Formulário para criação/edição de usuários"""
    nome = StringField('Nome completo', validators=[DataRequired(), Length(2, 100)])
    username = StringField('Usuário (login)', validators=[DataRequired(), Length(3, 50)])
    email = StringField('E-mail', validators=[Optional(), Email()])
    perfil = SelectField('Perfil', choices=[
        ('vendedor', 'Vendedor'),
        ('gerente', 'Gerente'),
        ('admin', 'Administrador')
    ])
    senha = PasswordField('Senha', validators=[Optional(), Length(6)])
    submit = SubmitField('Salvar')


class ProdutoForm(FlaskForm):
    """Formulário para criação/edição de produtos"""
    nome = StringField('Nome', validators=[DataRequired()])
    tipo = SelectField('Tipo', choices=[
        ('moto', 'Motocicleta'),
        ('peca', 'Peça / Acessório')
    ])
    marca = StringField('Marca', validators=[Optional()])
    modelo = StringField('Modelo', validators=[Optional()])
    descricao = TextAreaField('Descrição', validators=[Optional()])
    preco_custo = FloatField('Preço de custo (R$)', validators=[Optional()])
    preco_venda = FloatField('Preço de venda (R$)', validators=[DataRequired()])
    submit = SubmitField('Salvar')


class ClienteForm(FlaskForm):
    """Formulário para criação/edição de clientes"""
    nome = StringField('Nome', validators=[DataRequired()])
    cpf = StringField('CPF', validators=[Optional()])
    telefone = StringField('Telefone', validators=[Optional()])
    email = StringField('E-mail', validators=[Optional()])
    endereco = StringField('Endereço', validators=[Optional()])
    submit = SubmitField('Salvar')


class LancamentoForm(FlaskForm):
    """Formulário para lançamentos financeiros"""
    descricao = StringField('Descrição', validators=[DataRequired()])
    tipo = SelectField('Tipo', choices=[
        ('receita', 'Receita'),
        ('despesa', 'Despesa')
    ])
    valor = FloatField('Valor (R$)', validators=[DataRequired()])
    categoria = StringField('Categoria', validators=[Optional()])
    data = StringField('Data', validators=[DataRequired()])
    submit = SubmitField('Salvar')


class LojaForm(FlaskForm):
    """Formulário para criação/edição de lojas"""
    nome = StringField('Nome da loja', validators=[DataRequired(), Length(2, 100)])
    endereco = StringField('Endereço', validators=[Optional()])
    telefone = StringField('Telefone', validators=[Optional()])
    email = StringField('E-mail', validators=[Optional(), Email()])
    submit = SubmitField('Salvar')


class EstoqueLojaForm(FlaskForm):
    """Formulário para estoque por loja"""
    loja_id = SelectField('Loja', coerce=int, validators=[DataRequired()])
    produto_id = SelectField('Produto', coerce=int, validators=[DataRequired()])
    quantidade = IntegerField('Quantidade', validators=[DataRequired(), NumberRange(min=1)])
    submit = SubmitField('Salvar')


class ProdutoSaidaForm(FlaskForm):
    """Formulário para saída de produto da loja"""
    loja_id = SelectField('Loja', coerce=int, validators=[DataRequired()])
    produto_id = SelectField('Produto', coerce=int, validators=[DataRequired()])
    quantidade = IntegerField('Quantidade', validators=[DataRequired(), NumberRange(min=1)])
    submit = SubmitField('Registrar Saída')


class ProdutoMovimentarForm(FlaskForm):
    """Formulário para movimentar produto entre lojas"""
    loja_origem_id = SelectField('Loja de origem', coerce=int, validators=[DataRequired()])
    loja_destino_id = SelectField('Loja de destino', coerce=int, validators=[DataRequired()])
    produto_id = SelectField('Produto', coerce=int, validators=[DataRequired()])
    quantidade = IntegerField('Quantidade', validators=[DataRequired(), NumberRange(min=1)])
    submit = SubmitField('Transferir')


class ProdutoChegadaForm(FlaskForm):
    """Formulário para chegada de produto na loja"""
    loja_id = SelectField('Loja', coerce=int, validators=[DataRequired()])
    produto_id = SelectField('Produto', coerce=int, validators=[DataRequired()])
    quantidade = IntegerField('Quantidade', validators=[DataRequired(), NumberRange(min=1)])
    submit = SubmitField('Registrar Chegada')