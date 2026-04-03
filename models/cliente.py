from datetime import datetime

class Cliente:
    def __init__(self, db):
        self.db = db
    
    def adicionar(self, nome, email, telefone, endereco):
        try:
            self.db.cursor.execute('''
                INSERT INTO clientes (nome, email, telefone, endereco, data_cadastro)
                VALUES (?, ?, ?, ?, ?)
            ''', (nome, email, telefone, endereco, datetime.now().isoformat()))
            self.db.conexao.commit()
            return True, "Cliente adicionado com sucesso!"
        except Exception as e:
            return False, f"Erro ao adicionar cliente: {str(e)}"
    
    def atualizar(self, id, nome, email, telefone, endereco):
        try:
            self.db.cursor.execute('''
                UPDATE clientes SET nome=?, email=?, telefone=?, endereco=?
                WHERE id=?
            ''', (nome, email, telefone, endereco, id))
            self.db.conexao.commit()
            return True, "Cliente atualizado com sucesso!"
        except Exception as e:
            return False, f"Erro ao atualizar cliente: {str(e)}"
    
    def deletar(self, id):
        try:
            self.db.cursor.execute('DELETE FROM clientes WHERE id=?', (id,))
            self.db.conexao.commit()
            return True, "Cliente deletado com sucesso!"
        except Exception as e:
            return False, f"Erro ao deletar cliente: {str(e)}"
    
    def listar(self):
        self.db.cursor.execute('SELECT * FROM clientes')
        return self.db.cursor.fetchall()
    
    def buscar_por_id(self, id):
        self.db.cursor.execute('SELECT * FROM clientes WHERE id=?', (id,))
        return self.db.cursor.fetchone()
