from datetime import datetime

class Vendedor:
    def __init__(self, db):
        self.db = db
    
    def adicionar(self, nome_vendedor):
        try:
            self.db.cursor.execute('''
                INSERT INTO vendedores (nome_vendedor, data_cadastro)
                VALUES (?, ?)
            ''', (nome_vendedor, datetime.now().isoformat()))
            self.db.conexao.commit()
            return True, "Vendedor adicionado com sucesso!"
        except Exception as e:
            return False, f"Erro ao adicionar vendedor: {str(e)}"
    
    def atualizar(self, id, nome_vendedor):
        try:
            self.db.cursor.execute('''
                UPDATE vendedores SET nome_vendedor=?
                WHERE id=?
            ''', (nome_vendedor, id))
            self.db.conexao.commit()
            return True, "Vendedor atualizado com sucesso!"
        except Exception as e:
            return False, f"Erro ao atualizar vendedor: {str(e)}"
    
    def deletar(self, id):
        try:
            self.db.cursor.execute('DELETE FROM vendedores WHERE id=?', (id,))
            self.db.conexao.commit()
            return True, "Vendedor deletado com sucesso!"
        except Exception as e:
            return False, f"Erro ao deletar vendedor: {str(e)}"
    
    def listar(self):
        self.db.cursor.execute('SELECT * FROM vendedores')
        return self.db.cursor.fetchall()
    
    def buscar_por_id(self, id):
        self.db.cursor.execute('SELECT * FROM vendedores WHERE id=?', (id,))
        return self.db.cursor.fetchone()
