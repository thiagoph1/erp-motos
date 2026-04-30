"""
Script para atualizar produtos existentes com created_by padrão
"""
from app import create_app
from models import db, Produto, Usuario

def update_existing_products():
    """Atualiza produtos existentes com created_by"""
    app = create_app()
    
    with app.app_context():
        try:
            # Obter o primeiro usuário (admin)
            admin = Usuario.query.first()
            if not admin:
                print("❌ Erro: Nenhum usuário encontrado.")
                return False
            
            # Contar produtos sem created_by
            produtos_sem_creator = Produto.query.filter(
                (Produto.created_by == None) | (Produto.created_by == 0)
            ).count()
            
            if produtos_sem_creator > 0:
                print(f"Atualizando {produtos_sem_creator} produtos sem created_by...")
                
                # Atualizar todos os produtos
                Produto.query.filter(
                    (Produto.created_by == None) | (Produto.created_by == 0)
                ).update({Produto.created_by: admin.id})
                
                db.session.commit()
                print(f"✓ {produtos_sem_creator} produtos atualizados")
            else:
                print("✓ Todos os produtos já possuem created_by")
            
            # Verificar se há produtos com valores nulos
            total = Produto.query.count()
            print(f"\n✅ Total de produtos: {total}")
            
            return True
            
        except Exception as e:
            print(f"❌ Erro: {e}")
            import traceback
            traceback.print_exc()
            return False

if __name__ == '__main__':
    update_existing_products()
