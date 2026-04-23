# moto-chefe-ERP
Sistema de ERP da Moto Chefe

## Descrição
Sistema ERP simples para administrar uma loja de motocicletas elétricas, desenvolvido em Python com Flask e SQLite.

## Funcionalidades
- Autenticação de usuários
- Gerenciamento de produtos (CRUD)
- Gerenciamento de clientes (em desenvolvimento)
- Registro de vendas (em desenvolvimento)

## Como executar localmente
1. Instale as dependências:
   ```
   pip install -r requirements.txt
   ```

2. Execute o aplicativo:
   ```
   python app.py
   ```

3. Acesse http://localhost:5000 no navegador

4. Faça login com usuário: admin, senha: admin123

## Hospedagem no Render
1. **Faça push do código para GitHub**:
   ```
   git add .
   git commit -m "Preparar para deploy no Render"
   git push origin main
   ```

2. **Acesse o Render** (https://render.com) e faça login

3. **Crie um novo Web Service**:
   - Conecte seu repositório GitHub
   - Selecione o repositório `erp-motos`
   - Configure:
     - **Runtime**: Python 3
     - **Build Command**: `pip install -r requirements.txt`
     - **Start Command**: `gunicorn app:app`
   - **Environment Variables**: Adicione `SECRET_KEY` com uma chave segura

4. **Deploy**: O Render fará o build e deploy automaticamente

5. **Acesse sua URL**: O Render fornecerá uma URL gratuita (ex: https://erp-motos.onrender.com)

## Estrutura do projeto
- `app.py`: Aplicação principal Flask
- `templates/`: Templates HTML
- `erp_motos.db`: Banco de dados SQLite (criado automaticamente)
- `requirements.txt`: Dependências Python
- `Procfile`: Comando de start para Render
