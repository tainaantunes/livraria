from datetime import datetime

class Venda:
    def __init__(self, db):
        self.db = db
    
    def criar_venda(self, vendedor_id, cliente_id):
        """Criar nova venda em aberto"""
        try:
            self.db.cursor.execute('''
                INSERT INTO vendas (vendedor_id, cliente_id, data_venda, status, valor_total, metodo_pagamento)
                VALUES (?, ?, ?, ?, ?, ?)
            ''', (vendedor_id, cliente_id, datetime.now().isoformat(), 'aberto', 0, None))
            self.db.conexao.commit()
            return True, self.db.cursor.lastrowid, "Venda criada com sucesso!"
        except Exception as e:
            return False, None, f"Erro ao criar venda: {str(e)}"
    
    def adicionar_item(self, venda_id, livro_id, quantidade, preco_unitario):
        """Adicionar item à venda"""
        try:
            # Verificar se há estoque suficiente
            estoque_atual = self.db.cursor.execute('SELECT quantidade FROM livros WHERE id = ?', (livro_id,)).fetchone()[0]
            if estoque_atual < quantidade:
                return False, f"Estoque insuficiente! Disponível: {estoque_atual}"
            
            subtotal = quantidade * preco_unitario
            self.db.cursor.execute('''
                INSERT INTO itens_venda (venda_id, livro_id, quantidade, preco_unitario, subtotal)
                VALUES (?, ?, ?, ?, ?)
            ''', (venda_id, livro_id, quantidade, preco_unitario, subtotal))
            self.db.conexao.commit()
            
            # Reduzir estoque
            self.db.cursor.execute('UPDATE livros SET quantidade = quantidade - ? WHERE id = ?', (quantidade, livro_id))
            self.db.conexao.commit()
            
            # Atualizar valor total da venda
            self._atualizar_total_venda(venda_id)
            return True, "Item adicionado com sucesso!"
        except Exception as e:
            return False, f"Erro ao adicionar item: {str(e)}"
    
    def atualizar_item(self, item_id, quantidade, preco_unitario):
        """Atualizar quantidade e preço do item"""
        try:
            subtotal = quantidade * preco_unitario
            self.db.cursor.execute('''
                UPDATE itens_venda SET quantidade=?, preco_unitario=?, subtotal=?
                WHERE id=?
            ''', (quantidade, preco_unitario, subtotal, item_id))
            self.db.conexao.commit()
            
            # Atualizar total da venda
            venda_id = self.db.cursor.execute('SELECT venda_id FROM itens_venda WHERE id=?', (item_id,)).fetchone()[0]
            self._atualizar_total_venda(venda_id)
            return True, "Item atualizado com sucesso!"
        except Exception as e:
            return False, f"Erro ao atualizar item: {str(e)}"
    
    def remover_item(self, item_id):
        """Remover item da venda"""
        try:
            # Obter dados do item antes de remover
            item = self.db.cursor.execute('SELECT venda_id, livro_id, quantidade FROM itens_venda WHERE id=?', (item_id,)).fetchone()
            venda_id, livro_id, quantidade = item
            
            # Verificar se a venda está aberta
            venda_status = self.db.cursor.execute('SELECT status FROM vendas WHERE id=?', (venda_id,)).fetchone()[0]
            
            self.db.cursor.execute('DELETE FROM itens_venda WHERE id=?', (item_id,))
            self.db.conexao.commit()
            
            # Se a venda estiver aberta, devolver quantidade ao estoque
            if venda_status == 'aberto':
                self.db.cursor.execute('UPDATE livros SET quantidade = quantidade + ? WHERE id = ?', (quantidade, livro_id))
                self.db.conexao.commit()
            
            # Atualizar total da venda
            self._atualizar_total_venda(venda_id)
            return True, "Item removido com sucesso!"
        except Exception as e:
            return False, f"Erro ao remover item: {str(e)}"
    
    def _atualizar_total_venda(self, venda_id):
        """Recalcular total da venda"""
        resultado = self.db.cursor.execute(
            'SELECT SUM(subtotal) FROM itens_venda WHERE venda_id=?', (venda_id,)
        ).fetchone()
        total = resultado[0] if resultado[0] else 0
        self.db.cursor.execute('UPDATE vendas SET valor_total=? WHERE id=?', (total, venda_id))
        self.db.conexao.commit()
    
    def listar_itens_venda(self, venda_id):
        """Listar itens de uma venda específica"""
        self.db.cursor.execute('''
            SELECT iv.id, iv.livro_id, l.titulo, iv.quantidade, iv.preco_unitario, iv.subtotal
            FROM itens_venda iv
            JOIN livros l ON iv.livro_id = l.id
            WHERE iv.venda_id = ?
            ORDER BY iv.id
        ''', (venda_id,))
        return self.db.cursor.fetchall()
    
    def buscar_livro(self, termo):
        """Buscar livro por nome, ISBN ou ID"""
        try:
            termo = termo.strip()
            if not termo:
                return []

            # Se for dígitos, tenta por ID e se não encontrar tenta por ISBN exato
            if termo.isdigit():
                self.db.cursor.execute('SELECT id, titulo, isbn, preco_venda FROM livros WHERE id=?', (int(termo),))
                resultado = self.db.cursor.fetchall()
                if resultado:
                    return resultado
                # Não encontrou por ID, tenta pelo ISBN preciso
                self.db.cursor.execute('SELECT id, titulo, isbn, preco_venda FROM livros WHERE isbn=?', (termo,))
                resultado = self.db.cursor.fetchall()
                if resultado:
                    return resultado

            # Buscar por nome OU isbn parcial (inclusivo)
            termo_like = f'%{termo}%'
            self.db.cursor.execute('''
                SELECT id, titulo, isbn, preco_venda FROM livros
                WHERE titulo LIKE ? OR isbn LIKE ?
            ''', (termo_like, termo_like))
            return self.db.cursor.fetchall()
        except Exception:
            return []
    
    def obter_venda(self, venda_id):
        """Obter detalhes da venda"""
        self.db.cursor.execute('''
            SELECT v.id, v.vendedor_id, v.cliente_id, v.data_venda, v.status, v.valor_total, v.metodo_pagamento, v.data_pagamento
            FROM vendas v
            WHERE v.id = ?
        ''', (venda_id,))
        return self.db.cursor.fetchone()

    def buscar_vendas_relatorio(self, data_ini=None, data_fim=None, status=None, metodo_pagamento=None, cliente_id=None, vendedor_id=None, livro_id=None):
        """Buscar vendas para relatório com filtros opcionais"""
        query = '''
            SELECT v.id, v.data_venda, v.status, v.metodo_pagamento, c.nome, ven.nome_vendedor, v.valor_total
            FROM vendas v
            JOIN clientes c ON v.cliente_id = c.id
            JOIN vendedores ven ON v.vendedor_id = ven.id
        '''
        conditions = []
        params = []

        if data_ini:
            conditions.append('date(v.data_venda) >= date(?)')
            params.append(data_ini)
        if data_fim:
            conditions.append('date(v.data_venda) <= date(?)')
            params.append(data_fim)
        if status:
            conditions.append('v.status = ?')
            params.append(status)
        if metodo_pagamento:
            conditions.append('v.metodo_pagamento = ?')
            params.append(metodo_pagamento)
        if cliente_id:
            conditions.append('v.cliente_id = ?')
            params.append(cliente_id)
        if vendedor_id:
            conditions.append('v.vendedor_id = ?')
            params.append(vendedor_id)
        if livro_id:
            query += ' JOIN itens_venda iv ON v.id = iv.venda_id '
            conditions.append('iv.livro_id = ?')
            params.append(livro_id)

        if conditions:
            query += ' WHERE ' + ' AND '.join(conditions)

        query += ' ORDER BY v.data_venda DESC'

        self.db.cursor.execute(query, tuple(params))
        return self.db.cursor.fetchall()
    
    def listar_vendas_abertas(self):
        """Listar vendas em aberto"""
        self.db.cursor.execute('''
            SELECT v.id, vendor.nome_vendedor, cli.nome, v.data_venda, v.valor_total
            FROM vendas v
            JOIN vendedores vendor ON v.vendedor_id = vendor.id
            JOIN clientes cli ON v.cliente_id = cli.id
            WHERE v.status = 'aberto'
            ORDER BY v.data_venda DESC
        ''')
        return self.db.cursor.fetchall()
    
    def listar_todas_vendas(self):
        """Listar todas as vendas"""
        self.db.cursor.execute('''
            SELECT v.id, vendor.nome_vendedor, cli.nome, v.data_venda, v.status, v.valor_total, v.metodo_pagamento
            FROM vendas v
            JOIN vendedores vendor ON v.vendedor_id = vendor.id
            JOIN clientes cli ON v.cliente_id = cli.id
            ORDER BY v.data_venda DESC
        ''')
        return self.db.cursor.fetchall()
    
    def finalizar_venda(self, venda_id, metodo_pagamento):
        """Finalizar venda e registrar pagamento"""
        try:
            self.db.cursor.execute('''
                UPDATE vendas SET status=?, metodo_pagamento=?, data_pagamento=?
                WHERE id=?
            ''', ('finalizado', metodo_pagamento, datetime.now().isoformat(), venda_id))
            self.db.conexao.commit()
            return True, "Venda finalizada com sucesso!"
        except Exception as e:
            return False, f"Erro ao finalizar venda: {str(e)}"
    
    def deletar_venda(self, venda_id):
        """Deletar venda (apenas se aberta)"""
        try:
            # Verificar status
            venda = self.obter_venda(venda_id)
            if venda and venda[4] == 'aberto':
                self.db.cursor.execute('DELETE FROM itens_venda WHERE venda_id=?', (venda_id,))
                self.db.cursor.execute('DELETE FROM vendas WHERE id=?', (venda_id,))
                self.db.conexao.commit()
                return True, "Venda cancelada com sucesso!"
            else:
                return False, "Apenas vendas abertas podem ser deletadas!"
        except Exception as e:
            return False, f"Erro ao deletar venda: {str(e)}"
