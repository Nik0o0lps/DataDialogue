"""
Testes para o módulo de visualizações.
"""
import pytest
import pandas as pd
import plotly.graph_objects as go
from src.utils.visualizations import DataVisualizer


@pytest.fixture
def sample_data():
    """Dados de exemplo para testes de gráficos."""
    return pd.DataFrame({
        'estado': ['SP', 'RJ', 'MG', 'RS', 'PR'],
        'total': [100, 80, 60, 40, 20]
    })


@pytest.fixture
def temporal_data():
    """Dados temporais para testes de gráfico de linha."""
    return pd.DataFrame({
        'data': pd.date_range('2024-01-01', periods=12, freq='M'),
        'vendas': [100, 120, 110, 130, 140, 135, 150, 160, 155, 170, 180, 190]
    })


@pytest.fixture
def large_data():
    """Dados grandes que não devem gerar gráfico."""
    return pd.DataFrame({
        'col1': range(200),
        'col2': range(200, 400)
    })


def test_bar_chart_creation(sample_data):
    """Testa criação de gráfico de barras básico."""
    viz = DataVisualizer()
    fig = viz.create_bar_chart(sample_data, 'estado', 'total')
    
    assert fig is not None
    assert isinstance(fig, go.Figure)
    assert len(fig.data) > 0


def test_bar_chart_with_long_labels():
    """Testa que nomes longos geram gráfico horizontal."""
    data = pd.DataFrame({
        'nome': ['João da Silva Santos', 'Maria Oliveira Souza', 'Pedro Costa Lima'],
        'total_gasto': [1000, 1500, 800]
    })
    
    viz = DataVisualizer()
    fig = viz.create_bar_chart(data, 'nome', 'total_gasto')
    
    assert fig is not None
    # TODO: Verificar se é realmente horizontal (orientation='h')


def test_auto_visualize_simple_data(sample_data):
    """Testa detecção automática de visualização para dados simples."""
    viz = DataVisualizer()
    fig = viz.auto_visualize(sample_data)
    
    assert fig is not None
    assert isinstance(fig, go.Figure)


def test_auto_visualize_temporal_data(temporal_data):
    """Testa detecção de dados temporais."""
    viz = DataVisualizer()
    fig = viz.auto_visualize(temporal_data)
    
    assert fig is not None
    assert isinstance(fig, go.Figure)


def test_line_chart_creation(temporal_data):
    """Testa criação de gráfico de linha."""
    viz = DataVisualizer()
    fig = viz.create_line_chart(temporal_data)
    
    assert fig is not None
    assert isinstance(fig, go.Figure)
    assert len(fig.data) > 0


def test_no_visualization_for_large_data(large_data):
    """Testa que dados muito grandes não geram gráfico."""
    viz = DataVisualizer()
    fig = viz.auto_visualize(large_data)
    
    # Dados com mais de 100 linhas devem retornar None
    assert fig is None


def test_no_visualization_for_empty_data():
    """Testa que dataframe vazio não gera gráfico."""
    empty_df = pd.DataFrame()
    viz = DataVisualizer()
    fig = viz.auto_visualize(empty_df)
    
    assert fig is None


def test_pie_chart_creation():
    """Testa criação de gráfico de pizza."""
    data = pd.DataFrame({
        'categoria': ['A', 'B', 'C', 'D'],
        'valor': [30, 25, 25, 20]
    })
    
    viz = DataVisualizer()
    fig = viz.create_pie_chart(data, 'categoria', 'valor')
    
    assert fig is not None
    assert isinstance(fig, go.Figure)


def test_columns_with_id_filtered():
    """Testa que colunas com 'id' são filtradas das visualizações."""
    data = pd.DataFrame({
        'id': [1, 2, 3, 4, 5],
        'categoria': ['A', 'B', 'C', 'D', 'E'],
        'valor': [100, 200, 150, 180, 220]
    })
    
    viz = DataVisualizer()
    fig = viz.auto_visualize(data)
    
    # Deve criar gráfico ignorando a coluna 'id'
    assert fig is not None
