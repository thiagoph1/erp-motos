"""
Script de migração para PostgreSQL - adiciona colunas de auditoria à tabela produto
Use este script para atualizar o banco PostgreSQL no Railway
"""
from app import create_app
from models import db, Usuario
from sqlalchemy import text
import sys

def migrate_postgresql():
    """Executa a migração para PostgreSQL"""
    app = create_app()
    
    with app.app_context():
        try:
            # Obter o primeiro usuário (admin)
            admin = Usuario.query.first()
            if not admin:
                print("❌ Erro: Nenhum usuário encontrado.")
                return False
            
            print(f"🔄 Iniciando migração para PostgreSQL...")
            print(f"✓ Usando usuário '{admin.nome}' (ID: {admin.id}) como padrão\n")
            
            with db.engine.begin() as conn:
                
                # 1. Adicionar deleted_by se não existir
                try:
                    conn.execute(text("""
                        ALTER TABLE produto 
                        ADD COLUMN deleted_by INTEGER;
                    """))
                    print("✓ Coluna 'deleted_by' adicionada com sucesso")
                except Exception as e:
                    if "already exists" in str(e) or "duplicate column" in str(e):
                        print("✓ Coluna 'deleted_by' já existe")
                    else:
                        print(f"⚠ Erro ao adicionar 'deleted_by': {e}")
                
                # 2. Adicionar deleted_at se não existir
                try:
                    conn.execute(text("""
                        ALTER TABLE produto 
                        ADD COLUMN deleted_at TIMESTAMP;
                    """))
                    print("✓ Coluna 'deleted_at' adicionada com sucesso")
                except Exception as e:
                    if "already exists" in str(e) or "duplicate column" in str(e):
                        print("✓ Coluna 'deleted_at' já existe")
                    else:
                        print(f"⚠ Erro ao adicionar 'deleted_at': {e}")
                
                # 3. Adicionar is_deleted se não existir
                try:
                    conn.execute(text("""
                        ALTER TABLE produto 
                        ADD COLUMN is_deleted BOOLEAN NOT NULL DEFAULT FALSE;
                    """))
                    print("✓ Coluna 'is_deleted' adicionada com sucesso")
                except Exception as e:
                    if "already exists" in str(e) or "duplicate column" in str(e):
                        print("✓ Coluna 'is_deleted' já existe")
                    else:
                        print(f"⚠ Erro ao adicionar 'is_deleted': {e}")
                
                # 4. Adicionar created_by se não existir
                try:
                    conn.execute(text(f"""
                        ALTER TABLE produto 
                        ADD COLUMN created_by INTEGER NOT NULL DEFAULT {admin.id};
                    """))
                    print("✓ Coluna 'created_by' adicionada com sucesso")
                except Exception as e:
                    if "already exists" in str(e) or "duplicate column" in str(e):
                        print("✓ Coluna 'created_by' já existe")
                    else:
                        print(f"⚠ Erro ao adicionar 'created_by': {e}")
                
                # 5. Adicionar constraint de foreign key para created_by
                try:
                    conn.execute(text("""
                        ALTER TABLE produto 
                        ADD CONSTRAINT fk_produto_created_by 
                        FOREIGN KEY (created_by) REFERENCES usuario(id);
                    """))
                    print("✓ Foreign key 'created_by' adicionada com sucesso")
                except Exception as e:
                    if "already exists" in str(e) or "duplicate" in str(e):
                        print("✓ Foreign key 'created_by' já existe")
                    else:
                        print(f"⚠ Aviso ao adicionar FK 'created_by': {e}")
                
                # 6. Adicionar constraint de foreign key para deleted_by
                try:
                    conn.execute(text("""
                        ALTER TABLE produto 
                        ADD CONSTRAINT fk_produto_deleted_by 
                        FOREIGN KEY (deleted_by) REFERENCES usuario(id);
                    """))
                    print("✓ Foreign key 'deleted_by' adicionada com sucesso")
                except Exception as e:
                    if "already exists" in str(e) or "duplicate" in str(e):
                        print("✓ Foreign key 'deleted_by' já existe")
                    else:
                        print(f"⚠ Aviso ao adicionar FK 'deleted_by': {e}")
                
                # 7. Atualizar ANY null created_by values (by na chance some exist)
                result = conn.execute(text(f"""
                    UPDATE produto 
                    SET created_by = {admin.id} 
                    WHERE created_by IS NULL;
                """))
                rows_updated = result.rowcount
                if rows_updated > 0:
                    print(f"✓ {rows_updated} produtos atualizados com created_by padrão")
            
            print("\n✅ Migração PostgreSQL concluída com sucesso!")
            print("\n📋 Resumo das mudanças:")
            print("  - Coluna 'created_by' (Integer, NOT NULL)")
            print("  - Coluna 'deleted_by' (Integer, nullable)")
            print("  - Coluna 'deleted_at' (Timestamp, nullable)")
            print("  - Coluna 'is_deleted' (Boolean, DEFAULT FALSE)")
            print("  - Foreign keys configuradas")
            return True
            
        except Exception as e:
            print(f"\n❌ Erro durante a migração: {e}")
            import traceback
            traceback.print_exc()
            return False

if __name__ == '__main__':
    success = migrate_postgresql()
    sys.exit(0 if success else 1)
