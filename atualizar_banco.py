import sqlite3

def limpar_dados_preservando_cadastros():
    """
    Remove dados de movimentação (vendas, itens, estoque e inventário)
    Mantém: Clientes, Fornecedores e Vendedores.
    """
    try:
        conexao = sqlite3.connect('biblioteca.db')
        cursor = conexao.cursor()

        print("Refinando banco de dados... Aguarde.")

        # 1. Desativar chaves estrangeiras temporariamente para evitar erros de restrição
        cursor.execute("PRAGMA foreign_keys = OFF")

        # 2. Lista de tabelas para limpar (ordem importa se as chaves estivessem ON)
        tabelas_para_limpar = [
            'itens_venda',
            'vendas',
            'inventario_temp',
            'inventario_historico',
            'livros' # Livros costumam estar ligados a notas fiscais/estoque
        ]

        for tabela in tabelas_para_limpar:
            try:
                cursor.execute(f"DELETE FROM {tabela}")
                # Reinicia o contador de ID (autoincrement) para começar do 1 novamente
                cursor.execute(f"DELETE FROM sqlite_sequence WHERE name='{tabela}'")
                print(f"✔️ Dados da tabela '{tabela}' removidos.")
            except sqlite3.OperationalError as e:
                print(f"⚠️ Tabela '{tabela}' não encontrada ou já limpa.")

        # 3. Reativar chaves estrangeiras
        cursor.execute("PRAGMA foreign_keys = ON")

        conexao.commit()
        print("\n✅ Limpeza concluída! Cadastros de Clientes, Fornecedores e Vendedores foram preservados.")
        
    except Exception as e:
        print(f"❌ Erro ao limpar banco: {e}")
    finally:
        conexao.close()

if __name__ == "__main__":
    # Pergunta de segurança para não rodar por engano
    confirmacao = input("⚠️ Isso apagará todos os Livros e Vendas. Clientes/Fornecedores serão mantidos. Digite 'SIM' para continuar: ")
    if confirmacao.upper() == "SIM":
        limpar_dados_preservando_cadastros()
    else:
        print("Operação cancelada.")