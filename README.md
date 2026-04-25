# 🏍️ Mobility ERP

Sistema de gestão para loja de motocicletas elétricas — Flask + PostgreSQL.

## 🏗️ Arquitetura Modular

O projeto foi refatorado para uma arquitetura modular organizada:

```
erp-motos/
├── app.py              # Aplicação principal (factory pattern)
├── config.py           # Configurações da aplicação
├── models.py           # Modelos do banco de dados
├── forms.py            # Formulários WTForms
├── auth.py             # Decorators de autenticação
├── utils.py            # Funções utilitárias
├── routes/             # Blueprints organizados por funcionalidade
│   ├── auth.py         # Rotas de login/logout
│   ├── main.py         # Dashboard e rotas principais
│   ├── usuarios.py     # Gestão de usuários
│   └── produtos.py     # Gestão de produtos
├── templates/          # Templates HTML
├── requirements.txt    # Dependências Python
├── runtime.txt         # Versão Python (Railway)
├── Procfile           # Configuração gunicorn
└── .env.example       # Exemplo de variáveis de ambiente
```

## Funcionalidades
- ✅ Login com senha criptografada (hash bcrypt via Werkzeug)
- ✅ Perfis de acesso: **admin**, **gerente**, **vendedor**
- ✅ Estoque de motos e peças com alerta de estoque mínimo
- ✅ Registro de vendas com controle de estoque automático
- ✅ Clientes (CRM básico)
- ✅ Financeiro: receitas e despesas por mês
- ✅ Dashboard com KPIs
- ✅ Gerenciamento de usuários (somente admin)

## Perfis de acesso

| Perfil    | Dashboard | Estoque | Vendas | Clientes | Financeiro | Usuários |
|-----------|-----------|---------|--------|----------|------------|----------|
| admin     | ✅        | ✅ + excluir | ✅  | ✅       | ✅ + excluir | ✅    |
| gerente   | ✅        | ✅      | ✅     | ✅       | ✅         | ❌       |
| vendedor  | ✅        | 👁️ ver  | ✅     | ✅       | ❌         | ❌       |

## 🚀 Como rodar localmente

```bash
# 1. Clone o repositório
git clone https://github.com/thiagoph1/erp-motos.git
cd erp-motos

# 2. Crie um ambiente virtual
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate

# 3. Instale as dependências
pip install -r requirements.txt

# 4. Configure o .env (copie o exemplo)
cp .env.example .env
# Edite o .env com uma SECRET_KEY segura

# 5. Execute
python app.py
```

Acesse: http://localhost:5000
Login padrão: `admin` / `Admin@123` *(troque após o primeiro acesso!)*

## 🐘 Deploy no Railway (PostgreSQL)

1. **Configure o projeto no Railway**:
   - Conecte seu repositório GitHub
   - Adicione PostgreSQL (Railway cria automaticamente)
   - Copie a `DATABASE_URL` gerada

2. **Configure variáveis de ambiente**:
   ```bash
   SECRET_KEY=sua-chave-super-segura-aqui
   DATABASE_URL=postgresql://user:pass@host:5432/railway
   ```

3. **Deploy automático**:
   - Railway detecta mudanças no GitHub
   - Instala dependências automaticamente
   - Usa PostgreSQL para produção

## 📊 Benefícios da Arquitetura Modular

- **Manutenibilidade**: Código organizado por responsabilidade
- **Escalabilidade**: Fácil adicionar novas funcionalidades
- **Testabilidade**: Cada módulo pode ser testado isoladamente
- **Reutilização**: Funções utilitárias compartilhadas
- **Legibilidade**: Código mais fácil de entender e navegar

## 🔧 Estrutura dos Módulos

### `config.py`
- Configurações Flask, SQLAlchemy, Flask-Login
- Definição de perfis e permissões

### `models.py`
- Definição de todas as tabelas do banco
- Relacionamentos e métodos dos modelos

### `forms.py`
- Todos os formulários WTForms
- Validações e campos dos formulários

### `auth.py`
- Decorators de permissão (`@requer_admin`, `@requer_gerente_ou_admin`)
- Funções de autorização

### `utils.py`
- Funções helper (formatação, cálculos, etc.)
- Lógica reutilizável

### `routes/`
- **auth.py**: Login, logout
- **main.py**: Dashboard, página inicial
- **usuarios.py**: CRUD de usuários
- **produtos.py**: CRUD de produtos

### `app.py`
- Factory pattern para criar aplicação
- Registro de blueprints e extensões
- Inicialização do banco e usuário admin
2. Acesse [render.com](https://render.com) → New Web Service
3. Conecte o repositório
4. Configure:
   - **Build Command**: `pip install -r requirements.txt`
   - **Start Command**: `gunicorn app:app`
5. Em **Environment Variables**, adicione:
   - `SECRET_KEY` = uma chave longa e aleatória
6. Clique em **Deploy**

## Estrutura do projeto

```
erp-motos/
├── app.py                # Aplicação Flask (modelos, rotas, formulários)
├── requirements.txt
├── Procfile              # Comando para o Render
├── .env.example          # Variáveis de ambiente (modelo)
├── .gitignore
└── templates/
    ├── base.html         # Layout com sidebar
    ├── login.html
    ├── index.html        # Dashboard
    ├── produtos.html
    ├── produto_form.html
    ├── usuarios.html
    └── usuario_form.html
```

## Segurança
- Senhas armazenadas com hash (Werkzeug `generate_password_hash`)
- CSRF protection via Flask-WTF em todos os formulários
- Controle de acesso por perfil com decorator `@requer_perfil`
- `SECRET_KEY` carregada de variável de ambiente
- `.env` e banco de dados no `.gitignore`