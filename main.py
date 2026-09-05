import tkinter as tk
import ttkbootstrap as tb
from ttkbootstrap.constants import *
from tkinter import messagebox, simpledialog
from datetime import datetime
from tkcalendar import DateEntry
from database import DatabaseBiblioteca
from models.cliente import Cliente
from models.livro import Livro
from models.fornecedor import Fornecedor
from models.vendedor import Vendedor
from models.venda import Venda
from PIL import Image, ImageTk
import os
import sys
import shutil
import stat
import xml.etree.ElementTree as ET
from tkinter import filedialog
from migrations import atualizar_banco


class BibliotecaApp:
    def __init__(self, root):
        self.root = root
        self.root.state('zoomed') # Abre a janela ocupando a tela toda
        
        # --- AQUI É ONDE A MÁGICA ACONTECE ---
        # Escolha um tema: 'cosmo', 'flatly', 'darkly' (escuro), 'superhero'
        self.style = tb.Style(theme="cosmo") 
        
        # Criando um estilo personalizado para botões grandes e modernos
        # 'Grande.TButton' é o nome que inventamos para este estilo
        # Criamos uma lista das cores que você usa para gerar os estilos grandes
        # Lista de sufixos de cores do bootstrap
        estilos_cores = ['primary', 'secondary', 'success', 'info', 'warning', 'danger','light', 'dark']

        for cor in estilos_cores:
            # Configura a versão SÓLIDA grande
            self.style.configure(f'{cor}.TButton', font=("Helvetica", 14, "bold"), padding=20)
            # Configura a versão OUTLINE (contorno) grande
            self.style.configure(f'{cor}.Outline.TButton', font=("Helvetica", 14, "bold"), padding=20)

        # Criamos um estilo NOVO para as outras telas (pequeno)
        # Chamaremos de 'Colheita.TButton' ou qualquer nome para os botões normais
        self.style.configure('Normal.TButton', font=("Helvetica", 10), padding=5)# O padding aumenta o tamanho interno do botão
        
        self.root.title("Sistema de Biblioteca - Tela Inicial")
        self.root.geometry("1000x700")
        self.root.resizable(True, True)
        
        # Inicializar banco de dados
        self.db = DatabaseBiblioteca()

        # --- Backup automático antes de qualquer atualização de banco ---
        try:
            if getattr(sys, 'frozen', False):
                base_path = os.path.dirname(sys.executable)
            else:
                base_path = os.path.abspath(".")
            caminho_db = os.path.join(base_path, "biblioteca.db")

            # Garante que o arquivo não está marcado como "somente leitura"
            # (pode acontecer se o banco veio de um backup, pendrive, OneDrive etc.)
            if os.path.exists(caminho_db):
                try:
                    os.chmod(caminho_db, stat.S_IWRITE | stat.S_IREAD)
                except Exception as e:
                    print(f"Aviso: não foi possível ajustar permissões do banco: {e}")

            if os.path.exists(caminho_db):
                backup = os.path.join(
                    base_path,
                    f"biblioteca_backup_{datetime.now().strftime('%Y%m%d_%H%M%S')}.db"
                )
                shutil.copy2(caminho_db, backup)
        except Exception as e:
            print(f"Aviso: não foi possível gerar backup automático: {e}")

        # --- Aplica migrações pendentes no banco (adiciona colunas/tabelas novas) ---
        try:
            atualizar_banco(self.db.conexao, self.db.cursor)
        except Exception as e:
            messagebox.showerror("Erro na atualização do banco", str(e))
            self.root.destroy()
            return

        self.cliente = Cliente(self.db)
        self.livro = Livro(self.db)
        self.fornecedor = Fornecedor(self.db)
        self.vendedor = Vendedor(self.db)
        self.venda = Venda(self.db)
        
        # Carregar ícones de pagamento
        self.carregar_icones_pagamento()
        
        self.criar_menu()
        self.criar_tela_inicial()
    
    def carregar_icones_pagamento(self):
        """Carrega os ícones dos métodos de pagamento (Compatível com .exe)"""
        import sys
        
        # Lógica para encontrar o caminho das imagens no .exe ou no script
        if getattr(sys, 'frozen', False):
            # Se for executável, o PyInstaller extrai tudo para sys._MEIPASS
            base_path = sys._MEIPASS
        else:
            # Se estiver rodando o .py normal, usa o caminho atual
            base_path = os.path.abspath(".")
            
        self.icones_pagamento = {}
        
        # Mapeamos os nomes para os caminhos usando os.path.join para evitar erros de barra / ou \
        icones_paths = {
            'PIX': os.path.join(base_path, 'images', 'pix.png'),
            'CARTAO DE DEBITO': os.path.join(base_path, 'images', 'debito.png'),
            'CARTAO DE CREDITO': os.path.join(base_path, 'images', 'credito.png'),
            'DINHEIRO': os.path.join(base_path, 'images', 'dinheiro.png')
        }
        
        for metodo, path in icones_paths.items():
            try:
                if os.path.exists(path):
                    img = Image.open(path)
                    img = img.resize((32, 32), Image.Resampling.LANCZOS)
                    self.icones_pagamento[metodo] = ImageTk.PhotoImage(img)
                else:
                    # Se o arquivo não existir no caminho especificado
                    print(f"Aviso: Ícone não encontrado em {path}")
                    self.icones_pagamento[metodo] = None
            except Exception as e:
                print(f"Erro ao carregar ícone {metodo}: {e}")
                self.icones_pagamento[metodo] = None
    
    def criar_menu(self):
        menubar = tk.Menu(self.root)
        self.root.config(menu=menubar)
        
        menu_arquivo = tk.Menu(menubar, tearoff=0)
        menubar.add_cascade(label="Arquivo", menu=menu_arquivo)
        menu_arquivo.add_command(label="Sair", command=self.root.quit)
        
        menu_modulos = tk.Menu(menubar, tearoff=0)
        menubar.add_cascade(label="Modulos", menu=menu_modulos)
        menu_modulos.add_command(label="Clientes", command=self.tela_clientes)
        menu_modulos.add_command(label="Livros", command=self.tela_livros)
        menu_modulos.add_command(label="Entrada de Livros", command=self.tela_entrada_livros)
        menu_modulos.add_command(label="Fornecedores", command=self.tela_fornecedores)
        menu_modulos.add_command(label="Vendedores", command=self.tela_vendedores)
        menu_modulos.add_command(label="Vendas", command=self.tela_vendas)
        menu_modulos.add_command(label="Inventário", command=self.tela_inventario)
        menu_modulos.add_command(label="Relatórios", command=self.tela_relatorios)
        menu_modulos.add_command(label="Importar Nota XML", command=self.tela_importar_xml)
    
    def criar_tela_inicial(self):
        self.limpar_janela()
        
        main_frame = tb.Frame(self.root, padding=30)
        main_frame.pack(fill=BOTH, expand=YES)

        # Título do Sistema
        tb.Label(main_frame, text="📚 SISTEMA LIVRARIA PRO", 
                font=("Helvetica", 45, "bold"), bootstyle="primary").pack(pady=(0, 40))

        menu_frame = tb.Frame(main_frame)
        menu_frame.pack(fill=BOTH, expand=YES)

        # Configuração de 3 colunas responsivas
        for i in range(3):
            menu_frame.columnconfigure(i, weight=1)

        # DEFINIÇÃO DE CORES POR BOTÃO:
        # SUCCESS = Verde | INFO = Azul Claro | WARNING = Amarelo/Laranja 
        # DANGER = Vermelho | PRIMARY = Azul Real | SECONDARY = Cinza
        menu_itens = [
            ("Registrar Venda", self.tela_vendas, "💰", SUCCESS),     # VERDE
            ("Entrada de Livros", self.tela_entrada_livros, "📥", INFO), # AZUL
            ("Inventário", self.tela_inventario, "📋", WARNING),      # LARANJA
            ("Importar Nota XML", self.tela_importar_xml, "�", DARK),   # Cinza escuro
            ("Gerenciar Livros", self.tela_livros, "📖", PRIMARY),     # AZUL ESCURO
            ("Gerenciar Clientes", self.tela_clientes, "👥", SECONDARY), # CINZA
            ("Gerenciar Fornecedores", self.tela_fornecedores, "🚚", SUCCESS), # Cinza Grafite / Preto
            ("Relatórios", self.tela_relatorios, "📊", INFO),       # Relatórios abaixo de Fornecedores
            ("Gerenciar Vendedores", self.tela_vendedores, "👔", WARNING),   # AZUL
            ("Devolução", self.tela_devolucao, "🔄", DARK), # Laranja
            ("Sair do Sistema", self.sair_sistema, "❌", DANGER), # Botão ficará alinhado à direita
        ]

        row, col = 0, 0
        sair_btn = None
        for texto, comando, icone, cor in menu_itens:
            # Criando o botão com a cor específica da iteração atual
            btn = tb.Button(
                menu_frame, 
                text=f"{icone}\n{texto}", 
                command=comando,
                style=f'{cor.lower()}.Outline.TButton',    # Usa o estilo de fonte que criamos no __init__
                #bootstyle=f"{cor}-outline", # Se quiser o botão "cheio", use apenas bootstyle=cor
                cursor="hand2"
            )
            
            btn.grid(row=row, column=col, padx=15, pady=15, sticky="nsew")

            # Lógica para organizar as colunas (3 por linha)
            col += 1
            if col > 2:
                col = 0
                row += 1

            # keep reference to the Sair button so we can reposition it to the right
            if texto == "Sair do Sistema":
                sair_btn = btn

        # Faz com que as linhas também estiquem se a janela crescer
        for r in range(row + 1):
            menu_frame.rowconfigure(r, weight=1)

        # Reposicionar o botão 'Sair do Sistema' para a coluna mais à direita
        if sair_btn:
            sair_btn.grid_forget()
            # garante que esteja na última linha, coluna 2 (direita)
            sair_btn.grid(row=row, column=2, padx=15, pady=15, sticky="nsew")
    
    def tela_clientes(self):
        self.limpar_janela()
        colunas = ["ID", "Nome", "Email", "Telefone", "Endereco"]

        frame = tb.Frame(self.root)
        frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        frame.columnconfigure(0, weight=1)
        frame.rowconfigure(2, weight=1)

        # --- TÍTULO ---
        tb.Label(frame, text="Gerenciar Clientes", font=("Arial", 20, "bold")).grid(
            row=0, column=0, sticky=tk.W, pady=(0, 15))

        # --- BOTÕES HORIZONTAIS ---
        botoes_frame = tb.Frame(frame)
        botoes_frame.grid(row=1, column=0, sticky=tk.EW, pady=(0, 10))
        
        tb.Button(botoes_frame, text="Adicionar", bootstyle=PRIMARY, 
                 command=self.adicionar_cliente).pack(side=tk.LEFT, padx=3)
        tb.Button(botoes_frame, text="Editar", bootstyle=PRIMARY,
                 command=self.editar_cliente).pack(side=tk.LEFT, padx=3)
        tb.Button(botoes_frame, text="Deletar", bootstyle=DANGER,
                 command=self.deletar_cliente).pack(side=tk.LEFT, padx=3)
        tb.Button(botoes_frame, text="Atualizar", bootstyle=PRIMARY,
                 command=self.atualizar_lista_clientes).pack(side=tk.LEFT, padx=3)
        tb.Button(botoes_frame, text="Voltar", bootstyle=SECONDARY,
                 command=self.criar_tela_inicial).pack(side=tk.LEFT, padx=3)

        # --- TREEVIEW COM SCROLLBARS ---
        tree_container = tb.Frame(frame)
        tree_container.grid(row=2, column=0, sticky=tk.NSEW)
        tree_container.rowconfigure(0, weight=1)
        tree_container.columnconfigure(0, weight=1)

        self.tree = tb.Treeview(tree_container, columns=colunas, show="headings", height=20)
        
        style = tb.Style()
        style.configure("Treeview", font=("Arial", 11), rowheight=25)
        style.configure("Treeview.Heading", font=("Arial", 11, "bold"))

        vsb = tb.Scrollbar(tree_container, orient=tk.VERTICAL, command=self.tree.yview)
        hsb = tb.Scrollbar(tree_container, orient=tk.HORIZONTAL, command=self.tree.xview)
        self.tree.configure(yscrollcommand=vsb.set, xscrollcommand=hsb.set)

        self.tree.grid(row=0, column=0, sticky="nsew")
        vsb.grid(row=0, column=1, sticky="ns")
        hsb.grid(row=1, column=0, sticky="ew")

        self.tree.column("#0", width=0, stretch=tk.NO)
        for col in colunas:
            self.tree.column(col, anchor=tk.W, width=150, minwidth=100, stretch=True)
            self.tree.heading(col, text=col, anchor=tk.W)

        dados = self.cliente.listar()
        for i, item in enumerate(dados):
            tag = "par" if i % 2 == 0 else "impar"
            self.tree.insert("", "end", values=item[:len(colunas)], tags=(tag,))

        self.refresh_func = self.atualizar_lista_clientes
    
    # def tela_livros(self):        
    #     dados = self.livro.listar()
    #     colunas = ["ID", "Titulo", "Autor", "Espirito", "ISBN", "Qtd", "Preco Compra", "Preco Venda", "Fornecedor"]
    #     self.criar_tela_crud("Livros", dados, colunas,
    #                         self.adicionar_livro, self.editar_livro,
    #                         self.deletar_livro, self.atualizar_lista_livros)

    def tela_livros(self):
        self.limpar_janela()
        colunas = ["ID", "Titulo", "Autor", "Categoria", "Espirito", "ISBN", "Qtd", "Preco Compra", "Preco Venda", "Fornecedor"]

        frame = tb.Frame(self.root)

        frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)

        # Título
        tb.Label(frame, text="Gerenciar Livros", font=("Arial", 20, "bold")).pack(pady=(0, 5))

        # Barra de pesquisa + botões de ação na mesma linha
        search_frame = tb.Frame(frame)
        search_frame.pack(fill=tk.X, pady=(0, 5))

        tb.Label(search_frame, text="🔍 Pesquisar:", font=("Arial", 15)).pack(side=tk.LEFT, padx=(0, 5))
        self.entry_pesquisa_livro = tb.Entry(search_frame, width=30)
        self.entry_pesquisa_livro.pack(side=tk.LEFT, padx=(0, 5))
        tb.Button(search_frame, text="Buscar", bootstyle=INFO,
                command=self.pesquisar_livros).pack(side=tk.LEFT, padx=(0, 3))
        tb.Button(search_frame, text="Limpar", bootstyle=SECONDARY,
                command=self.atualizar_lista_livros).pack(side=tk.LEFT, padx=(0, 15))

        # Separador visual e botões de ação na mesma linha
        tb.Button(search_frame, text="Adicionar", bootstyle=PRIMARY, command=self.adicionar_livro).pack(side=tk.LEFT, padx=3)
        tb.Button(search_frame, text="Atualizar", bootstyle=PRIMARY, command=self.atualizar_lista_livros).pack(side=tk.LEFT, padx=3)
        tb.Button(search_frame, text="Editar", bootstyle=PRIMARY, command=self.editar_livro).pack(side=tk.LEFT, padx=3)
        tb.Button(search_frame, text="Deletar", bootstyle=DANGER, command=self.deletar_livro).pack(side=tk.LEFT, padx=3)
        tb.Button(search_frame, text="Voltar", bootstyle=SECONDARY, command=self.criar_tela_inicial).pack(side=tk.LEFT, padx=3)

        # Bind Enter na pesquisa
        self.entry_pesquisa_livro.bind("<Return>", lambda e: self.pesquisar_livros())

        # Treeview com scrollbars
        tree_container = tb.Frame(frame)
        tree_container.pack(fill=tk.BOTH, expand=True)
        self.tree = tb.Treeview(tree_container, columns=colunas, show="headings", height=20)
        
        # Aumentar fonte das linhas e do cabeçalho
        style = tb.Style()
        style.configure("Treeview", font=("Arial", 12))
        style.configure("Treeview.Heading", font=("Arial", 12, "bold"))
        style.configure("Treeview", font=("Arial", 12), rowheight=30)

        vsb = tb.Scrollbar(tree_container, orient=tk.VERTICAL, command=self.tree.yview)
        hsb = tb.Scrollbar(tree_container, orient=tk.HORIZONTAL, command=self.tree.xview)
        self.tree.configure(yscrollcommand=vsb.set, xscrollcommand=hsb.set)

        self.tree.grid(row=0, column=0, sticky="nsew")
        vsb.grid(row=0, column=1, sticky="ns")
        hsb.grid(row=1, column=0, sticky="ew")

        tree_container.grid_columnconfigure(0, weight=8)
        tree_container.grid_rowconfigure(0, weight=8)

        self.tree.column("#0", width=0, stretch=tk.NO)
        for col in colunas:
            self.tree.column(col, anchor=tk.W, width=150, minwidth=100, stretch=True)
            self.tree.heading(col, text=col, anchor=tk.W)

        # Carrega os livros incluindo a categoria diretamente do banco para garantir ordem
        try:
            self.db.cursor.execute('''
                SELECT l.id, l.titulo, l.autor, l.categoria, l.espirito, l.isbn, l.quantidade, l.preco_compra, l.preco_venda, COALESCE(f.nome, 'N/A')
                FROM livros l
                LEFT JOIN fornecedores f ON l.fornecedor_id = f.id
                ORDER BY l.titulo
            ''')
            rows = self.db.cursor.fetchall()
        except Exception:
            rows = []

        for i, item in enumerate(rows):
            tag = "par" if i % 2 == 0 else "impar"
            self.tree.insert("", "end", values=item[:len(colunas)], tags=(tag,))

        self.refresh_func = self.atualizar_lista_livros
    
    def pesquisar_livros(self):
        termo = self.entry_pesquisa_livro.get().strip()
        if not termo:
            self.atualizar_lista_livros()
            return

        # Busca diretamente incluindo a categoria
        termo_busca = f"%{termo}%"
        try:
            self.db.cursor.execute('''
                SELECT l.id, l.titulo, l.autor, l.categoria, l.espirito, l.isbn, l.quantidade, l.preco_compra, l.preco_venda, COALESCE(f.nome, 'N/A')
                FROM livros l
                LEFT JOIN fornecedores f ON l.fornecedor_id = f.id
                WHERE LOWER(l.titulo) LIKE LOWER(?) OR LOWER(l.isbn) LIKE LOWER(?)
                ORDER BY l.titulo
            ''', (termo_busca, termo_busca))
            resultados = self.db.cursor.fetchall()
        except Exception:
            resultados = []

        # Limpa a tree e preenche com os resultados filtrados
        for item in self.tree.get_children():
            self.tree.delete(item)

        ncols = len(self.tree['columns'])
        for i, item in enumerate(resultados):
            tag = "par" if i % 2 == 0 else "impar"
            self.tree.insert("", "end", values=item[:ncols], tags=(tag,))

        if not resultados:
            messagebox.showinfo("Pesquisa", f"Nenhum livro encontrado para: '{termo}'")
    
    def tela_fornecedores(self):
        self.limpar_janela()
        colunas = ["ID", "Nome", "CNPJ", "Email", "Telefone"]

        frame = tb.Frame(self.root)
        frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        frame.columnconfigure(0, weight=1)
        frame.rowconfigure(2, weight=1)

        # --- TÍTULO ---
        tb.Label(frame, text="Gerenciar Fornecedores", font=("Arial", 20, "bold")).grid(
            row=0, column=0, sticky=tk.W, pady=(0, 15))

        # --- BOTÕES HORIZONTAIS ---
        botoes_frame = tb.Frame(frame)
        botoes_frame.grid(row=1, column=0, sticky=tk.EW, pady=(0, 10))
        
        tb.Button(botoes_frame, text="Adicionar", bootstyle=PRIMARY,
                 command=self.adicionar_fornecedor).pack(side=tk.LEFT, padx=3)
        tb.Button(botoes_frame, text="Editar", bootstyle=PRIMARY,
                 command=self.editar_fornecedor).pack(side=tk.LEFT, padx=3)
        tb.Button(botoes_frame, text="Deletar", bootstyle=DANGER,
                 command=self.deletar_fornecedor).pack(side=tk.LEFT, padx=3)
        tb.Button(botoes_frame, text="Atualizar", bootstyle=PRIMARY,
                 command=self.atualizar_lista_fornecedores).pack(side=tk.LEFT, padx=3)
        tb.Button(botoes_frame, text="Voltar", bootstyle=SECONDARY,
                 command=self.criar_tela_inicial).pack(side=tk.LEFT, padx=3)

        # --- TREEVIEW COM SCROLLBARS ---
        tree_container = tb.Frame(frame)
        tree_container.grid(row=2, column=0, sticky=tk.NSEW)
        tree_container.rowconfigure(0, weight=1)
        tree_container.columnconfigure(0, weight=1)

        self.tree = tb.Treeview(tree_container, columns=colunas, show="headings", height=20)
        
        style = tb.Style()
        style.configure("Treeview", font=("Arial", 11), rowheight=25)
        style.configure("Treeview.Heading", font=("Arial", 11, "bold"))

        vsb = tb.Scrollbar(tree_container, orient=tk.VERTICAL, command=self.tree.yview)
        hsb = tb.Scrollbar(tree_container, orient=tk.HORIZONTAL, command=self.tree.xview)
        self.tree.configure(yscrollcommand=vsb.set, xscrollcommand=hsb.set)

        self.tree.grid(row=0, column=0, sticky="nsew")
        vsb.grid(row=0, column=1, sticky="ns")
        hsb.grid(row=1, column=0, sticky="ew")

        self.tree.column("#0", width=0, stretch=tk.NO)
        for col in colunas:
            self.tree.column(col, anchor=tk.W, width=150, minwidth=100, stretch=True)
            self.tree.heading(col, text=col, anchor=tk.W)

        dados = self.fornecedor.listar()
        for i, item in enumerate(dados):
            tag = "par" if i % 2 == 0 else "impar"
            self.tree.insert("", "end", values=item[:len(colunas)], tags=(tag,))

        self.refresh_func = self.atualizar_lista_fornecedores
    
    def tela_vendedores(self):
        self.limpar_janela()
        colunas = ["ID", "Nome Vendedor", "Data Cadastro"]

        frame = tb.Frame(self.root)
        frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        frame.columnconfigure(0, weight=1)
        frame.rowconfigure(2, weight=1)

        # --- TÍTULO ---
        tb.Label(frame, text="Gerenciar Vendedores", font=("Arial", 20, "bold")).grid(
            row=0, column=0, sticky=tk.W, pady=(0, 15))

        # --- BOTÕES HORIZONTAIS ---
        botoes_frame = tb.Frame(frame)
        botoes_frame.grid(row=1, column=0, sticky=tk.EW, pady=(0, 10))
        
        tb.Button(botoes_frame, text="Adicionar", bootstyle=PRIMARY,
                 command=self.adicionar_vendedor).pack(side=tk.LEFT, padx=3)
        tb.Button(botoes_frame, text="Editar", bootstyle=PRIMARY,
                 command=self.editar_vendedor).pack(side=tk.LEFT, padx=3)
        tb.Button(botoes_frame, text="Deletar", bootstyle=DANGER,
                 command=self.deletar_vendedor).pack(side=tk.LEFT, padx=3)
        tb.Button(botoes_frame, text="Atualizar", bootstyle=PRIMARY,
                 command=self.atualizar_lista_vendedores).pack(side=tk.LEFT, padx=3)
        tb.Button(botoes_frame, text="Voltar", bootstyle=SECONDARY,
                 command=self.criar_tela_inicial).pack(side=tk.LEFT, padx=3)

        # --- TREEVIEW COM SCROLLBARS ---
        tree_container = tb.Frame(frame)
        tree_container.grid(row=2, column=0, sticky=tk.NSEW)
        tree_container.rowconfigure(0, weight=1)
        tree_container.columnconfigure(0, weight=1)

        self.tree = tb.Treeview(tree_container, columns=colunas, show="headings", height=20)
        
        style = tb.Style()
        style.configure("Treeview", font=("Arial", 11), rowheight=25)
        style.configure("Treeview.Heading", font=("Arial", 11, "bold"))

        vsb = tb.Scrollbar(tree_container, orient=tk.VERTICAL, command=self.tree.yview)
        hsb = tb.Scrollbar(tree_container, orient=tk.HORIZONTAL, command=self.tree.xview)
        self.tree.configure(yscrollcommand=vsb.set, xscrollcommand=hsb.set)

        self.tree.grid(row=0, column=0, sticky="nsew")
        vsb.grid(row=0, column=1, sticky="ns")
        hsb.grid(row=1, column=0, sticky="ew")

        self.tree.column("#0", width=0, stretch=tk.NO)
        for col in colunas:
            self.tree.column(col, anchor=tk.W, width=150, minwidth=100, stretch=True)
            self.tree.heading(col, text=col, anchor=tk.W)

        dados = self.vendedor.listar()
        for i, item in enumerate(dados):
            tag = "par" if i % 2 == 0 else "impar"
            self.tree.insert("", "end", values=item[:len(colunas)], tags=(tag,))

        self.refresh_func = self.atualizar_lista_vendedores
    
    def criar_tela_crud(self, titulo, dados, colunas, add_func, edit_func, del_func, refresh_func):
        self.limpar_janela()
        frame = tb.Frame(self.root)
        frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # Canvas + Scrollbar para garantir visibilidade em telas menores
        canvas = tk.Canvas(frame)
        scrollbar = tb.Scrollbar(frame, orient=tk.VERTICAL, command=canvas.yview)
        content_frame = tb.Frame(canvas)

        content_frame.bind("<Configure>", lambda e: canvas.configure(scrollregion=canvas.bbox("all")))
        canvas.create_window((0, 0), window=content_frame, anchor="nw")
        canvas.configure(yscrollcommand=scrollbar.set)

        canvas.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        
        titulo_label = tb.Label(content_frame, text=titulo, font=("Arial", 18, "bold"))
        titulo_label.pack()
        
        botoes = tb.Frame(content_frame)
        botoes.pack(pady=10)
        tb.Button(botoes, text="Adicionar", command=add_func).pack(side=tk.LEFT, padx=5)
        tb.Button(botoes, text="Editar", command=edit_func).pack(side=tk.LEFT, padx=5)
        tb.Button(botoes, text="Deletar", command=del_func).pack(side=tk.LEFT, padx=5)
        tb.Button(botoes, text="Atualizar", command=refresh_func).pack(side=tk.LEFT, padx=5)
        tb.Button(botoes, text="Voltar", command=self.criar_tela_inicial).pack(side=tk.LEFT, padx=5)
        
        # Container para a Treeview e suas próprias scrollbars
        tree_container = tb.Frame(content_frame)
        tree_container.pack(fill=tk.BOTH, expand=True)

        self.tree = tb.Treeview(tree_container, columns=colunas, height=15)
        
        # Scrollbar Vertical da Treeview
        vsb = tb.Scrollbar(tree_container, orient=tk.VERTICAL, command=self.tree.yview)
        # Scrollbar Horizontal da Treeview (PARA NÃO CORTAR CAMPOS)
        hsb = tb.Scrollbar(tree_container, orient=tk.HORIZONTAL, command=self.tree.xview)
        
        self.tree.configure(yscrollcommand=vsb.set, xscrollcommand=hsb.set)

        # Posicionamento da Treeview e Barras
        self.tree.grid(row=0, column=0, sticky='nsew')
        vsb.grid(row=0, column=1, sticky='ns')
        hsb.grid(row=1, column=0, sticky='ew')

        # Configura o peso para expandir
        tree_container.grid_columnconfigure(0, weight=1)
        tree_container.grid_rowconfigure(0, weight=1)

        self.tree.column("#0", width=0, stretch=tk.NO)
        for col in colunas:
            # minwidth garante que o campo não suma, width define o inicial
            self.tree.column(col, anchor=tk.W, width=150, minwidth=100, stretch=True)
            self.tree.heading(col, text=col, anchor=tk.W)
        
        for item in dados:
            self.tree.insert("", "end", values=item[:len(colunas)])
        
        self.refresh_func = refresh_func

    def adicionar_cliente(self):
        self.janela_formulario("Adicionar Cliente", 
                              [("Nome", "entry", ""), ("Email", "entry", ""), 
                               ("Telefone", "entry", ""), ("Endereco", "entry", "")],
                              lambda dados: self.cliente.adicionar(*dados),
                              self.atualizar_lista_clientes)
    
    def editar_cliente(self):
        if not self.tree.selection():
            messagebox.showwarning("Aviso", "Selecione um cliente!")
            return
        id_item = self.tree.item(self.tree.selection())['values'][0]
        cliente = self.cliente.buscar_por_id(id_item)
        if cliente:
            self.janela_formulario("Editar Cliente",
                                  [("Nome", "entry", cliente[1]), ("Email", "entry", cliente[2]),
                                   ("Telefone", "entry", cliente[3]), ("Endereco", "entry", cliente[4])],
                                  lambda dados: self.cliente.atualizar(id_item, *dados),
                                  self.atualizar_lista_clientes)
    
    def deletar_cliente(self):
        if not self.tree.selection():
            messagebox.showwarning("Aviso", "Selecione um cliente!")
            return
        id_item = self.tree.item(self.tree.selection())['values'][0]
        if messagebox.askyesno("Confirmacao", "Tem certeza que deseja deletar?"):
            sucesso, msg = self.cliente.deletar(id_item)
            messagebox.showinfo("Resultado", msg)
            if sucesso:
                self.atualizar_lista_clientes()
    
    def atualizar_lista_clientes(self):
        self.tela_clientes()
    
    def adicionar_livro(self):
        janela = tk.Toplevel(self.root)
        janela.title("Adicionar Livro")
        janela.geometry("500x600")
        janela.minsize(450, 550)
        
        # Container responsivo com scroll
        container = tb.Frame(janela)
        container.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        canvas = tk.Canvas(container)
        scrollbar = tb.Scrollbar(container, orient=tk.VERTICAL, command=canvas.yview)
        content_frame = tb.Frame(canvas)
        
        content_frame.bind("<Configure>", lambda e: canvas.configure(scrollregion=canvas.bbox("all")))
        canvas.create_window((0, 0), window=content_frame, anchor="nw")
        canvas.configure(yscrollcommand=scrollbar.set)
        
        canvas.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        
        # Título da seção
        tb.Label(content_frame, text="Adicionar Novo Livro", font=("Arial", 14, "bold")).pack(pady=(10, 20))
        
        campos = {}
        
        # Frame para organizar os campos em grid responsivo
        form_frame = tb.Frame(content_frame)
        form_frame.pack(fill=tk.BOTH, expand=True, padx=10)
        
        # Título
        tb.Label(form_frame, text="Título:", font=("Arial", 10, "bold")).grid(row=0, column=0, sticky=tk.W, pady=(10, 2))
        entrada_titulo = tb.Entry(form_frame, width=40)
        entrada_titulo.grid(row=0, column=1, pady=(10, 10), sticky=tk.EW, padx=(10, 0))
        campos['titulo'] = entrada_titulo
        
        # ISBN
        tb.Label(form_frame, text="ISBN:", font=("Arial", 10, "bold")).grid(row=1, column=0, sticky=tk.W, pady=(10, 2))
        entrada_isbn = tb.Entry(form_frame, width=40)
        entrada_isbn.grid(row=1, column=1, pady=(0, 10), sticky=tk.EW, padx=(10, 0))
        campos['isbn'] = entrada_isbn
        
        # Autor
        tb.Label(form_frame, text="Autor:", font=("Arial", 10, "bold")).grid(row=2, column=0, sticky=tk.W, pady=(10, 2))
        entrada_autor = tb.Entry(form_frame, width=40)
        entrada_autor.grid(row=2, column=1, pady=(0, 10), sticky=tk.EW, padx=(10, 0))
        campos['autor'] = entrada_autor

        # Categoria
        tb.Label(form_frame, text="Categoria:", font=("Arial", 10, "bold")).grid(row=3, column=0, sticky=tk.W, pady=(10, 2))
        entrada_categoria = tb.Entry(form_frame, width=40)
        entrada_categoria.grid(row=3, column=1, pady=(0, 10), sticky=tk.EW, padx=(10, 0))
        campos['categoria'] = entrada_categoria

        # Espírito
        tb.Label(form_frame, text="Espírito:", font=("Arial", 10, "bold")).grid(row=4, column=0, sticky=tk.W, pady=(10, 2))
        entrada_espirito = tb.Entry(form_frame, width=40)
        entrada_espirito.grid(row=4, column=1, pady=(0, 10), sticky=tk.EW, padx=(10, 0))
        campos['espirito'] = entrada_espirito
        
        # Quantidade
        tb.Label(form_frame, text="Quantidade:", font=("Arial", 10, "bold")).grid(row=5, column=0, sticky=tk.W, pady=(10, 2))
        entrada_qtd = tb.Entry(form_frame, width=40)
        entrada_qtd.insert(0, "1")
        entrada_qtd.grid(row=5, column=1, pady=(0, 10), sticky=tk.EW, padx=(10, 0))
        campos['qtd'] = entrada_qtd
        
        # Preço de Compra
        tb.Label(form_frame, text="Preço de Compra:", font=("Arial", 10, "bold")).grid(row=6, column=0, sticky=tk.W, pady=(10, 2))
        entrada_preco_compra = tb.Entry(form_frame, width=40)
        entrada_preco_compra.insert(0, "0.00")
        entrada_preco_compra.grid(row=6, column=1, pady=(0, 10), sticky=tk.EW, padx=(10, 0))
        campos['preco_compra'] = entrada_preco_compra
        
        # Preço de Venda
        tb.Label(form_frame, text="Preço de Venda:", font=("Arial", 10, "bold")).grid(row=7, column=0, sticky=tk.W, pady=(10, 2))
        entrada_preco_venda = tb.Entry(form_frame, width=40)
        entrada_preco_venda.insert(0, "0.00")
        entrada_preco_venda.grid(row=7, column=1, pady=(0, 10), sticky=tk.EW, padx=(10, 0))
        campos['preco_venda'] = entrada_preco_venda
        
        # Fornecedor
        tb.Label(form_frame, text="Fornecedor:", font=("Arial", 10, "bold")).grid(row=8, column=0, sticky=tk.W, pady=(10, 2))
        fornecedores = self.fornecedor.listar()
        fornecedor_combo = tb.Combobox(form_frame, 
                                       values=[f"{f[0]} - {f[1]}" for f in fornecedores], 
                                       state="readonly", width=38)
        # Definir fornecedor 1 como padrão se existir
        if fornecedores:
            fornecedor_combo.set(f"{fornecedores[0][0]} - {fornecedores[0][1]}")
        fornecedor_combo.grid(row=8, column=1, pady=(0, 20), sticky=tk.EW, padx=(10, 0))
        campos['fornecedor'] = fornecedor_combo
        
        # Configurar responsividade da grid
        form_frame.columnconfigure(1, weight=1)
        
        # Frame para botões
        button_frame = tb.Frame(content_frame)
        button_frame.pack(fill=tk.X, pady=(10, 20), padx=10)
        
        def salvar():
            try:
                titulo = campos['titulo'].get().strip()
                isbn = campos['isbn'].get().strip()
                autor = campos['autor'].get().strip()
                espirito = campos['espirito'].get().strip()
                qtd = campos['qtd'].get().strip()
                preco_compra = campos['preco_compra'].get().strip()
                preco_venda = campos['preco_venda'].get().strip()
                fornecedor_sel = campos['fornecedor'].get()
                
                if not titulo:
                    messagebox.showwarning("Aviso", "Título é obrigatório!")
                    return
                
                fornecedor_id = int(fornecedor_sel.split(" - ")[0]) if fornecedor_sel else None
                categoria = campos.get('categoria').get().strip() if campos.get('categoria') else None

                sucesso, msg = self.livro.adicionar(titulo, autor, isbn, qtd, preco_compra, preco_venda, espirito, fornecedor_id, categoria)
                messagebox.showinfo("Resultado", msg)
                
                if sucesso:
                    janela.destroy()
                    self.atualizar_lista_livros()
            except ValueError:
                messagebox.showerror("Erro", "Valores inválidos!")
        
        tb.Button(button_frame, text="Salvar", command=salvar).pack(side=tk.LEFT, padx=(0, 10))
        tb.Button(button_frame, text="Cancelar", command=janela.destroy).pack(side=tk.LEFT)
    
    def editar_livro(self):
        if not self.tree.selection():
            messagebox.showwarning("Aviso", "Selecione um livro!")
            return
        id_item = self.tree.item(self.tree.selection())['values'][0]
        livro = self.livro.buscar_por_id(id_item)
        if livro:
            janela = tk.Toplevel(self.root)
            janela.title("Editar Livro")
            janela.geometry("450x650")
            janela.resizable(True, True)

            canvas = tk.Canvas(janela)
            scrollbar = tb.Scrollbar(janela, orient=tk.VERTICAL, command=canvas.yview)
            frame = tb.Frame(canvas)

            frame.bind("<Configure>", lambda e: canvas.configure(scrollregion=canvas.bbox("all")))
            canvas.create_window((0, 0), window=frame, anchor="nw")
            canvas.configure(yscrollcommand=scrollbar.set)

            canvas.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
            scrollbar.pack(side=tk.RIGHT, fill=tk.Y)

            campos = {}
            
            # Titulo
            tb.Label(frame, text="Titulo:", font=("Arial", 10)).pack(anchor=tk.W, pady=(10, 2))
            entrada_titulo = tb.Entry(frame, width=40)
            entrada_titulo.insert(0, livro[1])
            entrada_titulo.pack(pady=(0, 10), fill=tk.X)
            campos['titulo'] = entrada_titulo
            
            # Autor
            tb.Label(frame, text="Autor:", font=("Arial", 10)).pack(anchor=tk.W, pady=(10, 2))
            entrada_autor = tb.Entry(frame, width=40)
            entrada_autor.insert(0, livro[2])
            entrada_autor.pack(pady=(0, 10), fill=tk.X)
            campos['autor'] = entrada_autor
            
            # Categoria
            tb.Label(frame, text="Categoria:", font=("Arial", 10)).pack(anchor=tk.W, pady=(10, 2))
            entrada_categoria = tb.Entry(frame, width=40)
            # tenta recuperar categoria diretamente do banco (mais seguro que depender da ordem do tuple)
            try:
                cat_row = self.db.cursor.execute('SELECT categoria FROM livros WHERE id=?', (id_item,)).fetchone()
                if cat_row and cat_row[0] is not None:
                    entrada_categoria.insert(0, cat_row[0])
            except Exception:
                pass
            entrada_categoria.pack(pady=(0, 10), fill=tk.X)
            campos['categoria'] = entrada_categoria
            
            # Espirito
            tb.Label(frame, text="Espirito:", font=("Arial", 10)).pack(anchor=tk.W, pady=(10, 2))
            entrada_espirito = tb.Entry(frame, width=40)
            entrada_espirito.insert(0, livro[6] or "")
            entrada_espirito.pack(pady=(0, 10), fill=tk.X)
            campos['espirito'] = entrada_espirito
            
            # ISBN
            tb.Label(frame, text="ISBN:", font=("Arial", 10)).pack(anchor=tk.W, pady=(10, 2))
            entrada_isbn = tb.Entry(frame, width=40)
            entrada_isbn.insert(0, livro[3])
            entrada_isbn.pack(pady=(0, 10), fill=tk.X)
            campos['isbn'] = entrada_isbn
            
            # Quantidade
            tb.Label(frame, text="Quantidade:", font=("Arial", 10)).pack(anchor=tk.W, pady=(10, 2))
            entrada_qtd = tb.Entry(frame, width=40)
            entrada_qtd.insert(0, str(livro[4]))
            entrada_qtd.pack(pady=(0, 10), fill=tk.X)
            campos['qtd'] = entrada_qtd
            
            # Preco Compra
            tb.Label(frame, text="Preco Compra:", font=("Arial", 10)).pack(anchor=tk.W, pady=(10, 2))
            entrada_preco_compra = tb.Entry(frame, width=40)
            entrada_preco_compra.insert(0, str(livro[5]))
            entrada_preco_compra.pack(pady=(0, 10), fill=tk.X)
            campos['preco_compra'] = entrada_preco_compra
            
            # Preco Venda
            tb.Label(frame, text="Preco Venda:", font=("Arial", 10)).pack(anchor=tk.W, pady=(10, 2))
            entrada_preco_venda = tb.Entry(frame, width=40)
            entrada_preco_venda.insert(0, str(livro[6]))
            entrada_preco_venda.pack(pady=(0, 10), fill=tk.X)
            campos['preco_venda'] = entrada_preco_venda
            
            # Fornecedor (Combobox)
            tb.Label(frame, text="Fornecedor:", font=("Arial", 10)).pack(anchor=tk.W, pady=(10, 2))
            fornecedores = self.fornecedor.listar()
            fornecedor_combo = tb.Combobox(frame,
                                           values=[f"{f[0]} - {f[1]}" for f in fornecedores],
                                           state="readonly", width=38)
            
            # Selecionar fornecedor atual
            if livro[8]:
                for i, f in enumerate(fornecedores):
                    if f[0] == livro[8]:
                        fornecedor_combo.current(i)
                        break
            
            fornecedor_combo.pack(pady=(0, 20), fill=tk.X)
            campos['fornecedor'] = fornecedor_combo
            
            def atualizar():
                try:
                    titulo = campos['titulo'].get()
                    autor = campos['autor'].get()
                    espirito = campos['espirito'].get()
                    isbn = campos['isbn'].get()
                    qtd = campos['qtd'].get()
                    preco_compra = campos['preco_compra'].get()
                    preco_venda = campos['preco_venda'].get()
                    fornecedor_sel = campos['fornecedor'].get()
                    
                    if not titulo:
                        messagebox.showwarning("Aviso", "Titulo e obrigatorio!")
                        return
                    
                    fornecedor_id = int(fornecedor_sel.split(" - ")[0]) if fornecedor_sel else None
                    categoria = campos.get('categoria').get().strip() if campos.get('categoria') else None

                    sucesso, msg = self.livro.atualizar(id_item, titulo, autor, isbn, qtd, preco_compra, preco_venda, espirito, fornecedor_id, categoria)
                    messagebox.showinfo("Resultado", msg)
                    
                    if sucesso:
                        janela.destroy()
                        self.atualizar_lista_livros()
                except ValueError:
                    messagebox.showerror("Erro", "Valores invalidos!")
            
            tb.Button(frame, text="Atualizar", command=atualizar).pack(side=tk.LEFT, padx=5, pady=20)
            tb.Button(frame, text="Cancelar", command=janela.destroy).pack(side=tk.LEFT, padx=5, pady=20)
    
    def deletar_livro(self):
        if not self.tree.selection():
            messagebox.showwarning("Aviso", "Selecione um livro!")
            return
        id_item = self.tree.item(self.tree.selection())['values'][0]
        if messagebox.askyesno("Confirmacao", "Tem certeza que deseja deletar?"):
            sucesso, msg = self.livro.deletar(id_item)
            messagebox.showinfo("Resultado", msg)
            if sucesso:
                self.atualizar_lista_livros()
    
    def atualizar_lista_livros(self):
        self.tela_livros()
    
    def tela_entrada_livros(self):
        self.limpar_janela()

        # Frame principal responsivo
        frame = tb.Frame(self.root)
        frame.pack(fill=tk.BOTH, expand=True, padx=15, pady=10)
        frame.columnconfigure(0, weight=1)
        # linha 0=título, 1=dados, 2=cálculo, 3=fornecedor, 4=botões
        for r in range(5):
            frame.rowconfigure(r, weight=0)

        # --- TÍTULO ---
        tb.Label(frame, text="Entrada de Livros", font=("Arial", 18, "bold")).grid(
            row=0, column=0, sticky=tk.W, pady=(0, 8))

        # ── BLOCO: DADOS DO LIVRO ─────────────────────────────────────
        entrada_frame = tb.LabelFrame(frame, text="Dados do Livro")
        entrada_frame.grid(row=1, column=0, sticky=tk.EW, pady=(0, 8))
        entrada_frame.columnconfigure(1, weight=1)

        # Dicionários de lookup
        livros_dict = {}
        livros_dict_isbn = {}
        for livro in self.livro.listar():
            titulo = livro[1] if livro[1] else f"ID-{livro[0]}"
            isbn   = livro[4] if livro[4] else f"ID-{livro[0]}"
            info = {
                'id': livro[0], 'titulo': livro[1], 'isbn': isbn,
                'preco_compra': livro[6], 'preco_venda': livro[7],
                'fornecedor_id': livro[9] if len(livro) > 9 else None
            }
            livros_dict[titulo]  = info
            livros_dict_isbn[isbn] = info

        # Nome do Livro
        tb.Label(entrada_frame, text="Nome do Livro:", font=("Arial", 10)).grid(
            row=0, column=0, sticky=tk.W, padx=10, pady=5)
        entrada_nome = tb.Combobox(entrada_frame, state="normal")
        entrada_nome.grid(row=0, column=1, sticky=tk.EW, padx=10, pady=5)
        entrada_nome['values'] = list(livros_dict.keys())

        # ISBN
        tb.Label(entrada_frame, text="ISBN:", font=("Arial", 10)).grid(
            row=1, column=0, sticky=tk.W, padx=10, pady=5)
        entrada_isbn = tb.Entry(entrada_frame)
        entrada_isbn.grid(row=1, column=1, sticky=tk.EW, padx=10, pady=5)

        # Quantidade
        tb.Label(entrada_frame, text="Quantidade:", font=("Arial", 10)).grid(
            row=2, column=0, sticky=tk.W, padx=10, pady=5)
        entrada_qtd = tb.Entry(entrada_frame)
        entrada_qtd.insert(0, "1")
        entrada_qtd.grid(row=2, column=1, sticky=tk.EW, padx=10, pady=5)

        # Valor Unitário
        tb.Label(entrada_frame, text="Valor Unitário (R$):", font=("Arial", 10)).grid(
            row=3, column=0, sticky=tk.W, padx=10, pady=5)
        entrada_valor = tb.Entry(entrada_frame)
        entrada_valor.insert(0, "0.00")
        entrada_valor.grid(row=3, column=1, sticky=tk.EW, padx=10, pady=5)

        # Percentual de Desconto
        tb.Label(entrada_frame, text="Percentual de Desconto (%):", font=("Arial", 10)).grid(
            row=4, column=0, sticky=tk.W, padx=10, pady=5)
        entrada_percentual = tb.Entry(entrada_frame)
        entrada_percentual.insert(0, "0")
        entrada_percentual.grid(row=4, column=1, sticky=tk.EW, padx=10, pady=5)

        # ── BLOCO: CÁLCULO AUTOMÁTICO ─────────────────────────────────
        calculo_frame = tb.LabelFrame(frame, text="Cálculo Automático")
        calculo_frame.grid(row=2, column=0, sticky=tk.EW, pady=(0, 8))
        calculo_frame.columnconfigure(1, weight=1)

        tb.Label(calculo_frame, text="Preço Compra (R$):", font=("Arial", 10, "bold")).grid(
            row=0, column=0, sticky=tk.W, padx=10, pady=5)
        label_preco_compra = tb.Label(calculo_frame, text="0.00",
                                      font=("Arial", 12, "bold"), foreground="green")
        label_preco_compra.grid(row=0, column=1, sticky=tk.W, padx=10, pady=5)

        tb.Label(calculo_frame, text="Preço Venda (R$):", font=("Arial", 10, "bold")).grid(
            row=1, column=0, sticky=tk.W, padx=10, pady=5)
        entrada_preco_venda = tb.Entry(calculo_frame, font=("Arial", 12, "bold"))
        entrada_preco_venda.insert(0, "0.00")
        entrada_preco_venda.grid(row=1, column=1, sticky=tk.EW, padx=10, pady=5)
        tb.Label(calculo_frame, text="(editável - sugestão automática)",
                 font=("Arial", 8, "italic")).grid(row=1, column=2, padx=10, pady=5)

        # ── BLOCO: FORNECEDOR ─────────────────────────────────────────
        fornecedor_frame = tb.LabelFrame(frame, text="Fornecedor")
        fornecedor_frame.grid(row=3, column=0, sticky=tk.EW, pady=(0, 8))
        fornecedor_frame.columnconfigure(0, weight=1)

        fornecedores = self.fornecedor.listar()
        fornecedor_combo = tb.Combobox(fornecedor_frame,
                                       values=[f"{f[0]} - {f[1]}" for f in fornecedores],
                                       state="readonly")
        fornecedor_combo.pack(fill=tk.X, padx=10, pady=8)

        # ── BOTÕES ────────────────────────────────────────────────────
        botoes_frame = tb.Frame(frame)
        botoes_frame.grid(row=4, column=0, sticky=tk.W, pady=8)

        # ── FUNÇÕES ───────────────────────────────────────────────────
        def atualizar_calculos(*args):
            try:
                valor_unit = float(entrada_valor.get())
                percentual = float(entrada_percentual.get())
                preco_compra = valor_unit - (valor_unit * percentual / 100)
                preco_venda_sugerido = preco_compra + 10
                label_preco_compra.config(text=f"{preco_compra:.2f}")
                entrada_preco_venda.delete(0, tk.END)
                entrada_preco_venda.insert(0, f"{preco_venda_sugerido:.2f}")
            except ValueError:
                label_preco_compra.config(text="Erro")
                entrada_preco_venda.delete(0, tk.END)
                entrada_preco_venda.insert(0, "Erro")

        def atualizar_sugestoes_nome(event):
            if event.keysym in ('Down', 'Up', 'Return', 'Escape', 'Tab'):
                return
            texto = entrada_nome.get().strip().lower()
            sugestoes = [l for l in livros_dict.keys() if texto in l.lower()]
            entrada_nome['values'] = sugestoes if sugestoes else list(livros_dict.keys())

        def ao_selecionar_livro_por_nome(*args):
            livro_sel = entrada_nome.get().strip()
            if livro_sel in livros_dict:
                entrada_isbn.delete(0, tk.END)
                entrada_isbn.insert(0, livros_dict[livro_sel]['isbn'])
                atualizar_calculos()
            elif livro_sel:
                if not messagebox.askyesno("Livro não cadastrado",
                        f"Livro '{livro_sel}' não cadastrado. Deseja continuar cadastrando?"):
                    entrada_nome.delete(0, tk.END)
                    entrada_isbn.delete(0, tk.END)

        def ao_preencher_isbn(*args):
            isbn_digitado = entrada_isbn.get().strip()
            if isbn_digitado and isbn_digitado in livros_dict_isbn:
                dados = livros_dict_isbn[isbn_digitado]
                if not entrada_nome.get():
                    entrada_nome.delete(0, tk.END)
                    entrada_nome.insert(0, dados['titulo'])
                atualizar_calculos()

        def limpar_campos():
            entrada_nome.delete(0, tk.END)
            entrada_isbn.delete(0, tk.END)
            entrada_qtd.delete(0, tk.END)
            entrada_qtd.insert(0, "1")
            entrada_valor.delete(0, tk.END)
            entrada_valor.insert(0, "0.00")
            entrada_percentual.delete(0, tk.END)
            entrada_percentual.insert(0, "0")
            fornecedor_combo.set("")
            label_preco_compra.config(text="0.00")
            entrada_preco_venda.delete(0, tk.END)
            entrada_preco_venda.insert(0, "0.00")

        def salvar_entrada():
            try:
                nome_livro    = entrada_nome.get().strip()
                isbn_livro    = entrada_isbn.get().strip()
                quantidade    = int(entrada_qtd.get())
                valor_unit    = float(entrada_valor.get())
                percentual    = float(entrada_percentual.get())
                preco_venda   = float(entrada_preco_venda.get())
                fornecedor_sel = fornecedor_combo.get()

                if not nome_livro:
                    messagebox.showwarning("Aviso", "Digite o nome do livro!")
                    return
                if not fornecedor_sel:
                    messagebox.showwarning("Aviso", "Selecione um fornecedor!")
                    return

                if nome_livro in livros_dict and not isbn_livro:
                    isbn_livro = livros_dict[nome_livro].get('isbn', '')
                if isbn_livro in livros_dict_isbn and not nome_livro:
                    nome_livro = livros_dict_isbn[isbn_livro].get('titulo', nome_livro)

                preco_compra = valor_unit - (valor_unit * percentual / 100)
                fornecedor_id = int(fornecedor_sel.split(" - ")[0])

                if isbn_livro:
                    livro_existente = self.db.cursor.execute(
                        'SELECT id FROM livros WHERE isbn=?', (isbn_livro,)).fetchone()
                else:
                    livro_existente = self.db.cursor.execute(
                        'SELECT id FROM livros WHERE titulo=?', (nome_livro,)).fetchone()

                if livro_existente:
                    self.db.cursor.execute('''
                        UPDATE livros SET quantidade=quantidade+?, preco_compra=?, preco_venda=?, fornecedor_id=?
                        WHERE id=?
                    ''', (quantidade, preco_compra, preco_venda, fornecedor_id, livro_existente[0]))
                    msg = f"Livro atualizado! +{quantidade} unidades"
                else:
                    self.db.cursor.execute('''
                        INSERT INTO livros (titulo, isbn, quantidade, preco_compra, preco_venda, fornecedor_id, data_cadastro)
                        VALUES (?, ?, ?, ?, ?, ?, ?)
                    ''', (nome_livro, isbn_livro, quantidade, preco_compra, preco_venda,
                          fornecedor_id, datetime.now().isoformat()))
                    msg = "Livro adicionado com sucesso!"

                self.db.conexao.commit()
                messagebox.showinfo("Sucesso", msg)
                limpar_campos()

            except ValueError:
                messagebox.showerror("Erro", "Verifique os valores digitados!")
            except Exception as e:
                messagebox.showerror("Erro", str(e))

        # Bindings
        entrada_nome.bind('<KeyRelease>', atualizar_sugestoes_nome)
        entrada_nome.bind('<<ComboboxSelected>>', ao_selecionar_livro_por_nome)
        entrada_isbn.bind('<FocusOut>', ao_preencher_isbn)
        entrada_valor.bind('<KeyRelease>', atualizar_calculos)
        entrada_percentual.bind('<KeyRelease>', atualizar_calculos)

        # Botões
        tb.Button(botoes_frame, text="💾 Salvar Entrada", bootstyle=SUCCESS,
                  command=salvar_entrada).pack(side=tk.LEFT, padx=(0, 8))
        tb.Button(botoes_frame, text="🧹 Limpar", bootstyle=SECONDARY,
                  command=limpar_campos).pack(side=tk.LEFT, padx=(0, 8))
        tb.Button(botoes_frame, text="⬅ Voltar", bootstyle=SECONDARY,
                  command=self.criar_tela_inicial).pack(side=tk.LEFT)
    
    def adicionar_fornecedor(self):
        self.janela_formulario("Adicionar Fornecedor",
                              [("Nome", "entry", ""), ("CNPJ", "entry", ""),
                               ("Email", "entry", ""), ("Telefone", "entry", ""),
                               ("Endereco", "entry", "")],
                              lambda dados: self.fornecedor.adicionar(*dados),
                              self.atualizar_lista_fornecedores)
    
    def editar_fornecedor(self):
        if not self.tree.selection():
            messagebox.showwarning("Aviso", "Selecione um fornecedor!")
            return
        id_item = self.tree.item(self.tree.selection())['values'][0]
        fornecedor = self.fornecedor.buscar_por_id(id_item)
        if fornecedor:
            self.janela_formulario("Editar Fornecedor",
                                  [("Nome", "entry", fornecedor[1]), ("CNPJ", "entry", fornecedor[2]),
                                   ("Email", "entry", fornecedor[3]), ("Telefone", "entry", fornecedor[4]),
                                   ("Endereco", "entry", fornecedor[5])],
                                  lambda dados: self.fornecedor.atualizar(id_item, *dados),
                                  self.atualizar_lista_fornecedores)
    
    def deletar_fornecedor(self):
        if not self.tree.selection():
            messagebox.showwarning("Aviso", "Selecione um fornecedor!")
            return
        id_item = self.tree.item(self.tree.selection())['values'][0]
        if messagebox.askyesno("Confirmacao", "Tem certeza que deseja deletar?"):
            sucesso, msg = self.fornecedor.deletar(id_item)
            messagebox.showinfo("Resultado", msg)
            if sucesso:
                self.atualizar_lista_fornecedores()
    
    def atualizar_lista_fornecedores(self):
        self.tela_fornecedores()
    
    def adicionar_vendedor(self):
        self.janela_formulario("Adicionar Vendedor",
                              [("Nome Vendedor", "entry", "")],
                              lambda dados: self.vendedor.adicionar(*dados),
                              self.atualizar_lista_vendedores)
    
    def editar_vendedor(self):
        if not self.tree.selection():
            messagebox.showwarning("Aviso", "Selecione um vendedor!")
            return
        id_item = self.tree.item(self.tree.selection())['values'][0]
        vendedor = self.vendedor.buscar_por_id(id_item)
        if vendedor:
            self.janela_formulario("Editar Vendedor",
                                  [("Nome Vendedor", "entry", vendedor[1])],
                                  lambda dados: self.vendedor.atualizar(id_item, *dados),
                                  self.atualizar_lista_vendedores)
    
    def deletar_vendedor(self):
        if not self.tree.selection():
            messagebox.showwarning("Aviso", "Selecione um vendedor!")
            return
        id_item = self.tree.item(self.tree.selection())['values'][0]
        if messagebox.askyesno("Confirmacao", "Tem certeza que deseja deletar?"):
            sucesso, msg = self.vendedor.deletar(id_item)
            messagebox.showinfo("Resultado", msg)
            if sucesso:
                self.atualizar_lista_vendedores()
    
    def atualizar_lista_vendedores(self):
        self.tela_vendedores()
    
    def tela_vendas(self):
        self.limpar_janela()
        
        frame = tb.Frame(self.root)
        frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        frame.columnconfigure(0, weight=1)
        frame.rowconfigure(0, weight=0)
        frame.rowconfigure(1, weight=0)
        frame.rowconfigure(2, weight=1)

        # --- TÍTULO ---
        tb.Label(frame, text="Gerenciar Vendas", font=("Arial", 20, "bold")).grid(
            row=0, column=0, sticky=tk.W, pady=(0, 15))

        # --- BOTÕES HORIZONTAIS (APÓS O TÍTULO) ---
        botoes_frame = tb.Frame(frame)
        botoes_frame.grid(row=1, column=0, sticky=tk.EW, pady=(0, 10))
        
        tb.Button(botoes_frame, text="Nova Venda", bootstyle=SUCCESS,
                 command=self.nova_venda).pack(side=tk.LEFT, padx=3)
        tb.Button(botoes_frame, text="Continuar Venda", bootstyle=INFO,
                 command=self.continuar_venda).pack(side=tk.LEFT, padx=3)
        tb.Button(botoes_frame, text="Relatório de Vendas", bootstyle=PRIMARY,
                 command=self.relatorio_vendas).pack(side=tk.LEFT, padx=3)
        tb.Button(botoes_frame, text="Histórico", bootstyle=WARNING,
                 command=self.historico_vendas).pack(side=tk.LEFT, padx=3)
        tb.Button(botoes_frame, text="Voltar", bootstyle=SECONDARY,
                 command=self.criar_tela_inicial).pack(side=tk.LEFT, padx=3)

    def relatorio_vendas(self):
        self.limpar_janela()

        frame = tb.Frame(self.root)
        frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        frame.rowconfigure(2, weight=1)
        frame.columnconfigure(0, weight=1)

        # --- TÍTULO ---
        tb.Label(frame, text="Relatório de Vendas", font=("Arial", 18, "bold")).grid(
            row=0, column=0, pady=(0, 8), sticky=tk.W)

        # --- FILTROS ---
        filtro_frame = tb.LabelFrame(frame, text="Filtros")
        filtro_frame.grid(row=1, column=0, sticky=tk.EW, padx=2, pady=4)
        filtro_frame.columnconfigure(1, weight=1)
        filtro_frame.columnconfigure(3, weight=1)

        tb.Label(filtro_frame, text="Data Início (DD/MM/YYYY):").grid(row=0, column=0, sticky=tk.W, padx=5, pady=3)
        entrada_data_ini = tb.Entry(filtro_frame, width=15)
        entrada_data_ini.insert(0, datetime.now().strftime('%d/%m/%Y'))
        entrada_data_ini.grid(row=0, column=1, padx=5, pady=3, sticky=tk.W)

        tb.Label(filtro_frame, text="Data Fim (DD/MM/YYYY):").grid(row=0, column=2, sticky=tk.W, padx=5, pady=3)
        entrada_data_fim = tb.Entry(filtro_frame, width=15)
        entrada_data_fim.insert(0, datetime.now().strftime('%d/%m/%Y'))
        entrada_data_fim.grid(row=0, column=3, padx=5, pady=3, sticky=tk.W)

        tb.Label(filtro_frame, text="Forma de Pagamento:").grid(row=1, column=0, sticky=tk.W, padx=5, pady=3)
        entrada_pagamento = tb.Combobox(filtro_frame,
            values=["", "DINHEIRO", "PIX", "CARTAO DE DEBITO", "CARTAO DE CREDITO"], width=20)
        entrada_pagamento.grid(row=1, column=1, padx=5, pady=3, sticky=tk.W)

        tb.Label(filtro_frame, text="Status:").grid(row=1, column=2, sticky=tk.W, padx=5, pady=3)
        entrada_status = tb.Combobox(filtro_frame, values=["", "aberto", "finalizado", "cancelado"], width=15)
        entrada_status.grid(row=1, column=3, padx=5, pady=3, sticky=tk.W)

        tb.Label(filtro_frame, text="Cliente:").grid(row=2, column=0, sticky=tk.W, padx=5, pady=3)
        clientes = self.cliente.listar()
        cliente_combo = tb.Combobox(filtro_frame,
            values=[""] + [f"{c[0]} - {c[1]}" for c in clientes], width=35)
        cliente_combo.grid(row=2, column=1, columnspan=3, padx=5, pady=3, sticky=tk.W)

        tb.Label(filtro_frame, text="Vendedor:").grid(row=3, column=0, sticky=tk.W, padx=5, pady=3)
        vendedores = self.vendedor.listar()
        vendedor_combo = tb.Combobox(filtro_frame,
            values=[""] + [f"{v[0]} - {v[1]}" for v in vendedores], width=35)
        vendedor_combo.grid(row=3, column=1, columnspan=3, padx=5, pady=3, sticky=tk.W)

        tb.Label(filtro_frame, text="Livro:").grid(row=4, column=0, sticky=tk.W, padx=5, pady=3)
        livros = self.livro.listar()
        livro_combo = tb.Combobox(filtro_frame,
            values=[""] + [f"{l[0]} - {l[1]}" for l in livros], width=35)
        livro_combo.grid(row=4, column=1, columnspan=3, padx=5, pady=3, sticky=tk.W)

        # --- TABELA (criada antes das funções para poder ser referenciada nelas) ---
        colunas = ["ID", "Data", "Status", "Pagamento", "Cliente", "Vendedor", "Total"]
        tree_container = tb.Frame(frame)
        tree_container.grid(row=2, column=0, sticky=tk.NSEW, padx=2, pady=(0, 4))
        tree_container.rowconfigure(0, weight=1)
        tree_container.columnconfigure(0, weight=1)

        tree_relatorio = tb.Treeview(tree_container, columns=colunas, show="headings")

        style = tb.Style()
        style.configure("Treeview", font=("Arial", 11), rowheight=28)
        style.configure("Treeview.Heading", font=("Arial", 11, "bold"))
        tree_relatorio.tag_configure("par",   background="#f0f0f0")
        tree_relatorio.tag_configure("impar", background="#ffffff")

        larguras = {"ID": 50, "Data": 160, "Status": 90, "Pagamento": 160,
                    "Cliente": 160, "Vendedor": 130, "Total": 90}
        for col in colunas:
            tree_relatorio.column(col, anchor=tk.W, width=larguras[col], stretch=True)
            tree_relatorio.heading(col, text=col, anchor=tk.W)

        vsb = tb.Scrollbar(tree_container, orient=tk.VERTICAL,   command=tree_relatorio.yview)
        hsb = tb.Scrollbar(tree_container, orient=tk.HORIZONTAL, command=tree_relatorio.xview)
        tree_relatorio.configure(yscrollcommand=vsb.set, xscrollcommand=hsb.set)
        tree_relatorio.grid(row=0, column=0, sticky=tk.NSEW)
        vsb.grid(row=0, column=1, sticky=tk.NS)
        hsb.grid(row=1, column=0, sticky=tk.EW)

        # --- RODAPÉ ---
        label_total = tb.Label(frame, text="Total: R$ 0.00", font=("Arial", 12, "bold"))
        label_total.grid(row=3, column=0, sticky=tk.E, pady=4)

        # --- FUNÇÕES ---
        def gerar_relatorio():
            try:
                data_ini = datetime.strptime(entrada_data_ini.get(), '%d/%m/%Y').strftime('%Y-%m-%d')
                data_fim = datetime.strptime(entrada_data_fim.get(), '%d/%m/%Y').strftime('%Y-%m-%d')
            except:
                data_ini = data_fim = None

            status      = entrada_status.get().strip() or None
            pagamento   = entrada_pagamento.get().strip() or None
            cliente_id  = int(cliente_combo.get().split(' - ')[0])  if cliente_combo.get()  else None
            vendedor_id = int(vendedor_combo.get().split(' - ')[0]) if vendedor_combo.get() else None
            livro_id    = int(livro_combo.get().split(' - ')[0])    if livro_combo.get()    else None

            resultado = self.venda.buscar_vendas_relatorio(
                data_ini=data_ini, data_fim=data_fim,
                status=status,
                metodo_pagamento=pagamento if pagamento != 'Nenhum' else None,
                cliente_id=cliente_id, vendedor_id=vendedor_id, livro_id=livro_id
            )

            for i in tree_relatorio.get_children():
                tree_relatorio.delete(i)

            total_geral = 0.0
            for idx, row in enumerate(resultado):
                tag = "par" if idx % 2 == 0 else "impar"
                tree_relatorio.insert('', 'end', values=row, tags=(tag,))
                try:
                    total_geral += float(row[6])
                except:
                    pass
            label_total.config(text=f"Total: R$ {total_geral:.2f}")

        def limpar_filtros():
            entrada_data_ini.delete(0, tk.END)
            entrada_data_ini.insert(0, datetime.now().strftime('%d/%m/%Y'))
            entrada_data_fim.delete(0, tk.END)
            entrada_data_fim.insert(0, datetime.now().strftime('%d/%m/%Y'))
            entrada_pagamento.set("")
            entrada_status.set("")
            cliente_combo.set("")
            vendedor_combo.set("")
            livro_combo.set("")
            for i in tree_relatorio.get_children():
                tree_relatorio.delete(i)
            label_total.config(text="Total: R$ 0.00")

        # --- BOTÕES dentro do filtro_frame (após funções definidas) ---
        botoes_frame = tb.Frame(filtro_frame)
        botoes_frame.grid(row=3, column=2, columnspan=4, pady=(8, 5), padx=5, sticky=tk.W)

        tb.Button(botoes_frame, text="🔍 Buscar Relatório", bootstyle=PRIMARY,
                  command=gerar_relatorio).pack(side=tk.LEFT, padx=5)
        tb.Button(botoes_frame, text="🧹 Limpar Filtros", bootstyle=PRIMARY,
                  command=limpar_filtros).pack(side=tk.LEFT, padx=5)
        tb.Button(botoes_frame, text="⬅ Voltar", bootstyle=SECONDARY,
                  command=self.tela_vendas).pack(side=tk.LEFT, padx=5)

        # Carrega registros de hoje ao abrir
        gerar_relatorio()

    def tela_relatorios(self):
        self.limpar_janela()

        frame = tb.Frame(self.root)
        frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        frame.columnconfigure(0, weight=1)

        tb.Label(frame, text="Módulo de Relatórios", font=("Arial", 20, "bold")).grid(
            row=0, column=0, sticky=tk.W, pady=(0, 12))

        # Filtros
        filtro_frame = tb.LabelFrame(frame, text="Filtros")
        filtro_frame.grid(row=1, column=0, sticky=tk.EW, padx=2, pady=4)
        filtro_frame.columnconfigure(1, weight=1)

        tb.Label(filtro_frame, text="Data Início (DD/MM/YYYY):").grid(row=0, column=0, sticky=tk.W, padx=5, pady=3)
        entrada_data_ini = tb.Entry(filtro_frame, width=15)
        entrada_data_ini.insert(0, datetime.now().strftime('%d/%m/%Y'))
        entrada_data_ini.grid(row=0, column=1, padx=5, pady=3, sticky=tk.W)

        tb.Label(filtro_frame, text="Data Fim (DD/MM/YYYY):").grid(row=0, column=2, sticky=tk.W, padx=5, pady=3)
        entrada_data_fim = tb.Entry(filtro_frame, width=15)
        entrada_data_fim.insert(0, datetime.now().strftime('%d/%m/%Y'))
        entrada_data_fim.grid(row=0, column=3, padx=5, pady=3, sticky=tk.W)

        tb.Label(filtro_frame, text="Categoria:").grid(row=1, column=0, sticky=tk.W, padx=5, pady=3)
        # carregar categorias distintas
        try:
            categorias_rows = self.db.cursor.execute('SELECT DISTINCT categoria FROM livros WHERE categoria IS NOT NULL').fetchall()
            categorias = [c[0] for c in categorias_rows if c[0]]
        except Exception:
            categorias = []
        entrada_categoria = tb.Combobox(filtro_frame, values=[''] + categorias, width=30)
        entrada_categoria.grid(row=1, column=1, columnspan=3, padx=5, pady=3, sticky=tk.W)

        # Área para resultados (Treeview será recriado conforme relatório)
        result_container = tb.Frame(frame)
        result_container.grid(row=3, column=0, sticky=tk.NSEW, padx=2, pady=(8, 4))
        result_container.rowconfigure(0, weight=1)
        result_container.columnconfigure(0, weight=1)

        def limpar_resultados():
            for w in result_container.winfo_children():
                w.destroy()

        def gerar_relatorio_categoria():
            limpar_resultados()
            # parse datas
            try:
                data_ini = datetime.strptime(entrada_data_ini.get(), '%d/%m/%Y').strftime('%Y-%m-%d')
                data_fim = datetime.strptime(entrada_data_fim.get(), '%d/%m/%Y').strftime('%Y-%m-%d')
            except Exception:
                data_ini = data_fim = None

            categoria = entrada_categoria.get().strip() or None

            sql = '''
                SELECT l.titulo, l.categoria,
                       DATE(COALESCE(v.data_pagamento, v.data_venda)) as data,
                       SUM(iv.quantidade) as total
                FROM itens_venda iv
                JOIN vendas v ON iv.venda_id = v.id
                JOIN livros l ON iv.livro_id = l.id
                WHERE v.status = 'finalizado'
            '''
            params = []
            if data_ini and data_fim:
                sql += ' AND DATE(COALESCE(v.data_pagamento, v.data_venda)) BETWEEN ? AND ? '
                params.extend([data_ini, data_fim])
            if categoria:
                sql += ' AND l.categoria = ? '
                params.append(categoria)
            sql += '''
                GROUP BY l.titulo, l.categoria,
                         DATE(COALESCE(v.data_pagamento, v.data_venda))
                ORDER BY DATE(COALESCE(v.data_pagamento, v.data_venda)) DESC, total DESC
            '''

            try:
                self.db.cursor.execute(sql, params)
                rows = self.db.cursor.fetchall()
            except Exception as e:
                messagebox.showerror('Erro', str(e))
                rows = []

            cols = ["Livro", "Categoria", "Data", "Quantidade Vendida"]
            tree = tb.Treeview(result_container, columns=cols, show='headings')
            style = tb.Style()
            style.configure("Treeview", font=("Arial", 11), rowheight=24)
            style.configure("Treeview.Heading", font=("Arial", 11, "bold"))

            for c in cols:
                tree.column(c, anchor=tk.W, width=150)
                tree.heading(c, text=c, anchor=tk.W)

            vsb = tb.Scrollbar(result_container, orient=tk.VERTICAL, command=tree.yview)
            hsb = tb.Scrollbar(result_container, orient=tk.HORIZONTAL, command=tree.xview)
            tree.configure(yscrollcommand=vsb.set, xscrollcommand=hsb.set)
            tree.grid(row=0, column=0, sticky=tk.NSEW)
            vsb.grid(row=0, column=1, sticky=tk.NS)
            hsb.grid(row=1, column=0, sticky=tk.EW)

            for i, r in enumerate(rows):
                tag = 'par' if i % 2 == 0 else 'impar'
                tree.insert('', 'end', values=(r[0], r[1], r[2], r[3]), tags=(tag,))

            if not rows:
                messagebox.showinfo('Relatório', 'Nenhum registro encontrado para os filtros selecionados.')

        def gerar_relatorio_cliente():
            limpar_resultados()
            try:
                data_ini = datetime.strptime(entrada_data_ini.get(), '%d/%m/%Y').strftime('%Y-%m-%d')
                data_fim = datetime.strptime(entrada_data_fim.get(), '%d/%m/%Y').strftime('%Y-%m-%d')
            except Exception:
                data_ini = data_fim = None

            categoria = entrada_categoria.get().strip() or None

            sql = '''
                SELECT c.id, c.nome, l.categoria, DATE(v.data_venda) as data, SUM(iv.quantidade) as total
                FROM vendas v
                JOIN itens_venda iv ON iv.venda_id = v.id
                JOIN clientes c ON v.cliente_id = c.id
                JOIN livros l ON iv.livro_id = l.id
                WHERE v.status = 'finalizado'
            '''
            params = []
            if data_ini and data_fim:
                sql += ' AND DATE(v.data_venda) BETWEEN ? AND ? '
                params.extend([data_ini, data_fim])
            if categoria:
                sql += ' AND l.categoria = ? '
                params.append(categoria)
            sql += ' GROUP BY c.id, l.categoria, DATE(v.data_venda) ORDER BY total DESC'

            try:
                self.db.cursor.execute(sql, params)
                rows = self.db.cursor.fetchall()
            except Exception as e:
                messagebox.showerror('Erro', str(e))
                rows = []

            cols = ["Cliente ID", "Cliente", "Categoria", "Data", "Quantidade Comprada"]
            tree = tb.Treeview(result_container, columns=cols, show='headings')
            style = tb.Style()
            style.configure("Treeview", font=("Arial", 11), rowheight=24)
            style.configure("Treeview.Heading", font=("Arial", 11, "bold"))

            for c in cols:
                tree.column(c, anchor=tk.W, width=150)
                tree.heading(c, text=c, anchor=tk.W)

            vsb = tb.Scrollbar(result_container, orient=tk.VERTICAL, command=tree.yview)
            hsb = tb.Scrollbar(result_container, orient=tk.HORIZONTAL, command=tree.xview)
            tree.configure(yscrollcommand=vsb.set, xscrollcommand=hsb.set)
            tree.grid(row=0, column=0, sticky=tk.NSEW)
            vsb.grid(row=0, column=1, sticky=tk.NS)
            hsb.grid(row=1, column=0, sticky=tk.EW)

            for i, r in enumerate(rows):
                tag = 'par' if i % 2 == 0 else 'impar'
                tree.insert('', 'end', values=(r[0], r[1], r[2], r[3], r[4]), tags=(tag,))

            if not rows:
                messagebox.showinfo('Relatório', 'Nenhum registro encontrado para os filtros selecionados.')

        botoes_frame = tb.Frame(filtro_frame)
        botoes_frame.grid(row=2, column=0, columnspan=4, pady=(6, 2))
        tb.Button(botoes_frame, text="Relatório por Categoria", bootstyle=PRIMARY, command=gerar_relatorio_categoria).pack(side=tk.LEFT, padx=6)
        tb.Button(botoes_frame, text="Relatório por Cliente", bootstyle=PRIMARY, command=gerar_relatorio_cliente).pack(side=tk.LEFT, padx=6)
        tb.Button(botoes_frame, text="Voltar", bootstyle=SECONDARY, command=self.criar_tela_inicial).pack(side=tk.LEFT, padx=6)

    def tela_inventario(self):
        self.limpar_janela()
        
        frame = tb.Frame(self.root)
        frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        frame.columnconfigure(0, weight=1)
        frame.rowconfigure(2, weight=1)

        # --- TÍTULO ---
        tb.Label(frame, text="Inventário de Livros", font=("Arial", 20, "bold")).grid(
            row=0, column=0, sticky=tk.W, pady=(0, 15))

        # --- BLOCO: ENTRADA DE DADOS ---
        entrada_frame = tb.LabelFrame(frame, text="Adicionar Item ao Inventário")
        entrada_frame.grid(row=1, column=0, sticky=tk.EW, pady=(0, 10))
        entrada_frame.columnconfigure(1, weight=1)
        entrada_frame.columnconfigure(3, weight=1)

        # ISBN
        tb.Label(entrada_frame, text="ISBN:", font=("Arial", 10)).grid(
            row=0, column=0, sticky=tk.W, padx=10, pady=5)
        isbn_entry = tb.Entry(entrada_frame)
        isbn_entry.grid(row=0, column=1, sticky=tk.EW, padx=10, pady=5)

        # Quantidade
        tb.Label(entrada_frame, text="Quantidade:", font=("Arial", 10)).grid(
            row=0, column=2, sticky=tk.W, padx=10, pady=5)
        quantidade_entry = tb.Entry(entrada_frame, width=10)
        quantidade_entry.insert(0, "1")
        quantidade_entry.grid(row=0, column=3, sticky=tk.W, padx=10, pady=5)

        # Operação
        tb.Label(entrada_frame, text="Operação:", font=("Arial", 10)).grid(
            row=1, column=0, sticky=tk.W, padx=10, pady=5)
        operacao_var = tk.StringVar(value="Entrada")
        operacao_combo = tb.Combobox(entrada_frame, values=["Entrada", "Saída"], 
                                     textvariable=operacao_var, state="readonly", width=15)
        operacao_combo.grid(row=1, column=1, sticky=tk.W, padx=10, pady=5)

        # --- BOTÕES HORIZONTAIS ---
        botoes_frame = tb.Frame(frame)
        botoes_frame.grid(row=3, column=0, sticky=tk.EW, pady=(10, 0))

        def adicionar_item():
            isbn = isbn_entry.get().strip()
            quantidade_text = quantidade_entry.get().strip()

            if not isbn:
                messagebox.showwarning("Aviso", "Informe o ISBN.")
                return
            if not quantidade_text.isdigit() or int(quantidade_text) < 0:
                messagebox.showwarning("Aviso", "Quantidade inválida.")
                return

            quantidade = int(quantidade_text)
            livro = self.livro.buscar_exato_isbn(isbn)
            if not livro:
                messagebox.showerror("Erro", "Livro não encontrado com esse ISBN.")
                return

            ajuste = quantidade if operacao_var.get() == "Entrada" else -quantidade
            sucesso, msg = self.livro.adicionar_item_inventario_temp(livro[0], isbn, livro[1], ajuste)
            if not sucesso:
                messagebox.showerror("Erro", msg)
                return

            carregar_inventario()
            isbn_entry.delete(0, tk.END)
            quantidade_entry.delete(0, tk.END)
            quantidade_entry.insert(0, "1")
            messagebox.showinfo("Sucesso", "Item adicionado ao inventário temporário.")

        def limpar_inventario():
            sucesso, msg = self.livro.limpar_inventario_temp()
            if not sucesso:
                messagebox.showerror("Erro", msg)
                return
            inventario.clear()
            atualizar_tree()
            messagebox.showinfo("Sucesso", "Inventário temporário limpo.")

        def aplicar_inventario():
            if not inventario:
                messagebox.showinfo("Aviso", "Nenhum item de inventário para aplicar.")
                return

            scaneados = set(inventario.keys())

            # 1) Ajusta os livros inventariados para o valor do inventário
            for isbn, data in inventario.items():
                saldo_anterior = data['atual']
                novo_saldo = data['quantidade']
                if novo_saldo < 0:
                    messagebox.showwarning("Aviso", f"Quantidade negativa para {isbn}. Ajustando para 0.")
                    novo_saldo = 0

                sucesso, msg = self.livro.atualizar_quantidade_por_id(data['id'], novo_saldo)
                if sucesso:
                    self.livro.registrar_historico_inventario(
                        livro_id=data['id'],
                        isbn=isbn,
                        titulo=data['titulo'],
                        operacao="Inventário",
                        quantidade=novo_saldo,
                        saldo_anterior=saldo_anterior,
                        saldo_posterior=novo_saldo
                    )

            # 2) Zera os livros não inventariados
            for livro in self.livro.listar():
                if livro[4] not in scaneados:  # livro[4] = isbn
                    book_id = livro[0]
                    saldo_anterior = livro[5]
                    if saldo_anterior != 0:
                        self.livro.atualizar_quantidade_por_id(book_id, 0)
                        self.livro.registrar_historico_inventario(
                            livro_id=book_id,
                            isbn=livro[4],
                            titulo=livro[1],
                            operacao="Inventário - não inventariado",
                            quantidade=0,
                            saldo_anterior=saldo_anterior,
                            saldo_posterior=0
                        )

            sucesso, msg = self.livro.limpar_inventario_temp()
            if not sucesso:
                messagebox.showerror("Erro", msg)
                return

            messagebox.showinfo("Sucesso", "Inventário aplicado com sucesso. Estoque atualizado.")
            inventario.clear()
            atualizar_tree()

        tb.Button(botoes_frame, text="Bipar/Adicionar", bootstyle=SUCCESS,
                 command=adicionar_item).pack(side=tk.LEFT, padx=3)
        tb.Button(botoes_frame, text="Limpar Inventário", bootstyle=WARNING,
                 command=limpar_inventario).pack(side=tk.LEFT, padx=3)
        tb.Button(botoes_frame, text="Aplicar Inventário", bootstyle=PRIMARY,
                 command=aplicar_inventario).pack(side=tk.LEFT, padx=3)
        tb.Button(botoes_frame, text="Voltar", bootstyle=SECONDARY,
                 command=self.criar_tela_inicial).pack(side=tk.LEFT, padx=3)

        # Dicionário de inventário temporário
        inventario = {}

        # --- TREEVIEW COM SCROLLBARS ---
        tree_container = tb.Frame(frame)
        tree_container.grid(row=2, column=0, sticky=tk.NSEW, pady=(0, 10))
        tree_container.rowconfigure(0, weight=1)
        tree_container.columnconfigure(0, weight=1)

        tree = tb.Treeview(tree_container, columns=["ISBN", "Título", "Quantidade", "Estoque Atual"], height=15)
        
        style = tb.Style()
        style.configure("Treeview", font=("Arial", 11), rowheight=25)
        style.configure("Treeview.Heading", font=("Arial", 11, "bold"))

        tree_scroll_y = tb.Scrollbar(tree_container, orient=tk.VERTICAL, command=tree.yview)
        tree_scroll_x = tb.Scrollbar(tree_container, orient=tk.HORIZONTAL, command=tree.xview)
        tree.configure(yscrollcommand=tree_scroll_y.set, xscrollcommand=tree_scroll_x.set)

        tree.grid(row=0, column=0, sticky="nsew")
        tree_scroll_y.grid(row=0, column=1, sticky="ns")
        tree_scroll_x.grid(row=1, column=0, sticky="ew")

        tree.column("#0", width=0, stretch=tk.NO)
        for col in ["ISBN", "Título", "Quantidade", "Estoque Atual"]:
            tree.column(col, anchor=tk.W, width=150, minwidth=100, stretch=True)
            tree.heading(col, text=col, anchor=tk.W)

        def carregar_inventario():
            nonlocal inventario
            inventario = {}
            for livro_id, isbn, titulo, quantidade in self.livro.listar_inventario_temp():
                livro = self.livro.buscar_por_id(livro_id)
                atual = livro[4] if livro else 0
                inventario[isbn] = {
                    'id': livro_id,
                    'titulo': titulo,
                    'quantidade': quantidade,
                    'atual': atual
                }
            atualizar_tree()

        def atualizar_tree():
            for i in tree.get_children():
                tree.delete(i)
            for i, (isbn, data) in enumerate(inventario.items()):
                tag = "par" if i % 2 == 0 else "impar"
                tree.insert("", "end", values=(isbn, data['titulo'], data['quantidade'], data['atual']), tags=(tag,))

        carregar_inventario()

    def nova_venda(self):
        # Janela para selecionar vendedor e cliente (com busca por nome e botão de novo cliente)
        janela = tk.Toplevel(self.root)
        janela.title("Nova Venda")
        largura_tela = janela.winfo_screenwidth()
        altura_tela = janela.winfo_screenheight()
        largura = min(720, max(560, int(largura_tela * 0.42)))
        altura = min(520, max(400, int(altura_tela * 0.52)))
        pos_x = max(0, (largura_tela - largura) // 2)
        pos_y = max(0, (altura_tela - altura) // 2)
        janela.geometry(f"{largura}x{altura}+{pos_x}+{pos_y}")
        janela.minsize(500, 380)
        janela.resizable(True, True)
        janela.transient(self.root)

        frame = tb.Frame(janela, padding=(28, 24))
        frame.pack(fill=tk.BOTH, expand=True)
        frame.columnconfigure(0, weight=1)
        frame.rowconfigure(4, weight=1)

        tb.Label(frame, text="Nova Venda", font=("Arial", 20, "bold"),
                 bootstyle=PRIMARY).grid(row=0, column=0, sticky=tk.W, pady=(0, 20))

        tb.Label(frame, text="Vendedor", font=("Arial", 13, "bold")).grid(
            row=1, column=0, sticky=tk.W, pady=(0, 6))
        vendedores = self.vendedor.listar()
        vendedor_combo = tb.Combobox(frame, values=[f"{v[0]} - {v[1]}" for v in vendedores], state="readonly")
        vendedor_combo.configure(font=("Arial", 13))
        vendedor_combo.grid(row=2, column=0, sticky="ew", pady=(0, 18), ipady=4)

        tb.Label(frame, text="Cliente", font=("Arial", 13, "bold")).grid(
            row=3, column=0, sticky=tk.NW, pady=(0, 6))

        # linha com Combobox (auto-complete) + botão 'Novo Cliente'
        cliente_row = tb.Frame(frame)
        cliente_row.grid(row=4, column=0, sticky="new", pady=(0, 20))
        cliente_row.columnconfigure(0, weight=1)

        clientes = self.cliente.listar()
        cliente_combo = tb.Combobox(cliente_row, values=[f"{c[0]} - {c[1]}" for c in clientes], state="normal")
        cliente_combo.configure(font=("Arial", 13))
        cliente_combo.grid(row=0, column=0, sticky="ew", padx=(0, 10), ipady=4)

        def abrir_novo_cliente():
            # Abre o formulário de adicionar cliente e atualiza a combobox ao retornar
            def refresh_and_select():
                atualizar_clientes()
                ultimo = self.cliente.ultimo_adicionado()
                if ultimo:
                    cliente_combo.set(f"{ultimo[0]} - {ultimo[1]}")
                # Garante que a janela "Nova Venda" volte ao topo e receba foco
                try:
                    janela.deiconify()
                    janela.lift()
                    janela.focus_force()
                except Exception:
                    pass

            self.janela_formulario("Adicionar Cliente",
                                  [("Nome", "entry", ""), ("Email", "entry", ""), ("Telefone", "entry", ""), ("Endereco", "entry", "")],
                                  lambda dados: self.cliente.adicionar(*dados),
                                  refresh_and_select,
                                  parent=janela)

        tb.Button(cliente_row, text="Novo Cliente", command=abrir_novo_cliente,
              bootstyle=INFO, padding=(12, 8)).grid(row=0, column=1, sticky=tk.E)

        def atualizar_clientes(termo=""):
            if termo and termo.strip():
                encontrados = self.cliente.buscar_por_nome(termo.strip())
            else:
                encontrados = self.cliente.listar()
            valores = [f"{c[0]} - {c[1]}" for c in encontrados]
            cliente_combo['values'] = valores

        def on_cliente_key(event=None):
            texto = cliente_combo.get().strip()
            atualizar_clientes(texto)
            if cliente_combo['values']:
                cliente_combo.after_idle(
                    lambda: cliente_combo.tk.call("ttk::combobox::Post", cliente_combo._w)
                )
            else:
                cliente_combo.tk.call("ttk::combobox::Unpost", cliente_combo._w)

        # Bind para buscar enquanto digita
        cliente_combo.bind('<KeyRelease>', on_cliente_key)

        def iniciar():
            if not vendedor_combo.get():
                messagebox.showwarning("Aviso", "Selecione um vendedor!")
                return

            # Determinar cliente selecionado
            cliente_text = cliente_combo.get().strip()
            cliente_id = None
            if ' - ' in cliente_text:
                try:
                    cliente_id = int(cliente_text.split(' - ')[0])
                except Exception:
                    cliente_id = None
            else:
                # tenta buscar pelo nome digitado e pega o primeiro resultado
                if cliente_text:
                    encontrados = self.cliente.buscar_por_nome(cliente_text)
                    if encontrados:
                        cliente_id = encontrados[0][0]

            if not cliente_id:
                messagebox.showwarning("Aviso", "Selecione ou informe um cliente válido!")
                return

            vendedor_id = int(vendedor_combo.get().split(" - ")[0])

            sucesso, venda_id, msg = self.venda.criar_venda(vendedor_id, cliente_id)
            if sucesso:
                janela.destroy()
                self.editar_venda(venda_id)
            else:
                messagebox.showerror("Erro", msg)

        tb.Button(frame, text="Iniciar Venda", command=iniciar,
                  bootstyle=SUCCESS, padding=(18, 10)).grid(
                      row=5, column=0, sticky=tk.EW, pady=(8, 0))

        janela.bind("<Return>", lambda event: iniciar())
        janela.bind("<Escape>", lambda event: janela.destroy())
        janela.after(100, lambda: vendedor_combo.focus_set())
    
    def editar_venda(self, venda_id):
        self.venda_id_atual = venda_id
        self.limpar_janela()
        frame = tb.Frame(self.root)
        frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        venda = self.venda.obter_venda(venda_id)
        vendedor = self.vendedor.buscar_por_id(venda[1])
        cliente = self.cliente.buscar_por_id(venda[2])
        
        info = f"Venda #{venda_id} | Vendedor: {vendedor[1]} | Cliente: {cliente[1]} | Status: {venda[4].upper()}"
        tb.Label(frame, text=info, font=("Arial", 11, "bold")).pack(pady=10)
        
        # Área de itens
        items_frame = tb.LabelFrame(frame, text="Itens da Venda")
        items_frame.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        
        self.tree_itens = tb.Treeview(items_frame, columns=["ID", "Livro", "Qtd", "Pago", "Saldo", "Preco", "Subtotal"], height=10)
        self.tree_itens.column("#0", width=0, stretch=tk.NO)
        for col in ["ID", "Livro", "Qtd", "Pago", "Saldo", "Preco", "Subtotal"]:
            self.tree_itens.column(col, anchor=tk.W, width=100)
            self.tree_itens.heading(col, text=col, anchor=tk.W)
        
        itens = self.venda.listar_itens_venda(venda_id)
        for item in itens:
            saldo = item[3] - item[6]
            self.tree_itens.insert("", "end", values=(item[0], item[2], item[3], item[6], saldo,
                                                        f"{item[4]:.2f}", f"{item[5]:.2f}"))
        
        scrollbar = tb.Scrollbar(items_frame, orient=tk.VERTICAL, command=self.tree_itens.yview)
        self.tree_itens.configure(yscroll=scrollbar.set)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        self.tree_itens.pack(fill=tk.BOTH, expand=True)
        
        # Botões de ação
        botoes_itens = tb.Frame(frame)
        botoes_itens.pack(pady=10)
        tb.Button(botoes_itens, text="Adicionar Livro", command=self.adicionar_livro_venda,
                bootstyle=PRIMARY, width=18, padding=(10, 10)).pack(side=tk.LEFT, padx=5)
        tb.Button(botoes_itens, text="Editar Item", command=self.editar_item_venda,
                bootstyle=WARNING, width=18, padding=(10, 10)).pack(side=tk.LEFT, padx=5)
        tb.Button(botoes_itens, text="Remover Item", command=self.remover_item_venda,
                bootstyle=DANGER, width=18, padding=(10, 10)).pack(side=tk.LEFT, padx=5)
        tb.Button(botoes_itens, text="Dar Baixa Parcial", command=self.pagar_item_venda,
                bootstyle=SUCCESS, width=18, padding=(10, 10)).pack(side=tk.LEFT, padx=5)
        
        # Total e pagamento
        total_frame = tb.Frame(frame)
        total_frame.pack(fill=tk.X, pady=10)
        
        venda_atualizada = self.venda.obter_venda(venda_id)
        tb.Label(total_frame, text=f"Total: R$ {venda_atualizada[5]:.2f}", font=("Arial", 14, "bold")).pack(side=tk.LEFT, padx=20)
        
        botoes_finais = tb.Frame(frame)
        botoes_finais.pack(pady=10)
        
        if venda[4] in ('aberto', 'parcial'):
            tb.Button(botoes_finais, text="Finalizar e Pagar", command=self.finalizar_venda,
                      bootstyle=SUCCESS, width=18, padding=(10, 10)).pack(side=tk.LEFT, padx=5)
            tb.Button(botoes_finais, text="Deixar em Aberto", command=self.tela_vendas,
                      bootstyle=INFO, width=18, padding=(10, 10)).pack(side=tk.LEFT, padx=5)
        else:
            tb.Label(botoes_finais, text=f"Pagamento: {venda[6]} em {venda[7]}", font=("Arial", 10)).pack(side=tk.LEFT, padx=20)
        
        tb.Button(botoes_finais, text="Voltar", command=self.tela_vendas,
              bootstyle=SECONDARY, width=18, padding=(10, 10)).pack(side=tk.LEFT, padx=5)
        
        self.atualizar_venda_display = lambda: self.editar_venda(venda_id)

    def pagar_item_venda(self):
        """Registra a baixa de uma quantidade do item selecionado."""
        selecao = self.tree_itens.selection()
        if not selecao:
            messagebox.showwarning("Aviso", "Selecione um item para dar baixa.")
            return

        valores = self.tree_itens.item(selecao[0])['values']
        item_id = int(valores[0])
        saldo = int(valores[4])
        if saldo <= 0:
            messagebox.showinfo("Pagamento", "Este item já está totalmente pago.")
            return

        janela = tk.Toplevel(self.root)
        janela.title("Baixa parcial do item")
        largura_tela = janela.winfo_screenwidth()
        altura_tela = janela.winfo_screenheight()
        largura = min(480, max(400, largura_tela - 80))
        altura = min(320, max(280, altura_tela - 120))
        janela.geometry(f"{largura}x{altura}")
        janela.minsize(400, 280)
        janela.resizable(True, True)
        frame = tb.Frame(janela, padding=15)
        frame.pack(fill=tk.BOTH, expand=True)

        tb.Label(frame, text=f"{valores[1]}\nSaldo: {saldo} unidade(s)",
                 font=("Arial", 11, "bold"), justify=tk.LEFT).pack(anchor=tk.W, pady=(0, 12))
        tb.Label(frame, text="Quantidade paga:").pack(anchor=tk.W)
        entrada_qtd = tb.Entry(frame)
        entrada_qtd.insert(0, str(saldo))
        entrada_qtd.pack(fill=tk.X, pady=(3, 10))
        tb.Label(frame, text="Forma de pagamento:").pack(anchor=tk.W)
        metodo = tb.Combobox(frame, values=["DINHEIRO", "PIX", "CARTAO DE DEBITO", "CARTAO DE CREDITO"],
                             state="readonly")
        metodo.set("PIX")
        metodo.pack(fill=tk.X, pady=(3, 15))

        def confirmar():
            try:
                quantidade = int(entrada_qtd.get())
            except ValueError:
                messagebox.showerror("Erro", "Informe uma quantidade válida.")
                return
            sucesso, mensagem = self.venda.registrar_pagamento_item(item_id, quantidade, metodo.get())
            if sucesso:
                janela.destroy()
                messagebox.showinfo("Pagamento", mensagem)
                self.atualizar_venda_display()
            else:
                messagebox.showerror("Erro", mensagem)

        botoes = tb.Frame(frame)
        botoes.pack(fill=tk.X, pady=(0, 2))
        botoes.columnconfigure(0, weight=1)
        botoes.columnconfigure(1, weight=1)
        tb.Button(botoes, text="Confirmar baixa", command=confirmar, bootstyle=SUCCESS).grid(
            row=0, column=0, padx=(0, 8), sticky="ew")
        tb.Button(botoes, text="Cancelar", command=janela.destroy, bootstyle=SECONDARY).grid(
            row=0, column=1, sticky="ew")
    
    def adicionar_livro_venda(self):
        janela = tk.Toplevel(self.root)
        janela.title("Adicionar Livro")
        janela.geometry("720x520")
        janela.minsize(520, 360)
        janela.resizable(True, True)

        frame = tb.Frame(janela, padding=10)
        frame.pack(fill=tk.BOTH, expand=True)
        frame.columnconfigure(0, weight=1)
        frame.rowconfigure(1, weight=1)

        # Campos de pesquisa organizados em grid responsivo
        procura_frame = tb.Frame(frame)
        procura_frame.grid(row=0, column=0, sticky="ew", pady=(0, 8))
        procura_frame.columnconfigure(1, weight=1)

        tb.Label(procura_frame, text="Nome do Livro:", font=("Arial", 10)).grid(row=0, column=0, sticky=tk.W, pady=2)
        entrada_nome_livro = tb.Entry(procura_frame)
        entrada_nome_livro.grid(row=0, column=1, padx=5, pady=2, sticky="ew")

        tb.Label(procura_frame, text="ISBN:", font=("Arial", 10)).grid(row=1, column=0, sticky=tk.W, pady=2)
        entrada_isbn_livro = tb.Entry(procura_frame)
        entrada_isbn_livro.grid(row=1, column=1, padx=5, pady=2, sticky="ew")

        buscar_btn = tb.Button(procura_frame, text="Buscar", bootstyle=INFO)
        buscar_btn.grid(row=0, column=2, rowspan=2, padx=(8,0), sticky="ns")

        # Lista de livros encontrados com scrollbars e comportamento responsivo
        tree_container = tb.Frame(frame)
        tree_container.grid(row=1, column=0, sticky="nsew")
        tree_container.columnconfigure(0, weight=1)
        tree_container.rowconfigure(0, weight=1)

        style = tb.Style()
        style.configure("Treeview", font=("Arial", 11), rowheight=26)
        style.configure("Treeview.Heading", font=("Arial", 11, "bold"))

        tree_livros = tb.Treeview(tree_container, columns=["ID", "Titulo", "ISBN", "Quantidade", "Preco"], show='headings')
        for col in ["ID", "Titulo", "ISBN", "Quantidade", "Preco"]:
            tree_livros.heading(col, text=col)
            tree_livros.column(col, anchor=tk.W, minwidth=80, width=140, stretch=True)

        vsb = tb.Scrollbar(tree_container, orient=tk.VERTICAL, command=tree_livros.yview)
        hsb = tb.Scrollbar(tree_container, orient=tk.HORIZONTAL, command=tree_livros.xview)
        tree_livros.configure(yscrollcommand=vsb.set, xscrollcommand=hsb.set)

        tree_livros.grid(row=0, column=0, sticky="nsew")
        vsb.grid(row=0, column=1, sticky="ns")
        hsb.grid(row=1, column=0, sticky="ew")

        # Quantidade e preço alinhados à direita para clareza
        form_frame = tb.Frame(frame)
        form_frame.grid(row=2, column=0, sticky="ew", pady=8)
        form_frame.columnconfigure(0, weight=1)
        campos_frame = tb.Frame(form_frame)
        campos_frame.grid(row=0, column=0, sticky="e")

        tb.Label(campos_frame, text="Quantidade:").grid(row=0, column=0, padx=5)
        entrada_qtd = tb.Entry(campos_frame, width=8)
        entrada_qtd.grid(row=0, column=1, padx=5)
        entrada_qtd.insert(0, "1")

        tb.Label(campos_frame, text="Preço Unitário:").grid(row=0, column=2, padx=5)
        entrada_preco = tb.Entry(campos_frame, width=12)
        entrada_preco.grid(row=0, column=3, padx=5)

        # Função de busca populando o Treeview
        def buscar():
            tree_livros.delete(*tree_livros.get_children())
            termo_nome = entrada_nome_livro.get().strip()
            termo_isbn = entrada_isbn_livro.get().strip()

            termo = termo_isbn or termo_nome
            if termo is not None and termo != "":
                livros = self.venda.buscar_livro(termo)
                for livro in livros:
                    tree_livros.insert("", "end", values=(livro[0], livro[1], livro[2], livro[4], f"R$ {livro[3]:.2f}"))

        def buscar_auto(event=None):
            buscar()

        buscar_btn.config(command=buscar)
        entrada_nome_livro.bind('<KeyRelease>', buscar_auto)
        entrada_isbn_livro.bind('<KeyRelease>', buscar_auto)

        # Preenche o preço automaticamente ao selecionar o livro na lista
        def preencher_preco(event=None):
            selecao = tree_livros.selection()
            if selecao:
                item = tree_livros.item(selecao)['values']
                preco_text = str(item[4]).replace("R$ ", "").replace(",", ".")
                entrada_preco.delete(0, tk.END)
                entrada_preco.insert(0, preco_text)

        tree_livros.bind('<<TreeviewSelect>>', preencher_preco)

        # Confirmar inclusão
        def confirmar_inclusao():
            selecao = tree_livros.selection()
            if not selecao:
                messagebox.showwarning("Aviso", "Selecione um livro na lista!")
                return
            try:
                livro_id = int(tree_livros.item(selecao)['values'][0])
                quantidade = int(entrada_qtd.get())
                preco = float(entrada_preco.get().replace(',', '.'))

                sucesso, msg = self.venda.adicionar_item(self.venda_id_atual, livro_id, quantidade, preco)
                if sucesso:
                    messagebox.showinfo("Sucesso", "Item adicionado!")
                    janela.destroy()
                    self.atualizar_venda_display()
                else:
                    messagebox.showerror("Erro", msg)
            except ValueError:
                messagebox.showerror("Erro", "Quantidade ou Preço inválidos!")

        # Botões finais alinhados e com comportamento responsivo
        button_frame = tb.Frame(frame)
        button_frame.grid(row=3, column=0, sticky="ew", pady=(6,0))
        button_frame.columnconfigure((0,1), weight=1)

        tb.Button(button_frame, text="✅ Incluir na Venda", command=confirmar_inclusao, bootstyle=SUCCESS).grid(row=0, column=0, padx=5, sticky="ew")
        tb.Button(button_frame, text="❌ Cancelar", command=janela.destroy, bootstyle=SECONDARY).grid(row=0, column=1, padx=5, sticky="ew")
    
    def incluir_livro_rapido(self):
        """Método rápido para incluir livro diretamente na venda"""
        janela = tk.Toplevel(self.root)
        janela.title("Incluir Livro na Venda")
        janela.geometry("400x250")
        janela.resizable(False, False)
        
        frame = tb.Frame(janela)
        frame.pack(fill=tk.BOTH, expand=True, padx=15, pady=15)
        
        # Título
        tb.Label(frame, text="Incluir Livro na Venda", font=("Arial", 12, "bold")).pack(pady=(0, 15))
        
        # Campo de busca rápida
        busca_frame = tb.Frame(frame)
        busca_frame.pack(fill=tk.X, pady=(0, 10))
        
        tb.Label(busca_frame, text="Buscar Livro:", font=("Arial", 10)).pack(anchor=tk.W)
        entrada_busca = tb.Entry(busca_frame, width=35)
        entrada_busca.pack(pady=(5, 0))
        entrada_busca.focus()
        
        # Combobox para seleção rápida
        livro_var = tk.StringVar()
        livros_combo = tb.Combobox(frame, textvariable=livro_var, state="readonly", width=35)
        livros_combo.pack(pady=(0, 10))
        
        # Atualizar lista de livros baseada na busca
        def atualizar_livros(event=None):
            termo = entrada_busca.get().strip()
            if len(termo) >= 2:  # Buscar apenas se tiver pelo menos 2 caracteres
                livros = self.venda.buscar_livro(termo)
                valores = [f"{livro[0]} - {livro[1]} (ISBN: {livro[2]}) - R$ {livro[3]:.2f}" for livro in livros]
                livros_combo['values'] = valores
                if valores:
                    livros_combo.event_generate('<Button-1>')  # Abrir dropdown
        
        entrada_busca.bind('<KeyRelease>', atualizar_livros)
        
        # Frame para quantidade
        qtd_frame = tb.Frame(frame)
        qtd_frame.pack(fill=tk.X, pady=(0, 15))
        
        tb.Label(qtd_frame, text="Quantidade:", font=("Arial", 10)).pack(side=tk.LEFT)
        entrada_qtd = tb.Entry(qtd_frame, width=10)
        entrada_qtd.pack(side=tk.LEFT, padx=(5, 0))
        entrada_qtd.insert(0, "1")
        
        # Botões
        button_frame = tb.Frame(frame)
        button_frame.pack(fill=tk.X, pady=(10, 0))
        
        def incluir():
            if not livro_var.get():
                messagebox.showwarning("Aviso", "Selecione um livro!")
                return
            
            try:
                # Extrair ID do livro da string selecionada
                livro_info = livro_var.get()
                livro_id = int(livro_info.split(" - ")[0])
                quantidade = int(entrada_qtd.get())
                
                # Buscar preço do livro
                livros = self.venda.buscar_livro("")
                preco = None
                for livro in livros:
                    if livro[0] == livro_id:
                        preco = livro[3]
                        break
                
                if preco is None:
                    messagebox.showerror("Erro", "Não foi possível obter o preço do livro!")
                    return
                
                sucesso, msg = self.venda.adicionar_item(self.venda_id_atual, livro_id, quantidade, preco)
                
                if sucesso:
                    messagebox.showinfo("Sucesso", f"Livro incluído na venda!\n{msg}")
                    # Manter janela aberta para inclusão de mais livros
                    self.atualizar_venda_display()
                    entrada_busca.delete(0, tk.END)
                    livros_combo.set('')
                    entrada_qtd.delete(0, tk.END)
                    entrada_qtd.insert(0, "1")
                    
            except ValueError:
                messagebox.showerror("Erro", "Quantidade deve ser um número válido!")
        
        tb.Button(button_frame, text="Incluir na Venda", command=incluir).pack(side=tk.LEFT, padx=(0, 10))
        tb.Button(button_frame, text="Cancelar", command=janela.destroy).pack(side=tk.LEFT)
        
        # Bind Enter para incluir rapidamente
        janela.bind('<Return>', lambda e: incluir())
        janela.bind('<Escape>', lambda e: janela.destroy())
    
    def editar_item_venda(self):
        if not self.tree_itens.selection():
            messagebox.showwarning("Aviso", "Selecione um item!")
            return
        
        item_id = int(self.tree_itens.item(self.tree_itens.selection())['values'][0])
        
        janela = tk.Toplevel(self.root)
        janela.title("Editar Item")
        janela.geometry("300x200")
        
        frame = tb.Frame(janela)
        frame.pack(fill=tk.BOTH, expand=True, padx=15, pady=15)
        
        item_completo = self.db.cursor.execute('SELECT * FROM itens_venda WHERE id=?', (item_id,)).fetchone()
        
        tb.Label(frame, text="Quantidade:", font=("Arial", 10)).pack(anchor=tk.W, pady=(10, 2))
        entrada_qtd = tb.Entry(frame, width=20)
        entrada_qtd.insert(0, str(item_completo[3]))
        entrada_qtd.pack(pady=(0, 15), fill=tk.X)
        
        tb.Label(frame, text="Preco Unitario:", font=("Arial", 10)).pack(anchor=tk.W, pady=(10, 2))
        entrada_preco = tb.Entry(frame, width=20)
        entrada_preco.insert(0, str(item_completo[4]))
        entrada_preco.pack(pady=(0, 15), fill=tk.X)
        
        def atualizar():
            try:
                quantidade = int(entrada_qtd.get())
                preco = float(entrada_preco.get())
                
                sucesso, msg = self.venda.atualizar_item(item_id, quantidade, preco)
                messagebox.showinfo("Resultado", msg)
                
                if sucesso:
                    janela.destroy()
                    self.atualizar_venda_display()
            except ValueError:
                messagebox.showerror("Erro", "Valores inválidos!")
        
        tb.Button(frame, text="Atualizar", command=atualizar).pack(pady=15)
    
    def remover_item_venda(self):
        if not self.tree_itens.selection():
            messagebox.showwarning("Aviso", "Selecione um item!")
            return
        
        item_id = int(self.tree_itens.item(self.tree_itens.selection())['values'][0])
        
        if messagebox.askyesno("Confirmacao", "Remover este item?"):
            sucesso, msg = self.venda.remover_item(item_id)
            messagebox.showinfo("Resultado", msg)
            if sucesso:
                self.atualizar_venda_display()
    
    def finalizar_venda(self):
        janela = tk.Toplevel(self.root)
        janela.title("Finalizar Venda - Pagamento")
        janela.geometry("450x500")
        janela.minsize(400, 450)
        
        # Container com scroll para responsividade
        container = tb.Frame(janela)
        container.pack(fill=tk.BOTH, expand=True)
        
        canvas = tk.Canvas(container)
        scrollbar = tb.Scrollbar(container, orient=tk.VERTICAL, command=canvas.yview)
        content_frame = tb.Frame(canvas)
        
        content_frame.bind("<Configure>", lambda e: canvas.configure(scrollregion=canvas.bbox("all")))
        canvas.create_window((0, 0), window=content_frame, anchor="nw")
        canvas.configure(yscrollcommand=scrollbar.set)
        
        canvas.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        
        # Título e total
        header_frame = tb.Frame(content_frame)
        header_frame.pack(fill=tk.X, pady=(20, 10), padx=20)
        
        tb.Label(header_frame, text=f"Total da Venda: R$ {self.venda.obter_venda(self.venda_id_atual)[5]:.2f}", 
                 font=("Arial", 16, "bold"), foreground="green").pack()
        
        # Seção de métodos de pagamento
        payment_frame = tb.LabelFrame(content_frame, text="Selecione o Método de Pagamento")
        #payment_frame.pack(fill=tk.BOTH, expand=True, padx=20, pady=10)
        payment_frame.pack(fill=X, padx=10, pady=10, ipady=10, ipadx=10)
        
        metodo_var = tk.StringVar(value="PIX")
        
        # Métodos de pagamento com imagens
        metodos = [
            ("PIX", "PIX - Pagamento Instantâneo"),
            ("CARTAO DE DEBITO", "Cartão de Débito"),
            ("CARTAO DE CREDITO", "Cartão de Crédito"),
            ("DINHEIRO", "Dinheiro")
        ]
        
        for metodo, descricao in metodos:
            metodo_frame = tb.Frame(payment_frame)
            metodo_frame.pack(fill=tk.X, pady=5)
            
            # Imagem do método de pagamento
            if self.icones_pagamento.get(metodo):
                imagem_label = tb.Label(metodo_frame, image=self.icones_pagamento[metodo])
            else:
                # Fallback para emoji se imagem não carregou
                emoji = {"PIX": "📱", "CARTAO DE DEBITO": "💳", "CARTAO DE CREDITO": "💳", "DINHEIRO": "💵"}.get(metodo, "💰")
                imagem_label = tb.Label(metodo_frame, text=emoji, font=("Arial", 20))
            
            imagem_label.pack(side=tk.LEFT, padx=(0, 10))
            
            # Radiobutton com descrição
            rb = tb.Radiobutton(metodo_frame, text=descricao, variable=metodo_var, value=metodo)
            rb.pack(side=tk.LEFT, fill=tk.X, expand=True)
        
        # Botão de confirmação
        button_frame = tb.Frame(content_frame)
        button_frame.pack(fill=tk.X, pady=20, padx=20)
        
        def confirmar_pagamento():
            venda = self.venda.obter_venda(self.venda_id_atual)
            sucesso, msg = self.venda.finalizar_venda(self.venda_id_atual, metodo_var.get())
            messagebox.showinfo("Resultado", msg)
            
            if sucesso:
                janela.destroy()
                messagebox.showinfo("Sucesso", "Venda finalizada com sucesso!")
                self.tela_vendas()
        
        tb.Button(button_frame, text="Confirmar Pagamento", command=confirmar_pagamento).pack(fill=tk.X, expand=True)
    
    def continuar_venda(self):
        vendas_abertas = self.venda.listar_vendas_abertas()
        
        if not vendas_abertas:
            messagebox.showinfo("Aviso", "Nenhuma venda aberta para continuar!")
            return
        
        janela = tk.Toplevel(self.root)
        janela.title("Continuar Venda")
        janela.geometry("700x450")
        janela.minsize(600, 380)

        frame = tb.Frame(janela)
        frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        frame.columnconfigure(0, weight=1)
        frame.rowconfigure(0, weight=0)
        frame.rowconfigure(1, weight=1)
        frame.rowconfigure(2, weight=0)

        tb.Label(frame, text="Vendas Abertas", font=("Arial", 14, "bold")).grid(
            row=0, column=0, sticky=tk.W, pady=(0, 10))

        tree_container = tb.Frame(frame)
        tree_container.grid(row=1, column=0, sticky=tk.NSEW, pady=(0, 10))
        tree_container.rowconfigure(0, weight=1)
        tree_container.columnconfigure(0, weight=1)

        tree = tb.Treeview(tree_container, columns=["ID", "Vendedor", "Cliente", "Data", "Total"], height=12)
        tree.column("#0", width=0, stretch=tk.NO)
        for col in ["ID", "Vendedor", "Cliente", "Data", "Total"]:
            tree.column(col, anchor=tk.W, width=120, minwidth=100, stretch=True)
            tree.heading(col, text=col, anchor=tk.W)

        tree_scroll_y = tb.Scrollbar(tree_container, orient=tk.VERTICAL, command=tree.yview)
        tree_scroll_x = tb.Scrollbar(tree_container, orient=tk.HORIZONTAL, command=tree.xview)
        tree.configure(yscrollcommand=tree_scroll_y.set, xscrollcommand=tree_scroll_x.set)
        
        tree.grid(row=0, column=0, sticky=tk.NSEW)
        tree_scroll_y.grid(row=0, column=1, sticky=tk.NS)
        tree_scroll_x.grid(row=1, column=0, sticky=tk.EW)

        for venda in vendas_abertas:
            tree.insert("", "end", values=(venda[0], venda[1], venda[2], venda[3][:10], f"R$ {venda[4]:.2f}"))

        btn_frame = tb.Frame(frame)
        btn_frame.grid(row=2, column=0, sticky=tk.E, pady=(10, 0))

        def abrir_venda():
            if not tree.selection():
                messagebox.showwarning("Aviso", "Selecione uma venda!")
                return

            venda_id = int(tree.item(tree.selection())['values'][0])
            janela.destroy()
            self.editar_venda(venda_id)
        def remover_venda():
            if not tree.selection():
                messagebox.showwarning("Aviso", "Selecione uma venda para remover!")
                return

            venda_id = int(tree.item(tree.selection())['values'][0])
            if not messagebox.askyesno("Confirmacao", "Deseja realmente remover uma venda?"):
                return

            sucesso, msg = self.venda.deletar_venda(venda_id)
            messagebox.showinfo("Resultado", msg)
            if sucesso:
                # Recarregar lista de vendas abertas na tree
                try:
                    for i in tree.get_children():
                        tree.delete(i)
                    novas = self.venda.listar_vendas_abertas()
                    for venda in novas:
                        tree.insert("", "end", values=(venda[0], venda[1], venda[2], venda[3][:10], f"R$ {venda[4]:.2f}"))
                except Exception:
                    pass

        tb.Button(btn_frame, text="Continuar", bootstyle=SUCCESS, command=abrir_venda).pack(side=tk.LEFT, padx=5)
        tb.Button(btn_frame, text="Remover", bootstyle=DANGER, command=remover_venda).pack(side=tk.LEFT, padx=5)
        tb.Button(btn_frame, text="Cancelar", bootstyle=SECONDARY, command=janela.destroy).pack(side=tk.LEFT, padx=5)
    
    def historico_vendas(self):
        vendas = self.venda.listar_todas_vendas()
        
        self.limpar_janela()
        frame = tb.Frame(self.root)
        frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)

        canvas = tk.Canvas(frame)
        scroll_y = tb.Scrollbar(frame, orient=tk.VERTICAL, command=canvas.yview)
        inner = tb.Frame(canvas)

        inner.bind("<Configure>", lambda e: canvas.configure(scrollregion=canvas.bbox("all")))
        canvas.create_window((0, 0), window=inner, anchor="nw")
        canvas.configure(yscrollcommand=scroll_y.set)

        canvas.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scroll_y.pack(side=tk.RIGHT, fill=tk.Y)

        tb.Label(inner, text="Historico de Vendas", font=("Arial", 18, "bold")).pack(pady=5)

        botoes = tb.Frame(inner)
        botoes.pack(pady=10)
        tb.Button(botoes, text="Voltar", command=self.tela_vendas).pack(side=tk.LEFT, padx=5)

        tree_frame = tb.Frame(inner)
        tree_frame.pack(fill=tk.BOTH, expand=True)

        tree = tb.Treeview(tree_frame, columns=["ID", "Vendedor", "Cliente", "Data", "Status", "Total", "Pagamento"], height=15)
        tree.column("#0", width=0, stretch=tk.NO)
        for col in ["ID", "Vendedor", "Cliente", "Data", "Status", "Total", "Pagamento"]:
            tree.column(col, anchor=tk.W, width=100)
            tree.heading(col, text=col, anchor=tk.W)

        for venda in vendas:
            tree.insert("", "end", values=(venda[0], venda[1], venda[2], venda[3][:10], venda[4].upper(), f"R$ {venda[5]:.2f}", venda[6] or "N/A"))

        tree_scroll = tb.Scrollbar(tree_frame, orient=tk.VERTICAL, command=tree.yview)
        tree.configure(yscroll=tree_scroll.set)
        tree_scroll.pack(side=tk.RIGHT, fill=tk.Y)
        tree.pack(fill=tk.BOTH, expand=True)
    
    def janela_formulario(self, titulo, campos, callback, refresh_callback, parent=None):
        # Se um parent for passado, o Toplevel será filho dele (útil para manter o foco correto)
        topo_parent = parent if parent is not None else self.root
        janela = tk.Toplevel(topo_parent)
        if parent is not None:
            try:
                janela.transient(parent)
                janela.grab_set()
            except Exception:
                pass
        janela.title(titulo)
        janela.geometry("450x500")
        janela.resizable(True, True)

        canvas = tk.Canvas(janela)
        scrollbar = tb.Scrollbar(janela, orient=tk.VERTICAL, command=canvas.yview)
        frame_campos = tb.Frame(canvas)

        frame_campos.bind("<Configure>", lambda e: canvas.configure(scrollregion=canvas.bbox("all")))
        canvas.create_window((0, 0), window=frame_campos, anchor="nw")
        canvas.configure(yscrollcommand=scrollbar.set)

        canvas.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)

        entradas = {}
        for campo in campos:
            tb.Label(frame_campos, text=campo[0] + ":", font=("Arial", 10)).pack(anchor=tk.W, pady=(10, 2))
            entrada = tb.Entry(frame_campos, width=40)
            if len(campo) > 2:
                entrada.insert(0, str(campo[2]))
            entrada.pack(pady=(0, 10))
            entradas[campo[0]] = entrada
        
        def salvar():
            dados = [entradas[campo[0]].get() for campo in campos]
            sucesso, msg = callback(dados)
            messagebox.showinfo("Resultado", msg)
            if sucesso:
                janela.destroy()
                refresh_callback()
        
        frame_botoes = tb.Frame(frame_campos)
        frame_botoes.pack(pady=20)
        tb.Button(frame_botoes, text="Salvar", command=salvar).pack(side=tk.LEFT, padx=5)
        tb.Button(frame_botoes, text="Cancelar", command=janela.destroy).pack(side=tk.LEFT, padx=5)
    
    def limpar_janela(self):
        for widget in self.root.winfo_children():
            if not isinstance(widget, tk.Menu):
                widget.destroy()
    
    def sair_sistema(self):
        if messagebox.askyesno("Sair", "Deseja realmente fechar o sistema?"):
            self.root.destroy()
    
    def tela_devolucao(self):
        self.limpar_janela()
        frame = tb.Frame(self.root, padding=20)
        frame.pack(fill=BOTH, expand=YES)

        tb.Label(frame, text="🔄 Devolução de Livros", font=("Helvetica", 18, "bold")).pack(pady=10)

        # Área de Busca de Venda
        busca_frame = tb.LabelFrame(frame, text="Buscar Venda Original")
        busca_frame.pack(fill=X, padx=10, pady=10, ipady=15, ipadx=10)

        tb.Label(busca_frame, text="ID da Venda:").pack(side=LEFT, padx=5)
        ent_venda_id = tb.Entry(busca_frame, width=15)
        ent_venda_id.pack(side=LEFT, padx=5)

        # Tabela para mostrar os itens daquela venda
        tree_frame = tb.Frame(frame)
        tree_frame.pack(fill=BOTH, expand=YES, padx=10, pady=10)

        colunas = ("ID Item", "Livro", "Saldo", "Preço Unit.")
        self.tree_itens_dev = tb.Treeview(tree_frame, columns=colunas, show="headings", bootstyle="info")
        
        for col in colunas:
            self.tree_itens_dev.heading(col, text=col)
            self.tree_itens_dev.column(col, anchor=W, width=150)
            
        scrollbar = tb.Scrollbar(tree_frame, orient=VERTICAL, command=self.tree_itens_dev.yview)
        self.tree_itens_dev.configure(yscrollcommand=scrollbar.set)
        self.tree_itens_dev.pack(fill=BOTH, expand=YES, side=LEFT)
        scrollbar.pack(fill=Y, side=RIGHT)

        def buscar_itens_venda():
            # Limpa tabela
            for i in self.tree_itens_dev.get_children(): self.tree_itens_dev.delete(i)
            
            v_id = ent_venda_id.get().strip()
            # SQL Inteligente: Só traz itens onde ainda há saldo para devolver
            # Filtro: quantidade (original) > quantidade_devolvida
            query = """
                SELECT 
                    iv.id, 
                    iv.livro_id, 
                    l.titulo, 
                    iv.quantidade, 
                    iv.preco_unitario, 
                    iv.quantidade_devolvida 
                FROM itens_venda iv
                JOIN livros l ON iv.livro_id = l.id
                WHERE iv.venda_id = ? AND iv.quantidade > iv.quantidade_devolvida
            """
            itens = self.db.cursor.execute(query, (v_id,)).fetchall()
            
            if not itens:
                messagebox.showinfo("Aviso", "Nenhum item encontrado para esta venda.")
                return
            
            for item in itens:
                    id_item = item[0]
                    titulo = item[2]
                    saldo_real = item[3] - item[5]
                    preco = item[4]

                    self.tree_itens_dev.insert("", END, values=(
                    id_item, 
                    titulo, 
                    saldo_real, # Mostra na tela apenas o que ele PODE devolver
                    f"R$ {preco:.2f}"
                ))

        tb.Button(busca_frame, text="🔍 Buscar Itens", command=buscar_itens_venda, style='Normal.TButton').pack(side=LEFT, padx=10)

        # Botão de Ação
        def processar_devolucao():
            selecao = self.tree_itens_dev.selection()
            if not selecao:
                messagebox.showwarning("Aviso", "Selecione o livro que está sendo devolvido.")
                return

            valores = self.tree_itens_dev.item(selecao)['values']
            id_item_venda = valores[0]
            nome_livro = valores[1]
            qtd_vendida = valores[2]

            # Pergunta a quantidade a devolver
            qtd_devolver = simpledialog.askinteger("Devolução", f"Quantas unidades de '{nome_livro}' deseja devolver?", 
                                                minvalue=1, maxvalue=int(qtd_vendida))
            
            if qtd_devolver:
                try:
                    # 1. Recuperar o ID do Livro através do ID do Item da Venda
                    # (Você precisará de uma query no banco para isso)
                    res = self.db.cursor.execute("SELECT livro_id FROM itens_venda WHERE id=?", (id_item_venda,)).fetchone()
                    livro_id = res[0]

                    # 2. Atualizar Estoque
                    sucesso, msg = self.livro.adicionar_estoque_por_id(livro_id, qtd_devolver)
                    self.livro.adicionar_estoque_por_id(livro_id, qtd_devolver) # Use seu método de somar estoque
                    if  sucesso:
                        # 3. Registrar o controle de devolução no banco
                        self.db.cursor.execute("""
                            UPDATE itens_venda 
                            SET quantidade_devolvida = quantidade_devolvida + ? 
                            WHERE id = ?
                        """, (qtd_devolver, id_item_venda))
                        self.db.conexao.commit()

                        messagebox.showinfo("Sucesso", f"{qtd_devolver} unidade(s) de '{nome_livro}' retornaram ao estoque.")
                        buscar_itens_venda() # Atualiza a lista
                    else:
                        messagebox.showerror("Erro", msg)
                    
                except Exception as e:
                    messagebox.showerror("Erro", f"Falha na devolução: {e}")

        btn_frame = tb.Frame(frame)
        btn_frame.pack(fill=X, pady=10)

        tb.Button(btn_frame, text="✅ Confirmar Devolução", bootstyle=SUCCESS, command=processar_devolucao, style='Normal.TButton').pack(side=LEFT, padx=10)
        tb.Button(btn_frame, text="⬅ Voltar", command=self.criar_tela_inicial, style='Normal.TButton').pack(side=RIGHT)
    
    def tela_importar_xml(self):
        import xml.etree.ElementTree as ET
        from tkinter import filedialog

        self.limpar_janela()        
        frame = tb.Frame(self.root, padding=20)
        frame.pack(fill=BOTH, expand=YES)

        tb.Label(frame, text="📥 Importar Nota Fiscal XML", font=("Helvetica", 18, "bold")).pack(pady=10)

        # --- TABELA ---
        colunas = ("Livro", "ISBN", "Qtd", "V. Unit", "% Desc", "P. Compra", "P. Venda")
        self.tree_xml = tb.Treeview(frame, columns=colunas, show="headings", bootstyle="primary")
        
        for col in colunas:
            self.tree_xml.heading(col, text=col)
            self.tree_xml.column(col, width=120, anchor=CENTER)
        
        # Ajuste específico para o nome do livro ser maior
        self.tree_xml.column("Livro", width=250, anchor=W)
        self.tree_xml.pack(fill=BOTH, expand=YES, pady=20)

        # --- LÓGICA DE EDIÇÃO NO GRID ---
        def on_double_click(event):
            """ Abre um campo de edição na célula clicada """
            item = self.tree_xml.identify_row(event.y)
            column = self.tree_xml.identify_column(event.x)
            
            if not item: return
            
            # Descobrir o índice da coluna
            col_idx = int(column.replace('#', '')) - 1
            x, y, width, height = self.tree_xml.bbox(item, column)
            
            # Pegar o valor atual
            valores_atuais = self.tree_xml.item(item)['values']
            value_atual = valores_atuais[col_idx]
            
            # Criar o campo de entrada (Entry) usando o tk padrão para evitar conflitos de estilo
            # Forçamos fundo branco e texto preto para garantir visibilidade
            entry = tk.Entry(self.tree_xml, bg="white", fg="black", insertbackground="black")
            entry.insert(0, value_atual)
            entry.place(x=x, y=y, width=width, height=height)
            
            entry.focus_set()
            entry.select_range(0, tk.END) # Seleciona o texto para facilitar a troca

            def salvar_edicao(event=None):
                novo_valor = entry.get()
                novos_valores = list(self.tree_xml.item(item)['values'])
                novos_valores[col_idx] = novo_valor
                self.tree_xml.item(item, values=novos_valores)
                entry.destroy()
            
            # Atalhos de teclado
            entry.bind('<Return>', salvar_edicao)
            entry.bind('<Tab>', salvar_edicao)     # TAB também confirma e salva
            entry.bind('<Escape>', lambda e: entry.destroy())
            entry.bind('<FocusOut>', lambda e: entry.destroy())

        self.tree_xml.bind("<Double-1>", on_double_click)

        def selecionar_e_processar():
            caminho = filedialog.askopenfilename(filetypes=[("XML", "*.xml")])
            if not caminho: return

            try:
                tree = ET.parse(caminho)
                root = tree.getroot()
                ns = {'nfe': 'http://www.portalfiscal.inf.br/nfe'}
                
                for i in self.tree_xml.get_children(): self.tree_xml.delete(i)

                for det in root.findall('.//nfe:det', ns):
                    prod = det.find('nfe:prod', ns)
                    
                    xProd = prod.find('nfe:xProd', ns).text
                    nome_livro = xProd.split('-')[0].strip()
                    isbn = prod.find('nfe:cEAN', ns).text if prod.find('nfe:cEAN', ns) is not None else "N/A"

                    qtd = float(prod.find('nfe:qCom', ns).text)
                    v_unit_bruto = float(prod.find('nfe:vUnCom', ns).text)
                    v_prod_total = float(prod.find('nfe:vProd', ns).text)
                    v_desc_total = float(prod.find('nfe:vDesc', ns).text) if prod.find('nfe:vDesc', ns) is not None else 0
                    
                    percentual_desc = (v_desc_total / v_prod_total) * 100 if v_prod_total > 0 else 0
                    preco_compra = v_unit_bruto * (1 - (percentual_desc / 100))
                    
                    # --- REGRA DE PREÇO COM ARREDONDAMENTO ---
                    if preco_compra < 31:
                        preco_venda = preco_compra + 10
                    else:
                        preco_venda = preco_compra * 1.20
                    
                    # Arredondamento para 2 casas decimais
                    preco_venda = round(preco_venda, 2)
                    
                    self.tree_xml.insert("", END, values=(
                        nome_livro,
                        isbn,
                        int(qtd),
                        f"{v_unit_bruto:.2f}",
                        f"{percentual_desc:.1f}",
                        f"{preco_compra:.2f}",
                        f"{preco_venda:.2f}"
                    ))
                
                messagebox.showinfo("Sucesso", "Nota XML processada. Você pode editar os valores clicando duas vezes nas células.")
            except Exception as e:
                messagebox.showerror("Erro", f"Erro ao ler XML: {e}")

        # Botões de Ação
        btn_frame = tb.Frame(frame)
        btn_frame.pack(fill=X, pady=5)

        tb.Button(btn_frame, text="📂 Abrir Arquivo XML", bootstyle=INFO, command=selecionar_e_processar).pack(side=LEFT, padx=10)
        tb.Button(btn_frame, text="❌ Remover Item", bootstyle=DANGER, command=self.remover_item_xml).pack(side=LEFT, padx=5)
        tb.Button(btn_frame, text="⬅ Voltar", bootstyle=SECONDARY, command=self.criar_tela_inicial).pack(side=RIGHT, padx=5)
        tb.Button(btn_frame, text="💾 Gravar no Banco", bootstyle=SUCCESS, command=self.gravar_livros_xml).pack(side=RIGHT, padx=5)
    
    def gravar_livros_xml(self):
        """ Percorre a Grid do XML e salva os dados no Banco de Dados """
        itens = self.tree_xml.get_children()
        
        if not itens:
            messagebox.showwarning("Aviso", "Não há dados na tabela para gravar.")
            return

        if not messagebox.askyesno("Confirmar", f"Deseja importar {len(itens)} itens para o banco de dados?"):
            return

        sucessos = 0
        erros = 0

        for item_id in itens:
            # Pegar valores da linha (respeitando as edições que você fez)
            valores = self.tree_xml.item(item_id)['values']
            
            titulo = str(valores[0])
            isbn = str(valores[1])
            quantidade = int(valores[2])
            preco_compra = float(str(valores[5]).replace("R$", "").strip())
            preco_venda = float(str(valores[6]).replace("R$", "").strip())

            try:
                # 1. Verificar se o livro já existe pelo ISBN
                self.db.cursor.execute("SELECT id, quantidade FROM livros WHERE isbn = ?", (isbn,))
                resultado = self.db.cursor.fetchone()

                if resultado:
                    # Se existe, atualiza o estoque somando a nova quantidade
                    livro_id, qtd_atual = resultado
                    nova_qtd = qtd_atual + quantidade
                    self.db.cursor.execute("""
                        UPDATE livros 
                        SET quantidade = ?, preco_compra = ?, preco_venda = ? 
                        WHERE id = ?
                    """, (nova_qtd, preco_compra, preco_venda, livro_id))
                else:
                    # Se não existe, cadastra como novo livro
                    # Deixamos Autor e Espírito como "Importado XML" ou vazio
                    self.db.cursor.execute("""
                        INSERT INTO livros (titulo, autor, isbn, quantidade, preco_compra, preco_venda, espirito, data_cadastro)
                        VALUES (?, ?, ?, ?, ?, ?, ?, ?)
                    """, (titulo, "Importado XML", isbn, quantidade, preco_compra, preco_venda, "N/A", datetime.now().isoformat()))
                
                sucessos += 1
            except Exception as e:
                print(f"Erro ao gravar item {titulo}: {e}")
                erros += 1

        self.db.conexao.commit()
        
        if erros == 0:
            messagebox.showinfo("Sucesso", f"{sucessos} livros foram processados com sucesso!")
            self.tree_xml.delete(*self.tree_xml.get_children()) # Limpa a grid após salvar
        else:
            messagebox.showwarning("Concluído com Alertas", f"Sucesso: {sucessos}\nErros: {erros}\nVerifique o console para detalhes.")

    def remover_item_xml(self):
        """Remove a linha selecionada no grid de importação XML"""
        selecionado = self.tree_xml.selection()
        
        if not selecionado:
            messagebox.showwarning("Aviso", "Por favor, selecione um item na tabela para remover.")
            return
        
        # Pergunta para confirmar a remoção apenas do grid
        if messagebox.askyesno("Confirmar", "Deseja remover este item da lista de importação?"):
            for item in selecionado:
                self.tree_xml.delete(item)

if __name__ == "__main__":
    root = tk.Tk()
    app = BibliotecaApp(root)
    root.mainloop()