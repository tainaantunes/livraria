from datetime import datetime

class Fornecedor:
    def __init__(self, db):
        self.db = db
    
    def adicionar(self, nome, cnpj, email, telefone, endereco):
        try:
            self.db.cursor.execute('''
                INSERT INTO fornecedores (nome, cnpj, email, telefone, endereco, data_cadastro)
                VALUES (?, ?, ?, ?, ?, ?)
            ''', (nome, cnpj, email, telefone, endereco, datetime.now().isoformat()))
            self.db.conexao.commit()
            return True, "Fornecedor adicionado com sucesso!"
        except Exception as e:
            return False, f"Erro ao adicionar fornecedor: {str(e)}"
    
    def atualizar(self, id, nome, cnpj, email, telefone, endereco):
        try:
            self.db.cursor.execute('''
                UPDATE fornecedores SET nome=?, cnpj=?, email=?, telefone=?, endereco=?
                WHERE id=?
            ''', (nome, cnpj, email, telefone, endereco, id))
            self.db.conexao.commit()
            return True, "Fornecedor atualizado com sucesso!"
        except Exception as e:
            return False, f"Erro ao atualizar fornecedor: {str(e)}"
    
    def deletar(self, id):
        try:
            self.db.cursor.execute('DELETE FROM fornecedores WHERE id=?', (id,))
            self.db.conexao.commit()
            return True, "Fornecedor deletado com sucesso!"
        except Exception as e:
            return False, f"Erro ao deletar fornecedor: {str(e)}"
    
    def listar(self):
        self.db.cursor.execute('SELECT * FROM fornecedores')
        return self.db.cursor.fetchall()
    
    def buscar_por_id(self, id):
        self.db.cursor.execute('SELECT * FROM fornecedores WHERE id=?', (id,))
        return self.db.cursor.fetchone()
