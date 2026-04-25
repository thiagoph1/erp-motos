# 🚀 Guia de Migração: Render → Railway com PostgreSQL

## Passo 1: Preparar no Railway

### 1.1 Criar um novo projeto
1. Acesse [railway.app](https://railway.app)
2. Clique em "Start a New Project"
3. Selecione "Deploy from GitHub repo"
4. Conecte seu repositório GitHub com o código ERP

### 1.2 Adicionar PostgreSQL
1. No painel do projeto Railway, clique em "Add"
2. Selecione "PostgreSQL"
3. Railway vai criar automaticamente o banco e gerar as credenciais

### 1.3 Copiar DATABASE_URL
1. Abra a aba do PostgreSQL no painel
2. Vá em "Variables" → localize `DATABASE_URL`
3. Copie a URL completa (algo como: `postgresql://user:pass@host:port/railway`)

---

## Passo 2: Configurar o Código Localmente

### 2.1 Instalar dependências
```bash
pip install -r requirements.txt
```
Isso vai instalar o `psycopg2-binary` (driver PostgreSQL para Python).

### 2.2 Criar arquivo .env com dados do Railway
```bash
# Edite o arquivo .env
SECRET_KEY=sua-chave-segura-aqui
DATABASE_URL=postgresql://user:password@host:5432/railway
```
Cole a `DATABASE_URL` que copiou do Railway.

### 2.3 (Opcional) Migrar dados do SQLite

Se você tem dados no SQLite que quer preservar:

```bash
# 1. Exportar dados do SQLite local
python migrate_db.py export
# Isso cria um arquivo export_sqlite.json

# 2. Configurar DATABASE_URL para PostgreSQL no .env

# 3. Importar para PostgreSQL
python migrate_db.py
```

Se não tem dados para preservar, pode pular isso.

---

## Passo 3: Configurar no Railway (via dashboard)

### 3.1 Variáveis de ambiente
1. No painel Railway, clique no seu serviço Flask
2. Vá em "Variables"
3. Adicione/configure:
   ```
   SECRET_KEY=sua-chave-segura-aqui
   DATABASE_URL=postgresql://user:password@host:5432/railway
   ```

### 3.2 (Opcional) Configurar inicialização do banco
Se quiser criar automaticamente as tabelas ao fazer deploy:
- O código já faz isso: `db.create_all()` + `seed_inicial()` rodamautomaticamente

---

## Passo 4: Deploy

### 4.1 Push do código
```bash
git add .
git commit -m "Migrate: SQLite → PostgreSQL for Railway"
git push origin main
```

### 4.2 Railway processa automaticamente
- Detecta que é Python + Flask
- Instala requirements.txt
- Roda o app em produção com gunicorn
- Cria as tabelas do PostgreSQL automaticamente
- Cria usuário admin padrão

---

## Verificação Pós-Deploy

1. Acesse a URL do seu app no Railway (algo como `https://seu-app.railway.app`)
2. Faça login com:
   - **Usuário**: `admin`
   - **Senha**: `Admin@123`
3. ✅ Se funcionar, migração bem-sucedida!

---

## 🚨 Troubleshooting

### "could not connect to database"
- Verifique se `DATABASE_URL` está correto nas variáveis do Railway
- Teste localmente com essas credenciais

### "relation does not exist"
- Railway pode ter criado o banco mas faltaram as tabelas
- Esta URL de conexão: `python app.py` localmente deveria resolver

### Versão diferente de Python
- Railway usa Python 3.11+ (compatível com seu código)
- Se precisar de versão específica, crie um arquivo `runtime.txt` com: `python-3.11.0`

---

## 📊 Benefícios dessa migração

| Aspecto | SQLite | PostgreSQL (Railway) |
|---------|--------|-----------------|
| **Concorrência** | ❌ Limitada | ✅ Excelente |
| **Backup** | Manual | ✅ Automático |
| **Escalabilidade** | ❌ Limitada | ✅ Escalável |
| **Disponibilidade** | 🟡 Médio | ✅ 99.9% uptime |
| **Segurança** | 🟡 Média | ✅ Enterprise-grade |

---

## 🔐 Dados de exemplo no novo banco

Após deploy, terá:

| Campo | Valor |
|-------|-------|
| **Usuário Admin** | `admin` |
| **Senha Admin** | `Admin@123` |
| **URL da App** | https://seu-app.railway.app |

**⚠️ Mude a senha do admin na primeira vez que logar!**

---

## Próximas melhorias (opcional)

- [ ] Adicionar backup automático (Railway oferece)
- [ ] Configurar HTTPS (Railway faz automaticamente)
- [ ] Adicionar monitoring
- [ ] Configurar alertas de erro
