"""
Configuração de fixtures para pytest.
"""
import pytest
import os
from pathlib import Path
from src.agents.sql_agent import SQLAgent
from src.utils.database import DatabaseManager

@pytest.fixture(scope="session")
def test_db_path():
    """Caminho do banco de dados de teste."""
    return "anexo_desafio_1.db"

@pytest.fixture(scope="session")
def db_manager(test_db_path):
    """Instância do DatabaseManager para testes."""
    return DatabaseManager(test_db_path)

@pytest.fixture(scope="function")
def sql_agent(test_db_path):
    """
    Instância do SQLAgent para cada teste.
    Nota: Requer GROQ_API_KEY ou OPENAI_API_KEY configurada.
    """
    # Verificar se tem API key
    if not (os.getenv('GROQ_API_KEY') or os.getenv('OPENAI_API_KEY')):
        pytest.skip("API key não configurada")
    
    return SQLAgent(db_path=test_db_path)

@pytest.fixture
def sample_questions():
    """Perguntas de exemplo para testes."""
    return [
        "Quantos clientes temos no total?",
        "Liste os 5 estados com maior número de clientes",
        "Qual categoria teve mais vendas em 2024?",
        "Qual a média de valor das compras?",
        "Quantas compras foram feitas via App?"
    ]
