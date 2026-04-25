"""
Script de Migração: SQLite → PostgreSQL
========================================

Este script ajuda a:
1. Exportar dados do SQLite local
2. Importar para PostgreSQL no Railway

Uso:
  python migrate_db.py
"""

import os
import json
from datetime import datetime
from app import app, db, Usuario, Produto, Cliente, Venda, ItemVenda, Lancamento

def export_sqlite_data():
    """Exporta dados do SQLite para JSON"""
    print("📤 Exportando dados do SQLite...")
    
    data = {
        'usuarios': [],
        'produtos': [],
        'clientes': [],
        'vendas': [],
        'itens_venda': [],
        'lancamentos': []
    }
    
    with app.app_context():
        # Exportar usuários
        for user in Usuario.query.all():
            data['usuarios'].append({
                'id': user.id,
                'nome': user.nome,
                'username': user.username,
                'email': user.email,
                'senha_hash': user.senha_hash,
                'perfil': user.perfil,
                'ativo': user.ativo,
                'criado_em': user.criado_em.isoformat() if user.criado_em else None
            })
        
        # Exportar produtos
        for prod in Produto.query.all():
            data['produtos'].append({
                'id': prod.id,
                'nome': prod.nome,
                'tipo': prod.tipo,
                'marca': prod.marca,
                'modelo': prod.modelo,
                'descricao': prod.descricao,
                'preco_custo': prod.preco_custo,
                'preco_venda': prod.preco_venda,
                'quantidade': prod.quantidade,
                'estoque_minimo': prod.estoque_minimo,
                'criado_em': prod.criado_em.isoformat() if prod.criado_em else None
            })
        
        # Exportar clientes
        for cli in Cliente.query.all():
            data['clientes'].append({
                'id': cli.id,
                'nome': cli.nome,
                'cpf': cli.cpf,
                'telefone': cli.telefone,
                'email': cli.email,
                'endereco': cli.endereco,
                'criado_em': cli.criado_em.isoformat() if cli.criado_em else None
            })
        
        # Exportar vendas
        for vnd in Venda.query.all():
            data['vendas'].append({
                'id': vnd.id,
                'cliente_id': vnd.cliente_id,
                'usuario_id': vnd.usuario_id,
                'total': vnd.total,
                'status': vnd.status,
                'criado_em': vnd.criado_em.isoformat() if vnd.criado_em else None
            })
        
        # Exportar itens de venda
        for item in ItemVenda.query.all():
            data['itens_venda'].append({
                'id': item.id,
                'venda_id': item.venda_id,
                'produto_id': item.produto_id,
                'quantidade': item.quantidade,
                'preco_unitario': item.preco_unitario
            })
        
        # Exportar lançamentos
        for lanc in Lancamento.query.all():
            data['lancamentos'].append({
                'id': lanc.id,
                'descricao': lanc.descricao,
                'tipo': lanc.tipo,
                'valor': lanc.valor,
                'data': lanc.data.isoformat() if lanc.data else None,
                'criado_em': lanc.criado_em.isoformat() if lanc.criado_em else None
            })
    
    # Salvar em arquivo
    with open('export_sqlite.json', 'w') as f:
        json.dump(data, f, indent=2, default=str)
    
    print(f"✅ Dados exportados em export_sqlite.json")
    print(f"   - {len(data['usuarios'])} usuários")
    print(f"   - {len(data['produtos'])} produtos")
    print(f"   - {len(data['clientes'])} clientes")
    print(f"   - {len(data['vendas'])} vendas")

def import_postgresql_data():
    """Importa dados do JSON para PostgreSQL"""
    if not os.path.exists('export_sqlite.json'):
        print("❌ Arquivo export_sqlite.json não encontrado!")
        print("   Execute primeiro: python migrate_db.py export")
        return
    
    print("📥 Importando dados para PostgreSQL...")
    
    with open('export_sqlite.json', 'r') as f:
        data = json.load(f)
    
    with app.app_context():
        try:
            # Importar usuários
            for udata in data['usuarios']:
                user = Usuario(
                    nome=udata['nome'],
                    username=udata['username'],
                    email=udata['email'],
                    perfil=udata['perfil'],
                    ativo=udata['ativo']
                )
                user.senha_hash = udata['senha_hash']
                db.session.add(user)
            
            db.session.commit()
            print(f"✅ {len(data['usuarios'])} usuários importados")
            
            # Importar produtos
            for pdata in data['produtos']:
                prod = Produto(
                    nome=pdata['nome'],
                    tipo=pdata['tipo'],
                    marca=pdata['marca'],
                    modelo=pdata['modelo'],
                    descricao=pdata['descricao'],
                    preco_custo=pdata['preco_custo'],
                    preco_venda=pdata['preco_venda'],
                    quantidade=pdata['quantidade'],
                    estoque_minimo=pdata['estoque_minimo']
                )
                db.session.add(prod)
            
            db.session.commit()
            print(f"✅ {len(data['produtos'])} produtos importados")
            
            # Importar clientes
            for cdata in data['clientes']:
                cli = Cliente(
                    nome=cdata['nome'],
                    cpf=cdata['cpf'],
                    telefone=cdata['telefone'],
                    email=cdata['email'],
                    endereco=cdata['endereco']
                )
                db.session.add(cli)
            
            db.session.commit()
            print(f"✅ {len(data['clientes'])} clientes importados")
            
            # Importar vendas
            for vdata in data['vendas']:
                vnd = Venda(
                    cliente_id=vdata['cliente_id'],
                    usuario_id=vdata['usuario_id'],
                    total=vdata['total'],
                    status=vdata['status']
                )
                db.session.add(vnd)
            
            db.session.commit()
            print(f"✅ {len(data['vendas'])} vendas importadas")
            
            # Importar itens de venda
            for idata in data['itens_venda']:
                item = ItemVenda(
                    venda_id=idata['venda_id'],
                    produto_id=idata['produto_id'],
                    quantidade=idata['quantidade'],
                    preco_unitario=idata['preco_unitario']
                )
                db.session.add(item)
            
            db.session.commit()
            print(f"✅ {len(data['itens_venda'])} itens de venda importados")
            
            # Importar lançamentos
            for ldata in data['lancamentos']:
                lanc = Lancamento(
                    descricao=ldata['descricao'],
                    tipo=ldata['tipo'],
                    valor=ldata['valor'],
                    data=datetime.fromisoformat(ldata['data']) if ldata['data'] else None
                )
                db.session.add(lanc)
            
            db.session.commit()
            print(f"✅ {len(data['lancamentos'])} lançamentos importados")
            
            print("\n✅ MIGRAÇÃO CONCLUÍDA COM SUCESSO!")
            
        except Exception as e:
            db.session.rollback()
            print(f"❌ Erro na importação: {e}")

if __name__ == '__main__':
    import sys
    
    if len(sys.argv) > 1 and sys.argv[1] == 'export':
        export_sqlite_data()
    else:
        print("Migração SQLite → PostgreSQL")
        print("=" * 40)
        print("\nOpções:")
        print("  python migrate_db.py export  → Exporta dados do SQLite")
        print("  python migrate_db.py          → Importa dados para PostgreSQL")
        print("\nPasso a passo:")
        print("1. python migrate_db.py export")
        print("2. Configure DATABASE_URL no .env para PostgreSQL")
        print("3. python migrate_db.py")
