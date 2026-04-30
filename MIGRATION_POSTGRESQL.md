# 🚀 Migração PostgreSQL para o Railway

Este guia mostra como executar a migração do PostgreSQL para adicionar as colunas de auditoria de produtos.

## Opção 1: Usando o Railway Dashboard (Recomendado)

### Passo 1: Acessar o Console PostgreSQL via Railway
1. Acesse o [Railway Dashboard](https://railway.app)
2. Selecione seu projeto **erp-motos**
3. Clique no plugin **PostgreSQL**
4. Vá para a aba **Query** (ou **Data**)

### Passo 2: Executar os comandos SQL

Cole e execute os seguintes comandos SQL **um por um**:

```sql
-- 1. Adicionar coluna deleted_by
ALTER TABLE produto ADD COLUMN deleted_by INTEGER;

-- 2. Adicionar coluna deleted_at
ALTER TABLE produto ADD COLUMN deleted_at TIMESTAMP;

-- 3. Adicionar coluna is_deleted (com valor padrão)
ALTER TABLE produto ADD COLUMN is_deleted BOOLEAN NOT NULL DEFAULT FALSE;

-- 4. Adicionar coluna created_by (com valor padrão = 1, admin)
ALTER TABLE produto ADD COLUMN created_by INTEGER NOT NULL DEFAULT 1;

-- 5. Adicionar foreign key para created_by
ALTER TABLE produto 
ADD CONSTRAINT fk_produto_created_by 
FOREIGN KEY (created_by) REFERENCES usuario(id);

-- 6. Adicionar foreign key para deleted_by
ALTER TABLE produto 
ADD CONSTRAINT fk_produto_deleted_by 
FOREIGN KEY (deleted_by) REFERENCES usuario(id);

-- 7. Verificar as colunas adicionadas
SELECT column_name, data_type, is_nullable 
FROM information_schema.columns 
WHERE table_name = 'produto' 
ORDER BY ordinal_position;
```

---

## Opção 2: Usando o Script Python (Se tiver conexão com Railway)

Se quiser executar o script automaticamente em produção:

### Passo 1: Copiar a variável DATABASE_URL do Railway

1. No Railway Dashboard, vá em seu projeto
2. Selecione o PostgreSQL
3. Copie a **DATABASE_URL** em "Connect"

### Passo 2: Executar o script localmente com a variável

```bash
# Setando a DATABASE_URL
export DATABASE_URL="postgresql://user:password@host:port/database"

# Executar a migração
python migrate_postgresql.py
```

### Passo 3: Ou usar via CLI do Railway

```bash
# Instalar Railway CLI (se não tiver)
npm install -g @railway/cli

# Login
railway login

# Conectar ao projeto
railway link

# Executar o script em produção
railway run python migrate_postgresql.py
```

---

## ✅ Verificação

Após executar, verifique se tudo está correto:

```sql
-- Contar produtos
SELECT COUNT(*) as total FROM produto;

-- Ver uma linha completa
SELECT * FROM produto LIMIT 1;

-- Verificar se created_by está preenchido
SELECT COUNT(*) as com_creator FROM produto WHERE created_by IS NOT NULL;
```

---

## 📊 O que foi adicionado

| Coluna | Tipo | Requerida | Descrição |
|--------|------|-----------|-----------|
| `created_by` | INTEGER | Sim | ID do usuário que criou o produto |
| `deleted_by` | INTEGER | Não | ID do usuário que deletou o produto |
| `deleted_at` | TIMESTAMP | Não | Data/hora da exclusão |
| `is_deleted` | BOOLEAN | Sim (DEFAULT: FALSE) | Flag de soft delete |

---

## 🔧 Troubleshooting

### Erro: "column already exists"
✓ Normal! Significa que a coluna já foi adicionada. Pule para a próxima.

### Erro de conexão
- Verifique a DATABASE_URL no Railway
- Confirme que o IP está autorizado (Railway geralmente permite automaticamente)

### Erro de Foreign Key
- Certifique-se de que a tabela `usuario` existe
- Verifique se o usuário com ID 1 existe

---

## 📝 Próximas passagens

Após a migração, o sistema automaticamente:
- ✅ Registra quem cria cada produto
- ✅ Registra quem e quando um produto é deletado
- ✅ Mantém histórico de exclusões
- ✅ Mostra página de histórico em `/produtos/historico`
