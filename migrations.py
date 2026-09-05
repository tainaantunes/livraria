# migrations.py
"""
Sistema simples de versionamento de banco de dados usando PRAGMA user_version.
Cada migração é uma função que recebe o cursor e faz as alterações necessárias.
"""

# Lista de migrações, em ordem. O índice + 1 é a versão final após rodá-la.
# migrations[0] leva o banco da versão 0 -> 1
# migrations[1] leva o banco da versão 1 -> 2, etc.

def migracao_001(cursor):
    """Exemplo: adiciona coluna 'categoria' na tabela livros (caso ainda não exista)."""
    colunas = {row[1] for row in cursor.execute("PRAGMA table_info(livros)")}
    if 'categoria' not in colunas:
        cursor.execute("ALTER TABLE livros ADD COLUMN categoria TEXT")

def migracao_002(cursor):
    """Exemplo: cria tabela nova de log de auditoria."""
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS log_auditoria (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            usuario TEXT,
            acao TEXT,
            data TEXT
        )
    """)

def migracao_003(cursor):
    """Exemplo: adiciona coluna de desconto em vendas."""
    colunas = {row[1] for row in cursor.execute("PRAGMA table_info(vendas)")}
    if 'desconto' not in colunas:
        cursor.execute("ALTER TABLE vendas ADD COLUMN desconto REAL DEFAULT 0")

def migracao_004(cursor):
    """Cria o histórico de pagamentos por item para permitir baixa parcial."""
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS pagamentos_venda (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            item_venda_id INTEGER NOT NULL,
            quantidade INTEGER NOT NULL,
            valor REAL NOT NULL,
            metodo_pagamento TEXT NOT NULL,
            data_pagamento TEXT NOT NULL,
            FOREIGN KEY (item_venda_id) REFERENCES itens_venda(id)
        )
    """)

# Adicione novas funções aqui conforme o sistema evolui (migracao_004, 005...)
MIGRATIONS = [
    migracao_001,
    migracao_002,
    migracao_003,
    migracao_004,
]


def atualizar_banco(conexao, cursor):
    """
    Verifica a versão atual do banco e aplica as migrações pendentes.
    Deve ser chamada logo após abrir a conexão com o banco, antes de usar o app.
    """
    cursor.execute("PRAGMA user_version")
    versao_atual = cursor.fetchone()[0]
    versao_alvo = len(MIGRATIONS)

    if versao_atual >= versao_alvo:
        return  # já está atualizado

    print(f"Atualizando banco de dados: v{versao_atual} -> v{versao_alvo}...")

    for i in range(versao_atual, versao_alvo):
        migracao = MIGRATIONS[i]
        try:
            migracao(cursor)
            nova_versao = i + 1
            cursor.execute(f"PRAGMA user_version = {nova_versao}")
            conexao.commit()
            print(f"  -> Migração {nova_versao} aplicada com sucesso.")
        except Exception as e:
            conexao.rollback()
            raise RuntimeError(
                f"Falha ao aplicar migração {i + 1}: {e}\n"
                "Atualização do banco abortada. Nenhuma alteração parcial foi salva."
            )

    print("Banco de dados atualizado com sucesso!")
