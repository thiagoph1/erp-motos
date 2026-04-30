"""
Script de migração para adicionar colunas de auditoria à tabela produto
Adiciona: created_by, deleted_by, deleted_at, is_deleted
"""
from app import create_app
from models import db, Produto, Usuario
from sqlalchemy import text

def migrate():
    """Executa a migração"""
    app = create_app()
    
    with app.app_context():
        try:
            # Obter o primeiro usuário (admin) para usar como created_by padrão
            admin = Usuario.query.first()
            if not admin:
                print("❌ Erro: Nenhum usuário encontrado. Crie um usuário admin primeiro.")
                return False
            
            print(f"✓ Usando usuário '{admin.nome}' (ID: {admin.id}) como padrão para produtos existentes")
            
            # Executar alterações no banco de dados
            with db.engine.connect() as conn:
                # Adicionar coluna created_by se não existir
                try:
                    conn.execute(text("""
                        ALTER TABLE produto 
                        ADD COLUMN created_by INTEGER NOT NULL DEFAULT :admin_id;
                    """), {"admin_id": admin.id})
                    conn.commit()
                    print("✓ Coluna 'created_by' adicionada com sucesso")
                except Exception as e:
                    if "already exists" in str(e):
                        print("✓ Coluna 'created_by' já existe")
                    else:
                        print(f"⚠ Erro ao adicionar 'created_by': {e}")
                
                # Adicionar coluna deleted_by se não existir
                try:
                    conn.execute(text("""
                        ALTER TABLE produto 
                        ADD COLUMN deleted_by INTEGER;
                    """))
                    conn.commit()
                    print("✓ Coluna 'deleted_by' adicionada com sucesso")
                except Exception as e:
                    if "already exists" in str(e):
                        print("✓ Coluna 'deleted_by' já existe")
                    else:
                        print(f"⚠ Erro ao adicionar 'deleted_by': {e}")
                
                # Adicionar coluna deleted_at se não existir
                try:
                    conn.execute(text("""
                        ALTER TABLE produto 
                        ADD COLUMN deleted_at TIMESTAMP;
                    """))
                    conn.commit()
                    print("✓ Coluna 'deleted_at' adicionada com sucesso")
                except Exception as e:
                    if "already exists" in str(e):
                        print("✓ Coluna 'deleted_at' já existe")
                    else:
                        print(f"⚠ Erro ao adicionar 'deleted_at': {e}")
                
                # Adicionar coluna is_deleted se não existir
                try:
                    conn.execute(text("""
                        ALTER TABLE produto 
                        ADD COLUMN is_deleted BOOLEAN NOT NULL DEFAULT FALSE;
                    """))
                    conn.commit()
                    print("✓ Coluna 'is_deleted' adicionada com sucesso")
                except Exception as e:
                    if "already exists" in str(e):
                        print("✓ Coluna 'is_deleted' já existe")
                    else:
                        print(f"⚠ Erro ao adicionar 'is_deleted': {e}")
                
                # Adicionar constraints de foreign key se não existirem
                try:
                    conn.execute(text("""
                        ALTER TABLE produto 
                        ADD CONSTRAINT fk_produto_created_by 
                        FOREIGN KEY (created_by) REFERENCES usuario(id);
                    """))
                    conn.commit()
                    print("✓ Foreign key 'created_by' adicionada")
                except Exception as e:
                    if "already exists" in str(e) or "unique violation" in str(e):
                        print("✓ Foreign key 'created_by' já existe")
                    else:
                        print(f"⚠ Erro ao adicionar FK 'created_by': {e}")
                
                try:
                    conn.execute(text("""
                        ALTER TABLE produto 
                        ADD CONSTRAINT fk_produto_deleted_by 
                        FOREIGN KEY (deleted_by) REFERENCES usuario(id);
                    """))
                    conn.commit()
                    print("✓ Foreign key 'deleted_by' adicionada")
                except Exception as e:
                    if "already exists" in str(e) or "unique violation" in str(e):
                        print("✓ Foreign key 'deleted_by' já existe")
                    else:
                        print(f"⚠ Erro ao adicionar FK 'deleted_by': {e}")
            
            print("\n✅ Migração concluída com sucesso!")
            return True
            
        except Exception as e:
            print(f"\n❌ Erro durante a migração: {e}")
            import traceback
            traceback.print_exc()
            return False

if __name__ == '__main__':
    migrate()
