"""
Aplicação Streamlit - Assistente Virtual de Dados
Interface para interagir com o agente SQL inteligente.
"""
import streamlit as st
import sys
from pathlib import Path
import os
from dotenv import load_dotenv
import pandas as pd

# Carregar variáveis de ambiente
load_dotenv()

# Adicionar o diretório atual ao path
sys.path.insert(0, str(Path(__file__).parent))

from src.agents.sql_agent import SQLAgent
from src.utils.visualizations import DataVisualizer

# Configuração da página
st.set_page_config(
    page_title="Assistente Virtual de Dados",
    layout="wide",
    initial_sidebar_state="expanded"
)

# CSS customizado
st.markdown("""
<style>
    .main-header {
        font-size: 3rem;
        font-weight: bold;
        color: #1f77b4;
        text-align: center;
        margin-bottom: 1rem;
    }
    .sub-header {
        text-align: center;
        color: #666;
        margin-bottom: 2rem;
    }
    .reasoning-step {
        padding: 0.5rem;
        margin: 0.3rem 0;
        background-color: #f0f2f6;
        border-radius: 5px;
        font-family: monospace;
    }
    .sql-query {
        background-color: #282c34;
        color: #61dafb;
        padding: 1rem;
        border-radius: 5px;
        font-family: 'Courier New', monospace;
        overflow-x: auto;
    }
    .example-question {
        background-color: #e8f4f8;
        padding: 0.8rem;
        margin: 0.5rem 0;
        border-radius: 5px;
        border-left: 4px solid #1f77b4;
        cursor: pointer;
    }
    .example-question:hover {
        background-color: #d1e7f0;
    }
</style>
""", unsafe_allow_html=True)


def initialize_agent():
    """Inicializa o agente SQL (com cache)."""
    if 'agent' not in st.session_state:
        with st.spinner("Inicializando agente inteligente..."):
            try:
                st.session_state.agent = SQLAgent(db_path="anexo_desafio_1.db")
                st.session_state.agent_ready = True
                
                # Mostrar qual API está sendo usada
                if os.getenv("GROQ_API_KEY"):
                    st.sidebar.success("Usando Groq (gratuito e rápido!)")
                elif os.getenv("OPENAI_API_KEY"):
                    st.sidebar.success("Usando OpenAI GPT")
                    
            except Exception as e:
                st.error(f"Erro ao inicializar agente: {str(e)}")
                st.info("Verifique se sua chave da API está configurada no arquivo .env")
                st.info("Para Groq: GROQ_API_KEY no .env")
                st.info("Para OpenAI: OPENAI_API_KEY no .env")
                st.session_state.agent_ready = False


def main():
    """Função principal da aplicação."""
    
    # Header
    st.markdown('<div class="main-header">Assistente Virtual de Dados</div>', unsafe_allow_html=True)
    st.markdown('<div class="sub-header">Faça perguntas sobre seus dados em linguagem natural</div>', unsafe_allow_html=True)
    
    # Inicializar agente
    initialize_agent()
    
    # Sidebar
    with st.sidebar:
        st.title("Sobre")
        st.info(
            """
            Este assistente usa **Inteligência Artificial** para:
            
            - Entender perguntas em linguagem natural  
            - Gerar queries SQL automaticamente  
            - Executar e corrigir erros sozinho  
            - Criar visualizações inteligentes  
            
            **Tecnologias:**
            - LangChain & LangGraph
            - Groq / OpenAI GPT
            - SQLite
            - Streamlit
            """
        )
        
        st.divider()
        
        st.title("Exemplos de Perguntas")
        
        example_questions = [
            "Liste os 5 estados com maior número de clientes que compraram via app em maio",
            "Quantos clientes interagiram com campanhas de WhatsApp em 2024?",
            "Quais categorias de produto tiveram o maior número de compras em média por cliente?",
            "Qual o número de reclamações não resolvidas por canal?",
            "Qual a tendência de reclamações por canal no último ano?",
            "Quais os 10 clientes que mais gastaram?",
            "Qual a média de idade dos clientes por estado?",
            "Quantas compras foram feitas por canal em 2024?",
        ]
        
        for i, question in enumerate(example_questions):
            if st.button(f"{question[:50]}...", key=f"example_{i}", use_container_width=True):
                st.session_state.current_question = question
                st.rerun()
    
    # Área principal
    if not st.session_state.get('agent_ready', False):
        st.warning("Agente não está pronto. Configure sua API key no arquivo .env")
        st.code("""
# Crie um arquivo .env com uma das opções:

# Opção 1 - Groq (gratuito e rápido!)
GROQ_API_KEY=sua_chave_groq_aqui
GROQ_MODEL=llama-3.3-70b-versatile

# Opção 2 - OpenAI
OPENAI_API_KEY=sua_chave_openai_aqui
        """, language="bash")
        st.info("Groq API (gratuita): https://console.groq.com/keys")
        st.info("OpenAI API: https://platform.openai.com/api-keys")
        return
    
    # Input de pergunta
    st.subheader("Faça sua pergunta")
    
    # Usar pergunta dos exemplos se houver
    default_question = st.session_state.get('current_question', '')
    
    question = st.text_area(
        "Digite sua pergunta sobre os dados:",
        value=default_question,
        height=100,
        placeholder="Ex: Quantos clientes compraram via app em maio de 2024?"
    )
    
    col1, col2 = st.columns([1, 5])
    with col1:
        search_button = st.button("Buscar", type="primary", use_container_width=True)
    with col2:
        if st.button("Limpar", use_container_width=True):
            st.session_state.current_question = ''
            st.rerun()
    
    # Processar pergunta
    if search_button and question:
        with st.spinner("Analisando sua pergunta..."):
            try:
                # Executar query
                result = st.session_state.agent.query(question)
                
                # Mostrar raciocínio
                with st.expander("Ver Raciocínio do Agente", expanded=True):
                    for step in result['reasoning_steps']:
                        st.markdown(f'<div class="reasoning-step">{step}</div>', unsafe_allow_html=True)
                
                # Mostrar query SQL
                st.subheader("Query SQL Gerada")
                st.code(result['sql_query'], language="sql")
                
                # Mostrar resposta
                st.subheader("Resposta")
                st.success(result['answer'])
                
                # Mostrar dados
                if result['data'] is not None and isinstance(result['data'], pd.DataFrame):
                    st.subheader("Dados")
                    
                    # Criar tabs para diferentes visualizações
                    tab1, tab2 = st.tabs(["Visualização", "Tabela"])
                    
                    with tab1:
                        # Tentar criar visualização automática
                        visualizer = DataVisualizer()
                        fig = visualizer.auto_visualize(result['data'], question)
                        
                        if fig:
                            st.plotly_chart(fig, use_container_width=True)
                        else:
                            st.info("Dados exibidos em formato de tabela")
                            # Ajustar altura baseada no número de linhas (40px por linha + header)
                            num_rows = len(result['data'])
                            table_height = min(40 + (num_rows * 35), 400)
                            st.dataframe(result['data'], use_container_width=True, height=table_height, hide_index=True)
                    
                    with tab2:
                        # Ajustar altura baseada no número de linhas
                        num_rows = len(result['data'])
                        table_height = min(40 + (num_rows * 35), 400)
                        st.dataframe(result['data'], use_container_width=True, height=table_height, hide_index=True)
                        
                        # Mostrar resumo
                        st.caption(f"Total de {num_rows} {'registro' if num_rows == 1 else 'registros'}")
                        
                        # Botão para download
                        csv = result['data'].to_csv(index=False).encode('utf-8')
                        st.download_button(
                            label="Download CSV",
                            data=csv,
                            file_name="resultado.csv",
                            mime="text/csv"
                        )
                
            except Exception as e:
                st.error(f"Erro ao processar pergunta: {str(e)}")
                st.exception(e)
    
    # Footer
    st.divider()
    st.markdown(
        """
        <div style="text-align: center; color: #666; padding: 2rem;">
            Desenvolvido usando LangChain, LangGraph e Streamlit
        </div>
        """,
        unsafe_allow_html=True
    )


if __name__ == "__main__":
    main()
