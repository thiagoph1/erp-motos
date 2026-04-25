# 🏍️ Moto Chefe ERP

Sistema de gestão para loja de motocicletas elétricas — Flask + SQLite.

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

## Como rodar localmente

```bash
# 1. Clone o repositório
git clone https://github.com/seu-usuario/moto-chefe-ERP.git
cd moto-chefe-ERP

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

## Deploy no Render.com (gratuito)

1. Faça push para o GitHub
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
moto-chefe-ERP/
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