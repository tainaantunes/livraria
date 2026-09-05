import sqlite3
import os

class DatabaseBiblioteca:
    def __init__(self, db_name='biblioteca.db'):
        self.db_name = db_name
        self.conectar()
        self.criar_tabelas()
    
    def conectar(self):
        self.conexao = sqlite3.connect(self.db_name)
        self.cursor = self.conexao.cursor()
    
    def criar_tabelas(self):
        # Tabela Clientes
        self.cursor.execute('''
            CREATE TABLE IF NOT EXISTS clientes (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                nome TEXT NOT NULL,
                email TEXT,
                telefone TEXT,
                endereco TEXT,
                data_cadastro TEXT
            )
        ''')
        
        # Tabela Livros
        self.cursor.execute('''
            CREATE TABLE IF NOT EXISTS livros (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                titulo TEXT NOT NULL,
                autor TEXT,
                categoria TEXT,
                isbn TEXT UNIQUE,
                quantidade INTEGER,
                preco_compra REAL,
                preco_venda REAL,
                espirito TEXT,
                fornecedor_id INTEGER,
                data_cadastro TEXT,
                FOREIGN KEY (fornecedor_id) REFERENCES fornecedores(id)
            )
        ''')
        
        # Tabela Fornecedores
        self.cursor.execute('''
            CREATE TABLE IF NOT EXISTS fornecedores (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                nome TEXT NOT NULL,
                cnpj TEXT UNIQUE,
                email TEXT,
                telefone TEXT,
                endereco TEXT,
                data_cadastro TEXT
            )
        ''')
        
        # Tabela Vendedores
        self.cursor.execute('''
            CREATE TABLE IF NOT EXISTS vendedores (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                nome_vendedor TEXT NOT NULL,
                data_cadastro TEXT
            )
        ''')
        
        # Tabela Vendas
        self.cursor.execute('''
            CREATE TABLE IF NOT EXISTS vendas (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                vendedor_id INTEGER NOT NULL,
                cliente_id INTEGER NOT NULL,
                data_venda TEXT,
                status TEXT,
                valor_total REAL,
                metodo_pagamento TEXT,
                data_pagamento TEXT,
                FOREIGN KEY (vendedor_id) REFERENCES vendedores(id),
                FOREIGN KEY (cliente_id) REFERENCES clientes(id)
            )
        ''')
        
        # Tabela Itens de Venda
        self.cursor.execute('''
            CREATE TABLE IF NOT EXISTS itens_venda (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                venda_id INTEGER NOT NULL,
                livro_id INTEGER NOT NULL,
                quantidade INTEGER NOT NULL,
                preco_unitario REAL NOT NULL,
                subtotal REAL NOT NULL,
                FOREIGN KEY (venda_id) REFERENCES vendas(id),
                FOREIGN KEY (livro_id) REFERENCES livros(id)
            )
        ''')

        # Histórico de pagamentos vinculados a cada item da venda
        self.cursor.execute('''
            CREATE TABLE IF NOT EXISTS pagamentos_venda (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                item_venda_id INTEGER NOT NULL,
                quantidade INTEGER NOT NULL,
                valor REAL NOT NULL,
                metodo_pagamento TEXT NOT NULL,
                data_pagamento TEXT NOT NULL,
                FOREIGN KEY (item_venda_id) REFERENCES itens_venda(id)
            )
        ''')

        # Tabela Historico de Inventário
        self.cursor.execute('''
            CREATE TABLE IF NOT EXISTS inventario_historico (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                livro_id INTEGER NOT NULL,
                isbn TEXT,
                titulo TEXT,
                operacao TEXT,
                quantidade INTEGER,
                saldo_anterior INTEGER,
                saldo_posterior INTEGER,
                usuario TEXT,
                data TEXT,
                FOREIGN KEY (livro_id) REFERENCES livros(id)
            )
        ''')

        # Tabela inventário temporário (itens não aplicados)
        self.cursor.execute('''
            CREATE TABLE IF NOT EXISTS inventario_temp (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                livro_id INTEGER NOT NULL,
                isbn TEXT NOT NULL,
                titulo TEXT NOT NULL,
                quantidade INTEGER NOT NULL,
                data_inclusao TEXT,
                FOREIGN KEY (livro_id) REFERENCES livros(id)
            )
        ''')
        
        self.conexao.commit()
    
    def fechar(self):
        self.conexao.close()
