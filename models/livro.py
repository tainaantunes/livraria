from datetime import datetime

class Livro:
    def __init__(self, db):
        self.db = db
    
    def adicionar(self, titulo, autor, isbn, quantidade, preco_compra, preco_venda, espirito, fornecedor_id):
        try:
            self.db.cursor.execute('''
                INSERT INTO livros (titulo, autor, isbn, quantidade, preco_compra, preco_venda, espirito, fornecedor_id, data_cadastro)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
            ''', (titulo, autor, isbn, int(quantidade), float(preco_compra), float(preco_venda), espirito, int(fornecedor_id) if fornecedor_id else None, datetime.now().isoformat()))
            self.db.conexao.commit()
            return True, "Livro adicionado com sucesso!"
        except Exception as e:
            return False, f"Erro ao adicionar livro: {str(e)}"
    
    def atualizar(self, id, titulo, autor, isbn, quantidade, preco_compra, preco_venda, espirito, fornecedor_id):
        try:
            self.db.cursor.execute('''
                UPDATE livros SET titulo=?, autor=?, isbn=?, quantidade=?, preco_compra=?, preco_venda=?, espirito=?, fornecedor_id=?
                WHERE id=?
            ''', (titulo, autor, isbn, int(quantidade), float(preco_compra), float(preco_venda), espirito, int(fornecedor_id) if fornecedor_id else None, id))
            self.db.conexao.commit()
            return True, "Livro atualizado com sucesso!"
        except Exception as e:
            return False, f"Erro ao atualizar livro: {str(e)}"
    
    def deletar(self, id):
        try:
            self.db.cursor.execute('DELETE FROM livros WHERE id=?', (id,))
            self.db.conexao.commit()
            return True, "Livro deletado com sucesso!"
        except Exception as e:
            return False, f"Erro ao deletar livro: {str(e)}"
    
    def listar(self):
        self.db.cursor.execute('''
            SELECT l.id, l.titulo, l.autor, l.espirito, l.isbn, l.quantidade, l.preco_compra, l.preco_venda, COALESCE(f.nome, 'N/A') FROM livros l
            LEFT JOIN fornecedores f ON l.fornecedor_id = f.id
        ''')
        return self.db.cursor.fetchall()
    
    def buscar_por_id(self, id):
        self.db.cursor.execute('SELECT * FROM livros WHERE id=?', (id,))
        return self.db.cursor.fetchone()
    
    def buscar_por_nome_isbn(self, termo):
        """Busca livros que correspondem ao nome ou ISBN"""
        termo_busca = f"%{termo}%"
        self.db.cursor.execute('''
            SELECT l.id, l.titulo, l.isbn, l.autor, l.espirito, l.quantidade, l.preco_compra, l.preco_venda, l.fornecedor_id, COALESCE(f.nome, 'N/A')
            FROM livros l
            LEFT JOIN fornecedores f ON l.fornecedor_id = f.id
            WHERE LOWER(l.titulo) LIKE LOWER(?) OR LOWER(l.isbn) LIKE LOWER(?)
            ORDER BY l.titulo
        ''', (termo_busca, termo_busca))
        return self.db.cursor.fetchall()
    
    def buscar_exato_isbn(self, isbn):
        """Busca um livro específico pelo ISBN exato"""
        self.db.cursor.execute('''
            SELECT l.id, l.titulo, l.isbn, l.autor, l.espirito, l.quantidade, l.preco_compra, l.preco_venda, l.fornecedor_id, COALESCE(f.nome, 'N/A')
            FROM livros l
            LEFT JOIN fornecedores f ON l.fornecedor_id = f.id
            WHERE LOWER(l.isbn) = LOWER(?)
        ''', (isbn,))
        return self.db.cursor.fetchone()

    def atualizar_quantidade_por_id(self, id, quantidade):
        try:
            self.db.cursor.execute('UPDATE livros SET quantidade=? WHERE id=?', (int(quantidade), id))
            self.db.conexao.commit()
            return True, "Quantidade atualizada com sucesso!"
        except Exception as e:
            return False, f"Erro ao atualizar quantidade: {str(e)}"

    def registrar_historico_inventario(self, livro_id, isbn, titulo, operacao, quantidade, saldo_anterior, saldo_posterior, usuario=None):
        try:
            self.db.cursor.execute('''
                INSERT INTO inventario_historico (livro_id, isbn, titulo, operacao, quantidade, saldo_anterior, saldo_posterior, usuario, data)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
            ''', (livro_id, isbn, titulo, operacao, int(quantidade), int(saldo_anterior), int(saldo_posterior), usuario or 'sistema', datetime.now().isoformat()))
            self.db.conexao.commit()
            return True, "Histórico de inventário registrado."
        except Exception as e:
            return False, f"Erro ao registrar histórico de inventário: {str(e)}"

    def listar_historico_inventario(self):
        self.db.cursor.execute('''
            SELECT id, livro_id, isbn, titulo, operacao, quantidade, saldo_anterior, saldo_posterior, usuario, data
            FROM inventario_historico
            ORDER BY data DESC
        ''')
        return self.db.cursor.fetchall()

    def adicionar_item_inventario_temp(self, livro_id, isbn, titulo, quantidade):
        try:
            self.db.cursor.execute('SELECT id, quantidade FROM inventario_temp WHERE livro_id=?', (livro_id,))
            item = self.db.cursor.fetchone()
            if item:
                novo_qtd = item[1] + int(quantidade)
                self.db.cursor.execute('UPDATE inventario_temp SET quantidade=?, data_inclusao=? WHERE id=?', (novo_qtd, datetime.now().isoformat(), item[0]))
            else:
                self.db.cursor.execute('INSERT INTO inventario_temp (livro_id, isbn, titulo, quantidade, data_inclusao) VALUES (?, ?, ?, ?, ?)',
                                       (livro_id, isbn, titulo, int(quantidade), datetime.now().isoformat()))
            self.db.conexao.commit()
            return True, "Item adicionado ao inventário temporário."
        except Exception as e:
            return False, f"Erro ao adicionar inventário temporário: {str(e)}"

    def listar_inventario_temp(self):
        self.db.cursor.execute('SELECT livro_id, isbn, titulo, quantidade FROM inventario_temp')
        return self.db.cursor.fetchall()

    def limpar_inventario_temp(self):
        try:
            self.db.cursor.execute('DELETE FROM inventario_temp')
            self.db.conexao.commit()
            return True, "Inventário temporário limpo."
        except Exception as e:
            return False, f"Erro ao limpar inventário temporário: {str(e)}"

    def adicionar_estoque_por_id(self, id, quantidade_a_somar):
        """Soma uma quantidade ao estoque atual do livro"""
        try:
            # Primeiro pegamos a quantidade atual
            self.db.cursor.execute('SELECT quantidade FROM livros WHERE id=?', (id,))
            atual = self.db.cursor.fetchone()
            if atual:
                nova_qtd = atual[0] + int(quantidade_a_somar)
                self.db.cursor.execute('UPDATE livros SET quantidade=? WHERE id=?', (nova_qtd, id))
                self.db.conexao.commit()
                return True, f"Estoque atualizado: {nova_qtd} unidades."
            return False, "Livro não encontrado."
        except Exception as e:
            return False, f"Erro ao somar estoque: {str(e)}"    
    
    def devolver_ao_estoque(self, livro_id, quantidade):
        self.db.cursor.execute(
            "UPDATE livros SET quantidade = quantidade + ? WHERE id = ?",
            (quantidade, livro_id)
        )
        self.db.conexao.commit()