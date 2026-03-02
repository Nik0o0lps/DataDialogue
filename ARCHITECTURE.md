#  Arquitetura Detalhada do Sistema

## Visão Geral

O Assistente Virtual de Dados é construído com uma arquitetura modular baseada em agentes inteligentes usando **LangGraph**, uma biblioteca para orquestração de fluxos com LLMs.

## Componentes Principais

### 1. SQLAgent (Motor de IA)

**Arquivo:** `src/agents/sql_agent.py`

**Responsabilidade:** Core do sistema - gerencia todo o fluxo de processamento de perguntas.

#### Estados do Agente (AgentState)

```python
class AgentState(TypedDict):
    messages: List[BaseMessage]      # Histórico de mensagens
    question: str                     # Pergunta original
    schema: str                       # Schema do banco
    sql_query: str                    # Query SQL gerada
    query_result: Any                 # Resultado da query
    error_message: str                # Mensagem de erro (se houver)
    attempt_count: int                # Número de tentativas
    final_answer: str                 # Resposta final formatada
    reasoning_steps: List[str]        # Passos de raciocínio
```

#### Grafo de Estados (LangGraph)

```

  analyze_question     ← Entrada: Pergunta do usuário
                         Obtém schema do banco

           
           

   generate_sql        ← Gera query SQL usando LLM
                         Considera contexto e schema

           
           

   execute_sql         ← Executa query no SQLite
                         Captura erros se houver

           
           
     [Decisão: sucesso?]
           
            SIM 
                      
               
                 format_answer        ← Formata resposta final
                                        Gera texto em português
               
                          
           NO              
                       [END]
           
    
       handle_error        ← Analisa erro
                             Prepara correção
    
               
               [retry: max 3x]
                                   
               
               
        [volta para generate_sql]
```

#### Fluxo Detalhado

**1. analyze_question**
```python
- Input: Pergunta do usuário
- Ações:
  1. Obtém schema completo do banco (DatabaseManager)
  2. Cria mensagem de sistema com contexto
  3. Inicializa tracking de raciocínio
- Output: Estado atualizado com schema
```

**2. generate_sql**
```python
- Input: Pergunta + Schema (+ erro se retry)
- Ações:
  1. Monta prompt para o LLM com contexto
  2. Se é retry, inclui erro anterior
  3. Invoca LLM (ChatOpenAI)
  4. Extrai SQL da resposta
  5. Remove formatação markdown se houver
- Output: Query SQL gerada
```

**3. execute_sql**
```python
- Input: Query SQL
- Ações:
  1. Executa query via DatabaseManager
  2. Captura resultado ou erro
- Output: 
  - Sucesso: DataFrame com dados
  - Erro: Mensagem de erro detalhada
```

**4. handle_error** (se necessário)
```python
- Input: Erro + Query que falhou
- Ações:
  1. Registra tentativa
  2. Prepara contexto para correção
- Output: Estado pronto para retry
```

**5. format_answer**
```python
- Input: Dados + Query bem-sucedida
- Ações:
  1. Invoca LLM para gerar resposta em português
  2. Inclui insights dos dados
  3. Mantém tom conversacional
- Output: Resposta final formatada
```

### 2. DatabaseManager (Gerenciador de Dados)

**Arquivo:** `src/utils/database.py`

**Responsabilidade:** Abstração para operações com SQLite.

#### Métodos Principais

```python
class DatabaseManager:
    
    def get_schema() -> Dict
        """
        Descobre schema dinamicamente.
        Retorna estrutura completa: tabelas, colunas, tipos.
        """
    
    def get_schema_text() -> str
        """
        Formata schema para LLM (texto legível).
        Inclui contagem de registros.
        """
    
    def execute_query(query: str) -> Tuple[bool, Any]
        """
        Executa query com tratamento de erros.
        Retorna: (sucesso, resultado_ou_erro)
        """
    
    def get_sample_data(table: str, limit: int) -> DataFrame
        """
        Obtém amostras para contexto.
        """
```

### 3. DataVisualizer (Visualizações)

**Arquivo:** `src/utils/visualizations.py`

**Responsabilidade:** Criação automática de gráficos apropriados.

#### Lógica de Decisão

```python
def auto_visualize(df: DataFrame) -> Figure:
    """
    Detecta tipo de dados e escolhe visualização:
    
    1. Uma coluna categórica + uma numérica
       → Gráfico de Barras
    
    2. Dados temporais (coluna de data)
       → Gráfico de Linhas
    
    3. Distribuição (≤10 categorias)
       → Gráfico de Pizza (Donut)
    
    4. Comparação entre categorias
       → Barras Agrupadas
    
    5. Muitos dados (>100 linhas ou >10 colunas)
       → Apenas Tabela
    """
```

#### Tipos de Gráficos

- **Barras:** Comparações, rankings
- **Linhas:** Tendências temporais
- **Pizza/Donut:** Distribuições, proporções
- **Barras Agrupadas:** Comparações multidimensionais

### 4. Interface Streamlit

**Arquivo:** `app.py`

**Responsabilidade:** UI/UX - interface web interativa.

#### Estrutura da Interface

```

                    HEADER & TÍTULO                          

                                                            
   SIDEBAR                ÁREA PRINCIPAL                    
                                                            
  - Info               
  - Exemplos        Input de Pergunta                    
  - Tecnologias        
                                                            
                       
                     Raciocínio (expandível)           
                       
                                                            
                       
                     Query SQL                         
                       
                                                            
                       
                     Resposta em Texto                 
                       
                                                            
                       
                    Tabs: Gráfico | Tabela               
                       
                                                            

```

#### Funcionalidades

1. **Entrada de Pergunta**
   - Text area para perguntas livres
   - Botões de exemplo (sidebar)
   - Validação de entrada

2. **Processamento**
   - Spinner com feedback
   - Execução do agente
   - Tratamento de erros

3. **Exibição de Resultados**
   - Raciocínio (passos do agente)
   - Query SQL formatada
   - Resposta em linguagem natural
   - Dados (tabela + gráfico)
   - Download CSV

4. **Estado da Sessão**
   ```python
   st.session_state.agent          # Agente (cache)
   st.session_state.current_question  # Pergunta ativa
   st.session_state.agent_ready    # Status
   ```

## Fluxo de Dados Completo

```

 Usuário  
 digita   
 pergunta 

     
     

  app.py        
  (Streamlit)   

      question
     

  SQLAgent.query()                          
                                            
  1. analyze_question                       
     - DatabaseManager.get_schema()         
     - Prepara contexto para LLM            
                                            
  2. generate_sql                           
     - ChatOpenAI.invoke()                  
     - Extrai SQL da resposta               
                                            
  3. execute_sql                            
     - DatabaseManager.execute_query()      
     - sqlite3.execute()                    
                                            
  [Se erro: handle_error → retry 2, 3]     
                                            
  4. format_answer                          
     - ChatOpenAI.invoke()                  
     - Gera resposta em português           
                                            

      {answer, data, sql, steps}
     

  app.py        
  (Streamlit)   
                
  - Mostra steps
  - Mostra SQL  
  - Mostra answer
  - Mostra data 

      data (DataFrame)
     

  DataVisualizer        
  .auto_visualize()     
                        
  - Detecta tipo        
  - Cria Plotly figure  

      figure
     

  st.plotly_    
  chart()       

```

## Padrões de Design Utilizados

### 1. State Machine (LangGraph)
- Estados bem definidos
- Transições claras
- Fluxo determinístico com decisões

### 2. Strategy Pattern (Visualizações)
- Detecta tipo de dado
- Escolhe estratégia de visualização
- Implementa renderização

### 3. Singleton (Session State)
- Agente instanciado uma vez
- Cache de conexão
- Estado persistente

### 4. Facade (DatabaseManager)
- Interface simples para operações complexas
- Esconde detalhes de SQLite
- Tratamento centralizado de erros

## Pontos de Extensão

### 1. Adicionar Novos Tipos de Visualização
```python
# Em visualizations.py
@staticmethod
def create_heatmap(df: DataFrame) -> Figure:
    # Nova visualização
    pass

# Adicionar à decisão em auto_visualize()
if condição_para_heatmap:
    return create_heatmap(df)
```

### 2. Suportar Outros Bancos
```python
# Criar src/utils/postgres_manager.py
class PostgresManager(DatabaseManager):
    def get_connection(self):
        return psycopg2.connect(...)
```

### 3. Adicionar Novos Agentes
```python
# src/agents/chart_agent.py
class ChartAgent:
    """Agente especializado em recomendar gráficos"""
    pass

# Orquestrar com SQLAgent via LangGraph
```

### 4. Implementar Memória
```python
# Em sql_agent.py
class SQLAgent:
    def __init__(self, ...):
        self.memory = ConversationBufferMemory()
    
    def query(self, question):
        # Incluir histórico no contexto
        history = self.memory.load_memory_variables({})
        ...
```

## Segurança e Boas Práticas

### 1. Validação de SQL
- Apenas SELECT queries são executadas por padrão
- Sem DELETE, DROP, UPDATE não aprovados
- Timeout para queries longas (futuro)

### 2. Gestão de API Keys
- Nunca commitar .env
- Usar variáveis de ambiente
- Validação antes de uso

### 3. Tratamento de Erros
- Try-catch em todos os pontos críticos
- Mensagens claras para usuário
- Logs para debugging (futuro)

### 4. Performance
- Cache do schema (não muda frequentemente)
- Limite de tentativas (max 3)
- Reuso da conexão LLM

## Métricas e Observabilidade (Futuro)

```python
# Tracking de uso
metrics = {
    "total_queries": count,
    "success_rate": percentage,
    "avg_response_time": seconds,
    "retry_rate": percentage,
    "tokens_used": count,
    "cost": dollars
}
```

## Conclusão

A arquitetura foi projetada para ser:
-  **Modular**: Componentes independentes
-  **Extensível**: Fácil adicionar funcionalidades
-  **Robusta**: Tratamento de erros e retries
-  **Transparente**: Mostra raciocínio completo
-  **Inteligente**: Usa LLM para decisões complexas

O uso de **LangGraph** permite criar fluxos sofisticados mantendo o código limpo e testável.

