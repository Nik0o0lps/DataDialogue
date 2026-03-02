import sqlite3

# Conectar ao banco de dados
conn = sqlite3.connect('anexo_desafio_1.db')
cursor = conn.cursor()

# Listar todas as tabelas
cursor.execute("SELECT name FROM sqlite_master WHERE type='table'")
tables = cursor.fetchall()

print("=" * 80)
print("ESTRUTURA DO BANCO DE DADOS")
print("=" * 80)
print(f"\nTotal de tabelas: {len(tables)}\n")

for table in tables:
    table_name = table[0]
    print(f"\n{'='*80}")
    print(f"Tabela: {table_name}")
    print(f"{'='*80}")
    
    # Obter schema da tabela
    cursor.execute(f"PRAGMA table_info({table_name})")
    columns = cursor.fetchall()
    
    print("\nColunas:")
    for col in columns:
        col_id, col_name, col_type, not_null, default_val, pk = col
        pk_str = " (PRIMARY KEY)" if pk else ""
        not_null_str = " NOT NULL" if not_null else ""
        print(f"  - {col_name}: {col_type}{pk_str}{not_null_str}")
    
    # Contar registros
    cursor.execute(f"SELECT COUNT(*) FROM {table_name}")
    count = cursor.fetchone()[0]
    print(f"\nTotal de registros: {count}")
    
    # Mostrar alguns exemplos de dados
    if count > 0:
        cursor.execute(f"SELECT * FROM {table_name} LIMIT 3")
        rows = cursor.fetchall()
        print(f"\nExemplos de dados (primeiros 3 registros):")
        for i, row in enumerate(rows, 1):
            print(f"\n  Registro {i}:")
            for j, value in enumerate(row):
                print(f"    {columns[j][1]}: {value}")

conn.close()
print("\n" + "=" * 80)
