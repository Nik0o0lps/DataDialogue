"""
Testes para o módulo de banco de dados.
"""
import pytest
import pandas as pd
from src.utils.database import DatabaseManager


def test_get_connection(db_manager):
    """Testa criação de conexão com o banco."""
    conn = db_manager.get_connection()
    assert conn is not None
    conn.close()


def test_get_schema(db_manager):
    """Testa obtenção do schema do banco."""
    schema = db_manager.get_schema()
    assert isinstance(schema, dict)
    assert len(schema) > 0
    
    # Verificar se tem as tabelas esperadas (schema real do banco)
    expected_tables = ['campanhas_marketing', 'clientes', 'compras', 'suporte']
    for table in expected_tables:
        assert table in schema, f"Tabela {table} não encontrada no schema"


def test_get_schema_text(db_manager):
    """Testa formatação de schema em texto."""
    schema_text = db_manager.get_schema_text()
    assert isinstance(schema_text, str)
    assert len(schema_text) > 0
    assert 'Tabela:' in schema_text
    assert 'Colunas:' in schema_text


def test_execute_simple_query(db_manager):
    """Testa execução de query simples de contagem."""
    success, result = db_manager.execute_query("SELECT COUNT(*) as total FROM clientes")
    assert success is True
    assert isinstance(result, pd.DataFrame)
    assert 'total' in result.columns
    assert result['total'][0] > 0


def test_execute_query_with_filter(db_manager):
    """Testa query com filtro WHERE."""
    success, result = db_manager.execute_query(
        "SELECT COUNT(*) as total FROM compras WHERE canal = 'App'"
    )
    assert success is True
    assert isinstance(result, pd.DataFrame)
    assert 'total' in result.columns


def test_execute_invalid_query(db_manager):
    """Testa tratamento de query inválida."""
    success, result = db_manager.execute_query("SELECT * FROM tabela_que_nao_existe")
    assert success is False
    assert "Erro" in result  # Deve retornar mensagem de erro


def test_distinct_values_in_schema(db_manager):
    """Testa se schema contém valores distintos das colunas."""
    schema_text = db_manager.get_schema_text()
    
    # Deve conter exemplos de valores distintos ou ranges
    assert ('Valores distintos' in schema_text or 
            'Range de' in schema_text), \
            "Schema deve conter valores distintos ou ranges"


def test_query_with_join(db_manager):
    """Testa query com JOIN entre tabelas."""
    success, result = db_manager.execute_query("""
        SELECT c.nome, COUNT(co.id) as total_compras
        FROM clientes c
        LEFT JOIN compras co ON c.id = co.cliente_id
        GROUP BY c.id, c.nome
        LIMIT 5
    """)
    assert success is True
    assert isinstance(result, pd.DataFrame)
    assert 'nome' in result.columns
    assert 'total_compras' in result.columns
    assert len(result) <= 5


def test_query_with_aggregation(db_manager):
    """Testa query com agregação."""
    success, result = db_manager.execute_query("""
        SELECT canal, COUNT(*) as total
        FROM compras
        GROUP BY canal
        ORDER BY total DESC
    """)
    assert success is True
    assert isinstance(result, pd.DataFrame)
    assert 'canal' in result.columns
    assert 'total' in result.columns
    assert len(result) > 0
