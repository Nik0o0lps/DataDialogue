"""
Script para testar o agente SQL localmente (sem interface).
Use para validar queries e testar o funcionamento do agente.
"""
import os
import sys
from pathlib import Path
from dotenv import load_dotenv

# Carregar variáveis de ambiente
load_dotenv()

# Adicionar src ao path
sys.path.insert(0, str(Path(__file__).parent))

from src.agents.sql_agent import SQLAgent


def test_agent():
    """Testa o agente com várias perguntas."""
    
    print("=" * 80)
    print("TESTE DO AGENTE SQL")
    print("=" * 80)
    print()
    
    # Verificar API key
    if not os.getenv("OPENAI_API_KEY"):
        print("ERRO: OPENAI_API_KEY não configurada!")
        print("Configure no arquivo .env")
        return
    
    print("API Key encontrada")
    print()
    
    # Inicializar agente
    print("Inicializando agente...")
    try:
        agent = SQLAgent(db_path="anexo_desafio_1.db")
        print("Agente inicializado com sucesso!")
        print()
    except Exception as e:
        print(f"Erro ao inicializar: {e}")
        return
    
    # Perguntas de teste
    test_questions = [
        "Quantos clientes temos no total?",
        "Liste os 5 estados com maior número de clientes",
        "Quantas compras foram feitas via App em 2024?",
        "Qual a média de idade dos clientes?",
    ]
    
    for i, question in enumerate(test_questions, 1):
        print("=" * 80)
        print(f"TESTE {i}/{len(test_questions)}")
        print("=" * 80)
        print(f"\nPergunta: {question}\n")
        
        try:
            # Executar query
            result = agent.query(question)
            
            # Mostrar raciocínio
            print("Raciocínio do Agente:")
            for step in result['reasoning_steps']:
                print(f"   {step}")
            print()
            
            # Mostrar SQL
            print(f"SQL Gerado:\n{result['sql_query']}\n")
            
            # Mostrar resposta
            print(f"Resposta:\n{result['answer']}\n")
            
            # Mostrar dados (primeiras linhas)
            if result['data'] is not None:
                print("Dados (primeiras 5 linhas):")
                print(result['data'].head().to_string())
                print()
            
            print("Teste bem-sucedido!\n")
            
        except Exception as e:
            print(f"Erro no teste: {e}\n")
    
    print("=" * 80)
    print("TESTES CONCLUÍDOS")
    print("=" * 80)


if __name__ == "__main__":
    test_agent()
