# moto-chefe-ERP
Sistema de ERP da Moto Chefe

## Descrição
Sistema ERP simples para administrar uma loja de motocicletas elétricas, desenvolvido em Python com Flask e SQLite.

## Funcionalidades
- Autenticação de usuários
- Gerenciamento de produtos (CRUD)
- Gerenciamento de clientes (em desenvolvimento)
- Registro de vendas (em desenvolvimento)

## Como executar
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

## Hospedagem
Para hospedar gratuitamente:
- **Render**: Faça upload do código no GitHub e conecte ao Render
- **Railway**: Similar ao Render, suporta Python
- **Heroku**: Plataforma clássica para apps Python

## Estrutura do projeto
- `app.py`: Aplicação principal Flask
- `templates/`: Templates HTML
- `erp_motos.db`: Banco de dados SQLite (criado automaticamente)
- `requirements.txt`: Dependências Python
