import sqlite3

def atualizar_banco():
    try:
        # Conecta ao seu arquivo de banco de dados
        conexao = sqlite3.connect('biblioteca.db')
        cursor = conexao.cursor()

        # Comando para adicionar a nova coluna de controle de devolução
        # O 'DEFAULT 0' garante que todos os itens antigos comecem com zero devolvidos
        cursor.execute("ALTER TABLE itens_venda ADD COLUMN quantidade_devolvida INTEGER DEFAULT 0")

        conexao.commit()
        print("✅ Coluna 'quantidade_devolvida' adicionada com sucesso!")
        
    except sqlite3.OperationalError as e:
        if "duplicate column name" in str(e).lower():
            print("⚠️ A coluna já existe no banco de dados.")
        else:
            print(f"❌ Erro operacional: {e}")
    except Exception as e:
        print(f"❌ Ocorreu um erro: {e}")
    finally:
        conexao.close()

if __name__ == "__main__":
    atualizar_banco()