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


class BibliotecaApp:
    def __init__(self, root):
        self.root = root
        
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
    
    def criar_tela_inicial(self):
        self.limpar_janela()
        
        main_frame = tb.Frame(self.root, padding=30)
        main_frame.pack(fill=BOTH, expand=YES)

        # Título do Sistema
        tb.Label(main_frame, text="📚 SISTEMA LIVRARIA PRO", 
                font=("Helvetica", 28, "bold"), bootstyle="primary").pack(pady=(0, 40))

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
            ("Gerenciar Livros", self.tela_livros, "📖", PRIMARY),     # AZUL ESCURO
            ("Gerenciar Clientes", self.tela_clientes, "👥", SECONDARY), # CINZA
            ("Gerenciar Fornecedores", self.tela_fornecedores, "🚚", DARK), # Cinza Grafite / Preto
            ("Gerenciar Vendedores", self.tela_vendedores, "👔", INFO),   # AZUL
            ("Devolução", self.tela_devolucao, "🔄", WARNING), # Laranja
            ("Sair do Sistema", self.sair_sistema, "❌", DANGER), # <-- NOVO BOTÃO
        ]

        row, col = 0, 0
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

        # Faz com que as linhas também estiquem se a janela crescer
        for r in range(row + 1):
            menu_frame.rowconfigure(r, weight=1)
    
    def tela_clientes(self):
        dados = self.cliente.listar()
        colunas = ["ID", "Nome", "Email", "Telefone", "Endereco"]
        self.criar_tela_crud("Clientes", dados, colunas, 
                            self.adicionar_cliente, self.editar_cliente, 
                            self.deletar_cliente, self.atualizar_lista_clientes)
    
    def tela_livros(self):
        dados = self.livro.listar()
        colunas = ["ID", "Titulo", "Autor", "Espirito", "ISBN", "Qtd", "Preco Compra", "Preco Venda", "Fornecedor"]
        self.criar_tela_crud("Livros", dados, colunas,
                            self.adicionar_livro, self.editar_livro,
                            self.deletar_livro, self.atualizar_lista_livros)
    
    def tela_fornecedores(self):
        dados = self.fornecedor.listar()
        colunas = ["ID", "Nome", "CNPJ", "Email", "Telefone"]
        self.criar_tela_crud("Fornecedores", dados, colunas,
                            self.adicionar_fornecedor, self.editar_fornecedor,
                            self.deletar_fornecedor, self.atualizar_lista_fornecedores)
    
    def tela_vendedores(self):
        dados = self.vendedor.listar()
        colunas = ["ID", "Nome Vendedor", "Data Cadastro"]
        self.criar_tela_crud("Vendedores", dados, colunas,
                            self.adicionar_vendedor, self.editar_vendedor,
                            self.deletar_vendedor, self.atualizar_lista_vendedores)
    
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
        
        # Treeview
        self.tree = tb.Treeview(content_frame, columns=colunas, height=15)
        self.tree.column("#0", width=0, stretch=tk.NO)
        for col in colunas:
            self.tree.column(col, anchor=tk.W, width=120)
            self.tree.heading(col, text=col, anchor=tk.W)
        
        scrollbar_tree = tb.Scrollbar(content_frame, orient=tk.VERTICAL, command=self.tree.yview)
        self.tree.configure(yscroll=scrollbar_tree.set)
        scrollbar_tree.pack(side=tk.RIGHT, fill=tk.Y)
        
        for item in dados:
            self.tree.insert("", "end", values=item[:len(colunas)])
        
        self.tree.pack(fill=tk.BOTH, expand=True)
        
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
        
        # Espírito
        tb.Label(form_frame, text="Espírito:", font=("Arial", 10, "bold")).grid(row=3, column=0, sticky=tk.W, pady=(10, 2))
        entrada_espirito = tb.Entry(form_frame, width=40)
        entrada_espirito.grid(row=3, column=1, pady=(0, 10), sticky=tk.EW, padx=(10, 0))
        campos['espirito'] = entrada_espirito
        
        # Quantidade
        tb.Label(form_frame, text="Quantidade:", font=("Arial", 10, "bold")).grid(row=4, column=0, sticky=tk.W, pady=(10, 2))
        entrada_qtd = tb.Entry(form_frame, width=40)
        entrada_qtd.insert(0, "1")
        entrada_qtd.grid(row=4, column=1, pady=(0, 10), sticky=tk.EW, padx=(10, 0))
        campos['qtd'] = entrada_qtd
        
        # Preço de Compra
        tb.Label(form_frame, text="Preço de Compra:", font=("Arial", 10, "bold")).grid(row=5, column=0, sticky=tk.W, pady=(10, 2))
        entrada_preco_compra = tb.Entry(form_frame, width=40)
        entrada_preco_compra.insert(0, "0.00")
        entrada_preco_compra.grid(row=5, column=1, pady=(0, 10), sticky=tk.EW, padx=(10, 0))
        campos['preco_compra'] = entrada_preco_compra
        
        # Preço de Venda
        tb.Label(form_frame, text="Preço de Venda:", font=("Arial", 10, "bold")).grid(row=6, column=0, sticky=tk.W, pady=(10, 2))
        entrada_preco_venda = tb.Entry(form_frame, width=40)
        entrada_preco_venda.insert(0, "0.00")
        entrada_preco_venda.grid(row=6, column=1, pady=(0, 10), sticky=tk.EW, padx=(10, 0))
        campos['preco_venda'] = entrada_preco_venda
        
        # Fornecedor
        tb.Label(form_frame, text="Fornecedor:", font=("Arial", 10, "bold")).grid(row=7, column=0, sticky=tk.W, pady=(10, 2))
        fornecedores = self.fornecedor.listar()
        fornecedor_combo = tb.Combobox(form_frame, 
                                       values=[f"{f[0]} - {f[1]}" for f in fornecedores], 
                                       state="readonly", width=38)
        # Definir fornecedor 1 como padrão se existir
        if fornecedores:
            fornecedor_combo.set(f"{fornecedores[0][0]} - {fornecedores[0][1]}")
        fornecedor_combo.grid(row=7, column=1, pady=(0, 20), sticky=tk.EW, padx=(10, 0))
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
                
                sucesso, msg = self.livro.adicionar(titulo, autor, isbn, qtd, preco_compra, preco_venda, espirito, fornecedor_id)
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
                    
                    sucesso, msg = self.livro.atualizar(id_item, titulo, autor, isbn, qtd, preco_compra, preco_venda, espirito, fornecedor_id)
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

        titulo_label = tb.Label(content_frame, text="Entrada de Livros", font=("Arial", 18, "bold"))
        titulo_label.pack(pady=10)

        # Frame de entrada
        entrada_frame = tb.LabelFrame(content_frame, text="Dados do Livro")
        entrada_frame.pack(fill=X, padx=10, pady=10, ipady=10, ipadx=10)
        
        # Dicionário para armazenar livros e seus dados - mapeia por TÍTULO
        livros_dict = {}
        livros_dict_isbn = {}  # mapeia por ISBN
        todos_livros = self.livro.listar()
        for livro in todos_livros:
            # livro[0]=id, livro[1]=titulo, livro[4]=isbn
            titulo = livro[1] if livro[1] else f"ID-{livro[0]}"
            isbn = livro[4] if livro[4] else f"ID-{livro[0]}"
            
            livros_dict[titulo] = {
                'id': livro[0],
                'titulo': livro[1],
                'isbn': isbn,
                'preco_compra': livro[6],
                'preco_venda': livro[7],
                'fornecedor_id': livro[9] if len(livro) > 9 else None
            }
            
            livros_dict_isbn[isbn] = {
                'id': livro[0],
                'titulo': livro[1],
                'isbn': isbn,
                'preco_compra': livro[6],
                'preco_venda': livro[7],
                'fornecedor_id': livro[9] if len(livro) > 9 else None
            }
        
        # Nome do Livro - Com Autocompletar
        tb.Label(entrada_frame, text="Nome do Livro:", font=("Arial", 10)).grid(row=0, column=0, sticky=tk.W, pady=5)
        
        entrada_nome = tb.Combobox(entrada_frame, width=48, state="normal")
        entrada_nome.grid(row=0, column=1, padx=10, pady=5)
        
        def atualizar_sugestoes_nome(*args):
            """Atualiza sugestões de nomes conforme o usuário digita"""
            texto_digitado = entrada_nome.get().strip().lower()
            
            if not texto_digitado:
                entrada_nome['values'] = list(livros_dict.keys())
            else:
                # Filtra livros que começam com o texto digitado
                sugestoes = [liv for liv in livros_dict.keys()
                            if liv.lower().startswith(texto_digitado)]
                entrada_nome['values'] = sugestoes
        
        def ao_selecionar_livro_por_nome(*args):
            """Carrega dados do livro selecionado pelo nome"""
            livro_selecionado = entrada_nome.get().strip()

            if livro_selecionado in livros_dict:
                dados_livro = livros_dict[livro_selecionado]
                # Preenche apenas ISBN, sem alterar valor unitário
                entrada_isbn.delete(0, tk.END)
                entrada_isbn.insert(0, dados_livro['isbn'])
                # Seta campo de preco de compra/venda com calculo atual do input
                atualizar_calculos()
            else:
                if livro_selecionado:
                    if not messagebox.askyesno("Livro não cadastrado", f"Livro '{livro_selecionado}' não cadastrado. Deseja continuar cadastrando?"):
                        entrada_nome.delete(0, tk.END)
                        entrada_isbn.delete(0, tk.END)
        
        entrada_nome.bind('<KeyRelease>', atualizar_sugestoes_nome)
        entrada_nome.bind('<<ComboboxSelected>>', ao_selecionar_livro_por_nome)
        
        # Inicializa com lista de todos os livros
        entrada_nome['values'] = list(livros_dict.keys())
        
        # ISBN - Campo editável
        tb.Label(entrada_frame, text="ISBN:", font=("Arial", 10)).grid(row=1, column=0, sticky=tk.W, pady=5)
        entrada_isbn = tb.Entry(entrada_frame, width=50)
        entrada_isbn.grid(row=1, column=1, padx=10, pady=5)
        
        def ao_preencher_isbn(*args):
            """Busca o livro pelo ISBN quando preenchido"""
            isbn_digitado = entrada_isbn.get().strip()

            if isbn_digitado and isbn_digitado in livros_dict_isbn:
                dados_livro = livros_dict_isbn[isbn_digitado]
                # Se o nome não foi preenchido, preenche
                if not entrada_nome.get():
                    entrada_nome.delete(0, tk.END)
                    entrada_nome.insert(0, dados_livro['titulo'])
                # Mantém valor unitário do usuário e recalcula preços
                atualizar_calculos()
        
        entrada_isbn.bind('<FocusOut>', ao_preencher_isbn)
        
        # Quantidade
        tb.Label(entrada_frame, text="Quantidade:", font=("Arial", 10)).grid(row=2, column=0, sticky=tk.W, pady=5)
        entrada_qtd = tb.Entry(entrada_frame, width=50)
        entrada_qtd.insert(0, "1")
        entrada_qtd.grid(row=2, column=1, padx=10, pady=5)
        
        # Valor Unitário
        tb.Label(entrada_frame, text="Valor Unitario (R$):", font=("Arial", 10)).grid(row=3, column=0, sticky=tk.W, pady=5)
        entrada_valor = tb.Entry(entrada_frame, width=50)
        entrada_valor.insert(0, "0.00")
        entrada_valor.grid(row=3, column=1, padx=10, pady=5)
        
        # Percentual de Desconto
        tb.Label(entrada_frame, text="Percentual de Desconto (%):", font=("Arial", 10)).grid(row=4, column=0, sticky=tk.W, pady=5)
        entrada_percentual = tb.Entry(entrada_frame, width=50)
        entrada_percentual.insert(0, "0")
        entrada_percentual.grid(row=4, column=1, padx=10, pady=5)
        
        # Frame de cálculos
        calculo_frame = tb.LabelFrame(content_frame, text="Calculo Automatico")
        calculo_frame.pack(fill=X, padx=10, pady=10, ipady=10, ipadx=10)
        
        tb.Label(calculo_frame, text="Preco Compra (R$):", font=("Arial", 10, "bold")).grid(row=0, column=0, sticky=tk.W, pady=5)
        label_preco_compra = tb.Label(calculo_frame, text="0.00", font=("Arial", 12, "bold"), foreground="green")
        label_preco_compra.grid(row=0, column=1, padx=10, pady=5, sticky=tk.W)
        
        tb.Label(calculo_frame, text="Preco Venda (R$):", font=("Arial", 10, "bold")).grid(row=1, column=0, sticky=tk.W, pady=5)
        entrada_preco_venda = tb.Entry(calculo_frame, width=30, font=("Arial", 12, "bold"))
        entrada_preco_venda.insert(0, "0.00")
        entrada_preco_venda.grid(row=1, column=1, padx=10, pady=5, sticky=tk.W)
        
        tb.Label(calculo_frame, text="(editável - sugestão automática)", font=("Arial", 8, "italic")).grid(row=1, column=2, padx=10, pady=5)
        
        def atualizar_calculos(*args):
            try:
                valor_unit = float(entrada_valor.get())
                percentual = float(entrada_percentual.get())
                
                # Calcula preco_compra
                preco_compra = valor_unit - (valor_unit * percentual / 100)
                
                # Calcula preco_venda com lucro de 10 reais (sugestão)
                preco_venda_sugerido = preco_compra + 10
                
                label_preco_compra.config(text=f"{preco_compra:.2f}")
                entrada_preco_venda.delete(0, tk.END)
                entrada_preco_venda.insert(0, f"{preco_venda_sugerido:.2f}")
                
            except ValueError:
                label_preco_compra.config(text="Erro")
                entrada_preco_venda.delete(0, tk.END)
                entrada_preco_venda.insert(0, "Erro")
        
        entrada_valor.bind('<KeyRelease>', atualizar_calculos)
        entrada_percentual.bind('<KeyRelease>', atualizar_calculos)
        
        # Frame de fornecedor
        fornecedor_frame = tb.LabelFrame(content_frame, text="Fornecedor")
        fornecedor_frame.pack(fill=X, padx=10, pady=10, ipady=10, ipadx=10)
        
        tb.Label(fornecedor_frame, text="Fornecedor:", font=("Arial", 10)).pack(anchor=tk.W, pady=5)
        fornecedores = self.fornecedor.listar()
        fornecedor_combo = tb.Combobox(fornecedor_frame, 
                                       values=[f"{f[0]} - {f[1]}" for f in fornecedores], 
                                       state="readonly", width=50)
        fornecedor_combo.pack(fill=tk.X, pady=5)
        
        # Botões de ação
        botoes_frame = tb.Frame(content_frame)
        botoes_frame.pack(pady=20)
        
        def salvar_entrada():
            try:
                nome_livro = entrada_nome.get().strip()
                isbn_livro = entrada_isbn.get().strip()
                quantidade = int(entrada_qtd.get())
                valor_unit = float(entrada_valor.get())
                percentual = float(entrada_percentual.get())
                preco_venda = float(entrada_preco_venda.get())
                fornecedor_sel = fornecedor_combo.get()

                if not nome_livro:
                    messagebox.showwarning("Aviso", "Digite o nome do livro!")
                    return

                # Se encontrou pelo nome, preenche ISBN automaticamente
                if nome_livro in livros_dict and not isbn_livro:
                    isbn_livro = livros_dict[nome_livro].get('isbn', '')

                # Se encontrou pelo ISBN, preenche nome automaticamente
                if isbn_livro in livros_dict_isbn and not nome_livro:
                    nome_livro = livros_dict_isbn[isbn_livro].get('titulo', nome_livro)

                if not fornecedor_sel:
                    messagebox.showwarning("Aviso", "Selecione um fornecedor!")
                    return

                # Calcula valores
                preco_compra = valor_unit - (valor_unit * percentual / 100)
                fornecedor_id = int(fornecedor_sel.split(" - ")[0])

                # Tenta buscar por ISBN, depois por título
                if isbn_livro:
                    livro_existente = self.db.cursor.execute(
                        'SELECT id FROM livros WHERE isbn=?', (isbn_livro,)
                    ).fetchone()
                else:
                    livro_existente = self.db.cursor.execute(
                        'SELECT id FROM livros WHERE titulo=?', (nome_livro,)
                    ).fetchone()
                
                if livro_existente:
                    # Atualiza livro existente
                    livro_id = livro_existente[0]
                    self.db.cursor.execute('''
                        UPDATE livros SET quantidade=quantidade+?, preco_compra=?, preco_venda=?, fornecedor_id=?
                        WHERE id=?
                    ''', (quantidade, preco_compra, preco_venda, fornecedor_id, livro_id))
                    msg = f"Livro atualizado! +{quantidade} unidades"
                else:
                    # Cria novo livro
                    self.db.cursor.execute('''
                        INSERT INTO livros (titulo, isbn, quantidade, preco_compra, preco_venda, fornecedor_id, data_cadastro)
                        VALUES (?, ?, ?, ?, ?, ?, ?)
                    ''', (nome_livro, isbn_livro, quantidade, preco_compra, preco_venda, fornecedor_id, datetime.now().isoformat()))
                    msg = "Livro adicionado com sucesso!"
                
                self.db.conexao.commit()
                messagebox.showinfo("Sucesso", msg)
                
                # Limpa campos
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
                
            except ValueError:
                messagebox.showerror("Erro", "Verifique os valores digitados!")
            except Exception as e:
                messagebox.showerror("Erro", str(e))
        
        tb.Button(botoes_frame, text="Salvar Entrada", command=salvar_entrada).pack(side=tk.LEFT, padx=5)
        tb.Button(botoes_frame, text="Voltar", command=self.criar_tela_inicial).pack(side=tk.LEFT, padx=5)

    
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
        
        # Canvas + Scrollbar para garantir visibilidade em telas menores
        canvas = tk.Canvas(frame)
        scrollbar = tb.Scrollbar(frame, orient=tk.VERTICAL, command=canvas.yview)
        content_frame = tb.Frame(canvas)

        content_frame.bind("<Configure>", lambda e: canvas.configure(scrollregion=canvas.bbox("all")))
        canvas.create_window((0, 0), window=content_frame, anchor="nw")
        canvas.configure(yscrollcommand=scrollbar.set)

        canvas.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        
        titulo_label = tb.Label(content_frame, text="Vendas", font=("Arial", 18, "bold"))
        titulo_label.pack()
        
        botoes = tb.Frame(content_frame)
        botoes.pack(pady=10)
        tb.Button(botoes, text="Nova Venda", command=self.nova_venda).pack(side=tk.LEFT, padx=5)
        tb.Button(botoes, text="Continuar Venda", command=self.continuar_venda).pack(side=tk.LEFT, padx=5)
        tb.Button(botoes, text="Relatorio de Vendas", command=self.relatorio_vendas).pack(side=tk.LEFT, padx=5)
        tb.Button(botoes, text="Ver Historico", command=self.historico_vendas).pack(side=tk.LEFT, padx=5)
        tb.Button(botoes, text="Voltar", command=self.criar_tela_inicial).pack(side=tk.LEFT, padx=5)

    def relatorio_vendas(self):
        self.limpar_janela()
        frame = tb.Frame(self.root)
        frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10, ipady=10, ipadx=10)

        # Canvas + Scrollbar para garantir visibilidade em telas menores
        canvas = tk.Canvas(frame)
        scrollbar = tb.Scrollbar(frame, orient=tk.VERTICAL, command=canvas.yview)
        content_frame = tb.Frame(canvas)

        content_frame.bind("<Configure>", lambda e: canvas.configure(scrollregion=canvas.bbox("all")))
        canvas.create_window((0, 0), window=content_frame, anchor="nw")
        canvas.configure(yscrollcommand=scrollbar.set)

        canvas.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)

        tb.Label(content_frame, text="Relatório de Vendas", font=("Arial", 18, "bold")).pack(pady=5)

        filtro_frame = tb.LabelFrame(content_frame, text="Filtros")
        filtro_frame.pack(fill=tk.X, padx=5, pady=5, ipady=5, ipadx=5)

        # Data inicial (Usando Entry comum para evitar o bug do DateEntry)
        tb.Label(filtro_frame, text="Data Início (DD/MM/YYYY):", font=("Arial", 9)).grid(row=0, column=0, sticky=tk.W, padx=5, pady=3)
        entrada_data_ini = tb.Entry(filtro_frame, width=15)
        entrada_data_ini.insert(0, datetime.now().strftime('%d/%m/%Y')) # Sugere data de hoje
        entrada_data_ini.grid(row=0, column=1, padx=5, pady=3)
        
        # Data final
        tb.Label(filtro_frame, text="Data Fim (DD/MM/YYYY):", font=("Arial", 9)).grid(row=0, column=2, sticky=tk.W, padx=5, pady=3)
        entrada_data_fim = tb.Entry(filtro_frame, width=15)
        entrada_data_fim.insert(0, datetime.now().strftime('%d/%m/%Y'))
        entrada_data_fim.grid(row=0, column=3, padx=5, pady=3)

        # Forma de pagamento
        tb.Label(filtro_frame, text="Forma de Pagamento:", font=("Arial", 9)).grid(row=1, column=0, sticky=tk.W, padx=5, pady=3)
        entrada_pagamento = tb.Combobox(filtro_frame, values=["Dinheiro", "Cartão", "PIX", "Nenhum"], width=13)
        entrada_pagamento.grid(row=1, column=1, padx=5, pady=3)

        # Status
        tb.Label(filtro_frame, text="Status:", font=("Arial", 9)).grid(row=1, column=2, sticky=tk.W, padx=5, pady=3)
        entrada_status = tb.Combobox(filtro_frame, values=["aberto", "finalizado", "cancelado"], width=13)
        entrada_status.grid(row=1, column=3, padx=5, pady=3)

        # Cliente
        tb.Label(filtro_frame, text="Cliente:", font=("Arial", 9)).grid(row=2, column=0, sticky=tk.W, padx=5, pady=3)
        clientes = self.cliente.listar()
        cliente_combo = tb.Combobox(filtro_frame, values=[f"{c[0]} - {c[1]}" for c in clientes], width=30)
        cliente_combo.grid(row=2, column=1, columnspan=3, padx=5, pady=3, sticky=tk.W)

        # Vendedor
        tb.Label(filtro_frame, text="Vendedor:", font=("Arial", 9)).grid(row=3, column=0, sticky=tk.W, padx=5, pady=3)
        vendedores = self.vendedor.listar()
        vendedor_combo = tb.Combobox(filtro_frame, values=[f"{v[0]} - {v[1]}" for v in vendedores], width=30)
        vendedor_combo.grid(row=3, column=1, columnspan=3, padx=5, pady=3, sticky=tk.W)

        # Livro
        tb.Label(filtro_frame, text="Livro:", font=("Arial", 9)).grid(row=4, column=0, sticky=tk.W, padx=5, pady=3)
        livros = self.livro.listar()
        livro_combo = tb.Combobox(filtro_frame, values=[f"{l[0]} - {l[1]}" for l in livros], width=30)
        livro_combo.grid(row=4, column=1, columnspan=3, padx=5, pady=3, sticky=tk.W)

        # Botões de pesquisa
        botoes_filtro = tb.Frame(content_frame)
        botoes_filtro.pack(pady=5)

        def gerar_relatorio():
            # Leia diretamente do widget usando .get()
            data_ini_str = entrada_data_ini.get() 
            data_fim_str = entrada_data_fim.get()
            
            # Converte para o formato do banco (YYYY-MM-DD)
            try:
                data_ini = datetime.strptime(data_ini_str, '%d/%m/%Y').strftime('%Y-%m-%d')
                data_fim = datetime.strptime(data_fim_str, '%d/%m/%Y').strftime('%Y-%m-%d')
            except:
                data_ini = None
                data_fim = None
            
            status = entrada_status.get().strip() or None
            pagamento = entrada_pagamento.get().strip() or None
            cliente_id = int(cliente_combo.get().split(' - ')[0]) if cliente_combo.get() else None
            vendedor_id = int(vendedor_combo.get().split(' - ')[0]) if vendedor_combo.get() else None
            livro_id = int(livro_combo.get().split(' - ')[0]) if livro_combo.get() else None

            resultado = self.venda.buscar_vendas_relatorio(
                data_ini=data_ini,
                data_fim=data_fim,
                status=status,
                metodo_pagamento=pagamento if pagamento != 'Nenhum' else None,
                cliente_id=cliente_id,
                vendedor_id=vendedor_id,
                livro_id=livro_id
            )

            for i in tree_relatorio.get_children():
                tree_relatorio.delete(i)

            for row in resultado:
                tree_relatorio.insert('', 'end', values=row)

        tb.Button(botoes_filtro, text="Buscar Relatório", command=gerar_relatorio).pack(side=tk.LEFT, padx=5)
        tb.Button(botoes_filtro, text="Voltar", command=self.tela_vendas).pack(side=tk.LEFT, padx=5)

        # Tabela de resultado
        resultado_frame = tb.Frame(content_frame)
        resultado_frame.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)

        tree_relatorio = tb.Treeview(resultado_frame, columns=["ID", "Data", "Status", "Pagamento", "Cliente", "Vendedor", "Total"], height=15)
        tree_relatorio.column("#0", width=0, stretch=tk.NO)
        for col in ["ID", "Data", "Status", "Pagamento", "Cliente", "Vendedor", "Total"]:
            tree_relatorio.column(col, anchor=tk.W, width=120)
            tree_relatorio.heading(col, text=col, anchor=tk.W)

        scrollbar_rel = tb.Scrollbar(resultado_frame, orient=tk.VERTICAL, command=tree_relatorio.yview)
        tree_relatorio.configure(yscroll=scrollbar_rel.set)
        scrollbar_rel.pack(side=tk.RIGHT, fill=tk.Y)
        tree_relatorio.pack(fill=tk.BOTH, expand=True)

    def tela_inventario(self):
        self.limpar_janela()
        frame = tb.Frame(self.root)
        frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)

        # Container rolável
        canvas = tk.Canvas(frame)
        scroll_y = tb.Scrollbar(frame, orient=tk.VERTICAL, command=canvas.yview)
        content_frame = tb.Frame(canvas)

        content_frame.bind("<Configure>", lambda e: canvas.configure(scrollregion=canvas.bbox("all")))
        canvas.create_window((0, 0), window=content_frame, anchor="nw")
        canvas.configure(yscrollcommand=scroll_y.set)

        canvas.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scroll_y.pack(side=tk.RIGHT, fill=tk.Y)

        tb.Label(content_frame, text="Inventário de Livros", font=("Arial", 18, "bold")).pack(pady=10)

        form = tb.Frame(content_frame)
        form.pack(fill=tk.X, pady=10)

        tb.Label(form, text="ISBN:", font=("Arial", 10)).grid(row=0, column=0, sticky=tk.W, padx=5, pady=5)
        isbn_entry = tb.Entry(form, width=30)
        isbn_entry.grid(row=0, column=1, padx=5, pady=5)

        tb.Label(form, text="Quantidade:", font=("Arial", 10)).grid(row=0, column=2, sticky=tk.W, padx=5, pady=5)
        quantidade_entry = tb.Entry(form, width=10)
        quantidade_entry.grid(row=0, column=3, padx=5, pady=5)
        quantidade_entry.insert(0, "1")

        tb.Button(form, text="Bipar/Adicionar", command=lambda: adicionar_item()).grid(row=0, column=4, padx=5, pady=5)

        # Dicionário de inventário temporário carregado do banco
        inventario = {}

        tree_frame = tb.Frame(content_frame)
        tree_frame.pack(fill=tk.BOTH, expand=True, pady=10)

        tree = tb.Treeview(tree_frame, columns=["ISBN", "Título", "Quantidade", "Estoque Atual"], height=12)
        tree.column("#0", width=0, stretch=tk.NO)
        for col in ["ISBN", "Título", "Quantidade", "Estoque Atual"]:
            tree.column(col, anchor=tk.W, width=140)
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
            for isbn, data in inventario.items():
                tree.insert("", "end", values=(isbn, data['titulo'], data['quantidade'], data['atual']))

        carregar_inventario()
        tree_scroll = tb.Scrollbar(tree_frame, orient=tk.VERTICAL, command=tree.yview)
        tree.configure(yscroll=tree_scroll.set)
        tree_scroll.pack(side=tk.RIGHT, fill=tk.Y)
        tree.pack(fill=tk.BOTH, expand=True)

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

        tipo_frame = tb.Frame(form)
        tipo_frame.grid(row=1, column=0, columnspan=5, pady=(5, 10), sticky=tk.W)
        tb.Label(tipo_frame, text="Operação:", font=("Arial", 10)).pack(side=tk.LEFT)
        operacao_var = tk.StringVar(value="Entrada")
        operacao_combo = tb.Combobox(tipo_frame, values=["Entrada", "Saída"], textvariable=operacao_var, width=10, state="readonly")
        operacao_combo.pack(side=tk.LEFT, padx=5)

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

        botoes = tb.Frame(content_frame)
        botoes.pack(fill=tk.X, pady=10)

        tb.Button(botoes, text="Aplicar Inventário", command=aplicar_inventario).pack(side=tk.RIGHT, padx=5)
        tb.Button(botoes, text="Limpar Inventário", command=limpar_inventario).pack(side=tk.RIGHT, padx=5)
        tb.Button(botoes, text="Voltar", command=self.tela_livros).pack(side=tk.RIGHT, padx=5)

    def nova_venda(self):
        # Janela para selecionar vendedor e cliente
        janela = tk.Toplevel(self.root)
        janela.title("Nova Venda")
        janela.geometry("400x300")
        
        frame = tb.Frame(janela)
        frame.pack(fill=tk.BOTH, expand=True, padx=15, pady=15)
        
        tb.Label(frame, text="Vendedor:", font=("Arial", 10)).pack(anchor=tk.W, pady=(10, 2))
        vendedores = self.vendedor.listar()
        vendedor_combo = tb.Combobox(frame, values=[f"{v[0]} - {v[1]}" for v in vendedores], state="readonly")
        vendedor_combo.pack(pady=(0, 15), fill=tk.X)
        
        tb.Label(frame, text="Cliente:", font=("Arial", 10)).pack(anchor=tk.W, pady=(10, 2))
        clientes = self.cliente.listar()
        cliente_combo = tb.Combobox(frame, values=[f"{c[0]} - {c[1]}" for c in clientes], state="readonly")
        cliente_combo.pack(pady=(0, 20), fill=tk.X)
        
        def iniciar():
            if not vendedor_combo.get() or not cliente_combo.get():
                messagebox.showwarning("Aviso", "Selecione vendedor e cliente!")
                return
            
            vendedor_id = int(vendedor_combo.get().split(" - ")[0])
            cliente_id = int(cliente_combo.get().split(" - ")[0])
            
            sucesso, venda_id, msg = self.venda.criar_venda(vendedor_id, cliente_id)
            if sucesso:
                janela.destroy()
                self.editar_venda(venda_id)
            else:
                messagebox.showerror("Erro", msg)
        
        tb.Button(frame, text="Iniciar Venda", command=iniciar).pack(pady=20)
    
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
        
        self.tree_itens = tb.Treeview(items_frame, columns=["ID", "Livro", "Qtd", "Preco", "Subtotal"], height=10)
        self.tree_itens.column("#0", width=0, stretch=tk.NO)
        for col in ["ID", "Livro", "Qtd", "Preco", "Subtotal"]:
            self.tree_itens.column(col, anchor=tk.W, width=100)
            self.tree_itens.heading(col, text=col, anchor=tk.W)
        
        itens = self.venda.listar_itens_venda(venda_id)
        for item in itens:
            self.tree_itens.insert("", "end", values=(item[0], item[2], item[3], f"{item[4]:.2f}", f"{item[5]:.2f}"))
        
        scrollbar = tb.Scrollbar(items_frame, orient=tk.VERTICAL, command=self.tree_itens.yview)
        self.tree_itens.configure(yscroll=scrollbar.set)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        self.tree_itens.pack(fill=tk.BOTH, expand=True)
        
        # Botões de ação
        botoes_itens = tb.Frame(frame)
        botoes_itens.pack(pady=10)
        tb.Button(botoes_itens, text="Adicionar Livro", command=self.adicionar_livro_venda).pack(side=tk.LEFT, padx=5)
        tb.Button(botoes_itens, text="Editar Item", command=self.editar_item_venda).pack(side=tk.LEFT, padx=5)
        tb.Button(botoes_itens, text="Remover Item", command=self.remover_item_venda).pack(side=tk.LEFT, padx=5)
        
        # Total e pagamento
        total_frame = tb.Frame(frame)
        total_frame.pack(fill=tk.X, pady=10)
        
        venda_atualizada = self.venda.obter_venda(venda_id)
        tb.Label(total_frame, text=f"Total: R$ {venda_atualizada[5]:.2f}", font=("Arial", 14, "bold")).pack(side=tk.LEFT, padx=20)
        
        botoes_finais = tb.Frame(frame)
        botoes_finais.pack(pady=10)
        
        if venda[4] == 'aberto':
            tb.Button(botoes_finais, text="Finalizar e Pagar", command=self.finalizar_venda).pack(side=tk.LEFT, padx=5)
            tb.Button(botoes_finais, text="Deixar em Aberto", command=self.tela_vendas).pack(side=tk.LEFT, padx=5)
        else:
            tb.Label(botoes_finais, text=f"Pagamento: {venda[6]} em {venda[7]}", font=("Arial", 10)).pack(side=tk.LEFT, padx=20)
        
        tb.Button(botoes_finais, text="Voltar", command=self.tela_vendas).pack(side=tk.LEFT, padx=5)
        
        self.atualizar_venda_display = lambda: self.editar_venda(venda_id)
    
    def adicionar_livro_venda(self):
        janela = tk.Toplevel(self.root)
        janela.title("Adicionar Livro")
        janela.geometry("520x460")
        
        frame = tb.Frame(janela)
        frame.pack(fill=tk.BOTH, expand=True, padx=15, pady=15)
        
        # Campos de pesquisa
        procura_frame = tb.Frame(frame)
        procura_frame.pack(fill=tk.X, pady=(0, 10))
        
        tb.Label(procura_frame, text="Nome do Livro:", font=("Arial", 10)).grid(row=0, column=0, sticky=tk.W, pady=2)
        entrada_nome_livro = tb.Entry(procura_frame, width=30)
        entrada_nome_livro.grid(row=0, column=1, padx=5, pady=2)
        
        tb.Label(procura_frame, text="ISBN:", font=("Arial", 10)).grid(row=1, column=0, sticky=tk.W, pady=2)
        entrada_isbn_livro = tb.Entry(procura_frame, width=30)
        entrada_isbn_livro.grid(row=1, column=1, padx=5, pady=2)
        
        def buscar():
            tree_livros.delete(*tree_livros.get_children())
            termo_nome = entrada_nome_livro.get().strip()
            termo_isbn = entrada_isbn_livro.get().strip()

            termo = None
            if termo_isbn:
                termo = termo_isbn
            elif termo_nome:
                termo = termo_nome

            if termo:
                livros = self.venda.buscar_livro(termo)
                for livro in livros:
                    # livro: (id, titulo, isbn, preco_venda)
                    tree_livros.insert("", "end", values=(livro[0], livro[1], livro[2], f"R$ {livro[3]:.2f}"))
        
        def buscar_auto(event=None):
            buscar()
        
        # Bind events for auto-search
        entrada_nome_livro.bind('<KeyRelease>', buscar_auto)
        entrada_isbn_livro.bind('<KeyRelease>', buscar_auto)
        
        tb.Button(frame, text="Buscar", command=buscar).pack(pady=5)

        # Lista de livros encontrados
        tree_livros = tb.Treeview(frame, columns=["ID", "Titulo", "ISBN", "Preco"], height=8)
        tree_livros.column("#0", width=0, stretch=tk.NO)
        for col in ["ID", "Titulo", "ISBN", "Preco"]:
            tree_livros.column(col, anchor=tk.W, width=130)
            tree_livros.heading(col, text=col, anchor=tk.W)
        tree_livros.pack(fill=tk.BOTH, expand=True, pady=10)
        
        # Quantidade e preço
        # --- CAMPOS DE ENTRADA (Qtd e Preço) ---
        form_frame = tb.Frame(frame)
        form_frame.pack(fill=tk.X, pady=10)
        
        tb.Label(form_frame, text="Quantidade:").pack(side=tk.LEFT, padx=5)
        entrada_qtd = tb.Entry(form_frame, width=10)
        entrada_qtd.pack(side=tk.LEFT, padx=5)
        entrada_qtd.insert(0, "1")
        
        tb.Label(form_frame, text="Preço Unitário:").pack(side=tk.LEFT, padx=5)
        entrada_preco = tb.Entry(form_frame, width=10)
        entrada_preco.pack(side=tk.LEFT, padx=5)

        # Preenche o preço automaticamente ao selecionar o livro na lista
        def preencher_preco(event=None):
            selecao = tree_livros.selection()
            if selecao:
                item = tree_livros.item(selecao)['values']
                # Remove "R$ " e troca vírgula por ponto para o Entry aceitar
                preco_limpo = str(item[3]).replace("R$ ", "").replace(",", ".")
                entrada_preco.delete(0, tk.END)
                entrada_preco.insert(0, preco_limpo)

        tree_livros.bind('<<TreeviewSelect>>', preencher_preco)

        # --- FUNÇÃO DO BOTÃO INCLUIR ---
        def confirmar_inclusao():
            selecao = tree_livros.selection()
            if not selecao:
                messagebox.showwarning("Aviso", "Selecione um livro na lista!")
                return
            
            try:
                # Captura os dados
                livro_id = int(tree_livros.item(selecao)['values'][0])
                quantidade = int(entrada_qtd.get())
                preco = float(entrada_preco.get().replace(',', '.'))

                # Grava no banco através da sua classe Venda
                sucesso, msg = self.venda.adicionar_item(self.venda_id_atual, livro_id, quantidade, preco)
                
                if sucesso:
                    messagebox.showinfo("Sucesso", "Item adicionado!")
                    janela.destroy()  # Fecha a janela de busca
                    self.atualizar_venda_display()  # Atualiza a lista de itens da venda principal
                else:
                    messagebox.showerror("Erro", msg)

            except ValueError:
                messagebox.showerror("Erro", "Quantidade ou Preço inválidos!")

        # --- BOTÕES FINAIS DA JANELA ---
        button_frame = tb.Frame(frame)
        button_frame.pack(fill=tk.X, pady=10)
        
        tb.Button(button_frame, text="✅ Incluir na Venda", 
                   command=confirmar_inclusao).pack(side=tk.LEFT, padx=5, expand=True, fill=tk.X)
        
        tb.Button(button_frame, text="❌ Cancelar", 
                   command=janela.destroy).pack(side=tk.LEFT, padx=5, expand=True, fill=tk.X)
    
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
        janela.geometry("600x400")
        janela.minsize(500, 320)

        container = tb.Frame(janela)
        container.pack(fill=tk.BOTH, expand=True)

        canvas = tk.Canvas(container)
        scroll_y = tb.Scrollbar(container, orient=tk.VERTICAL, command=canvas.yview)
        inner = tb.Frame(canvas)

        inner.bind("<Configure>", lambda e: canvas.configure(scrollregion=canvas.bbox("all")))
        canvas.create_window((0, 0), window=inner, anchor="nw")
        canvas.configure(yscrollcommand=scroll_y.set)

        canvas.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scroll_y.pack(side=tk.RIGHT, fill=tk.Y)

        tb.Label(inner, text="Vendas Abertas:", font=("Arial", 11, "bold")).pack(anchor=tk.W, pady=10, padx=10)

        tree_frame = tb.Frame(inner)
        tree_frame.pack(fill=tk.BOTH, expand=True, padx=10)

        tree = tb.Treeview(tree_frame, columns=["ID", "Vendedor", "Cliente", "Data", "Total"], height=12)
        tree.column("#0", width=0, stretch=tk.NO)
        for col in ["ID", "Vendedor", "Cliente", "Data", "Total"]:
            tree.column(col, anchor=tk.W, width=100)
            tree.heading(col, text=col, anchor=tk.W)

        tree_scroll = tb.Scrollbar(tree_frame, orient=tk.VERTICAL, command=tree.yview)
        tree.configure(yscroll=tree_scroll.set)
        tree_scroll.pack(side=tk.RIGHT, fill=tk.Y)
        tree.pack(fill=tk.BOTH, expand=True)

        for venda in vendas_abertas:
            tree.insert("", "end", values=(venda[0], venda[1], venda[2], venda[3][:10], f"R$ {venda[4]:.2f}"))

        btn_frame = tb.Frame(inner)
        btn_frame.pack(fill=tk.X, pady=10, padx=10)

        def abrir_venda():
            if not tree.selection():
                messagebox.showwarning("Aviso", "Selecione uma venda!")
                return

            venda_id = int(tree.item(tree.selection())['values'][0])
            janela.destroy()
            self.editar_venda(venda_id)

        tb.Button(btn_frame, text="Continuar", command=abrir_venda).pack(side=tk.RIGHT)
    
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
    
    def janela_formulario(self, titulo, campos, callback, refresh_callback):
        janela = tk.Toplevel(self.root)
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

        tb.Button(btn_frame, text="✅ Confirmar Devolução", bootstyle=SUCCESS, command=processar_devolucao, style='Normal.TButton').pack(side=RIGHT, padx=10)
        tb.Button(btn_frame, text="⬅ Voltar", command=self.criar_tela_inicial, style='Normal.TButton').pack(side=RIGHT)

if __name__ == "__main__":
    root = tk.Tk()
    app = BibliotecaApp(root)
    root.mainloop()