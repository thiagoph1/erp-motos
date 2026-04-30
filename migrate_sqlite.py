"""
Script de migração para SQLite - adiciona colunas de auditoria à tabela produto
"""
from app import create_app
from models import db, Usuario
from sqlalchemy import text

def migrate_sqlite():
    """Executa a migração para SQLite"""
    app = create_app()
    
    with app.app_context():
        try:
            # Obter o primeiro usuário (admin)
            admin = Usuario.query.first()
            if not admin:
                print("❌ Erro: Nenhum usuário encontrado.")
                return False
            
            print(f"✓ Usando usuário '{admin.nome}' (ID: {admin.id}) como padrão")
            
            with db.engine.begin() as conn:
                # Para SQLite, precisamos de uma abordagem diferente
                # Primeiro, verificar se a coluna já existe
                
                # Nota: SQLite não tem um descapi direto para verificar colunas
                # Vamos tentar criar a coluna e capturar o erro se já existir
                
                try:
                    # Adicionar created_by (SEM DEFAULT com parametro)
                    conn.execute(text("ALTER TABLE produto ADD COLUMN created_by INTEGER"))
                    print("✓ Coluna 'created_by' adicionada")
                except Exception as e:
                    if "duplicate column" in str(e):
                        print("✓ Coluna 'created_by' já existe")
                    else:
                        raise
                
                # Agora atualizar os valores existentes
                conn.execute(text(f"UPDATE produto SET created_by = {admin.id} WHERE created_by IS NULL"))
                print(f"✓ Produtos existentes atualizados com created_by = {admin.id}")
                
            print("\n✅ Migração SQLite concluída com sucesso!")
            return True
            
        except Exception as e:
            print(f"\n❌ Erro durante a migração: {e}")
            import traceback
            traceback.print_exc()
            return False

if __name__ == '__main__':
    migrate_sqlite()
