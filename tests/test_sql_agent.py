"""
Testes para o agente SQL inteligente.
"""
import pytest
import os
from unittest.mock import Mock, patch
from src.agents.sql_agent import SQLAgent


def test_agent_initialization():
    """Testa inicialização do agente."""
    # Skip se não tiver API key
    if not (os.getenv('GROQ_API_KEY') or os.getenv('OPENAI_API_KEY')):
        pytest.skip("API key não configurada")
    
    agent = SQLAgent()
    assert agent is not None
    assert agent.db is not None
    assert agent.llm is not None
    assert agent.graph is not None


@pytest.mark.skip(reason="Requer API key válida e consome créditos")
def test_simple_count_query(sql_agent):
    """Testa query simples de contagem."""
    result = sql_agent.query("Quantos clientes temos?")
    
    assert result is not None
    assert 'success' in result
    assert result['success'] is True
    assert result['data'] is not None
    assert 'sql_query' in result
    assert 'SELECT' in result['sql_query'].upper()
    assert 'COUNT' in result['sql_query'].upper()


@pytest.mark.skip(reason="Requer API key válida e consome créditos")
def test_top_n_query(sql_agent):
    """Testa query com TOP N (limite)."""
    result = sql_agent.query("Liste os 5 estados com mais clientes")
    
    assert result['success']
    assert len(result['data']) <= 5
    assert 'LIMIT' in result['sql_query'].upper()


@pytest.mark.skip(reason="Requer API key válida e consome créditos")
def test_query_with_filter(sql_agent):
    """Testa query com filtro WHERE."""
    result = sql_agent.query("Quantas compras foram feitas via App?")
    
    assert result['success']
    assert 'WHERE' in result['sql_query'].upper()
    assert 'App' in result['sql_query'] or 'app' in result['sql_query'].lower()


def test_reasoning_steps_returned(sql_agent):
    """Testa se reasoning steps são retornados no resultado."""
    if not (os.getenv('GROQ_API_KEY') or os.getenv('OPENAI_API_KEY')):
        pytest.skip("API key não configurada")
    
    # Não vamos executar query real, apenas verificar estrutura
    # TODO: Implementar com mocks
    pass


@pytest.mark.parametrize("question,expected_keyword", [
    ("Quantos clientes", "COUNT"),
    ("média de valor", "AVG"),
    ("total de vendas", "SUM"),
    ("maior valor", "MAX"),
    ("menor valor", "MIN"),
])
@pytest.mark.skip(reason="Requer implementação com mocks")
def test_query_type_detection(question, expected_keyword):
    """Testa se o tipo de agregação é detectado corretamente."""
    # TODO: Implementar com mocks do LLM
    pass


def test_agent_state_structure():
    """Testa estrutura do estado do agente."""
    from src.agents.sql_agent import AgentState
    
    # Verificar que AgentState tem os campos esperados
    # TypedDict não pode ser instanciado, mas podemos verificar annotations
    assert 'messages' in AgentState.__annotations__
    assert 'question' in AgentState.__annotations__
    assert 'sql_query' in AgentState.__annotations__
    assert 'query_result' in AgentState.__annotations__
    assert 'error_message' in AgentState.__annotations__


@pytest.mark.skip(reason="Requer API key e implementação de mock complexo")
def test_error_recovery_mechanism():
    """Testa mecanismo de retry quando SQL está errado."""
    # Mock do LLM que retorna SQL inválido na primeira vez
    # e válido na segunda
    # TODO: Implementar
    pass


@pytest.mark.skip(reason="Requer API key")
def test_multiple_questions(sql_agent, sample_questions):
    """Testa múltiplas perguntas sequenciais."""
    for question in sample_questions[:3]:  # Apenas 3 para não consumir muitos créditos
        result = sql_agent.query(question)
        assert result is not None
        assert 'answer' in result


def test_database_manager_integration():
    """Testa integração com DatabaseManager."""
    if not (os.getenv('GROQ_API_KEY') or os.getenv('OPENAI_API_KEY')):
        pytest.skip("API key não configurada")
    
    agent = SQLAgent()
    
    # Verificar que o agente tem acesso ao banco
    assert agent.db is not None
    
    # Verificar que consegue pegar o schema
    schema_text = agent.db.get_schema_text()
    assert isinstance(schema_text, str)
    assert len(schema_text) > 0
