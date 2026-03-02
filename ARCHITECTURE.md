# Arquitetura Detalhada do Sistema

## Visão Geral

O **DataDialogue** é construído com uma arquitetura modular baseada em agentes inteligentes usando **LangGraph**, uma biblioteca para orquestração de fluxos com LLMs. O sistema traduz perguntas em linguagem natural para queries SQL, executa-as e apresenta resultados com visualizações automáticas.

## Arquitetura de Alto Nível

```mermaid
graph LR
    subgraph "Camada de Apresentação"
        UI[Streamlit UI]
    end
    
    subgraph "Camada de Inteligência"
        AG[SQL Agent<br/>LangGraph]
        LLM[Groq LLM<br/>llama-3.3-70b]
    end
    
    subgraph "Camada de Dados"
        DB[(SQLite<br/>Database)]
        DM[Database<br/>Manager]
    end
    
    subgraph "Camada de Visualização"
        VIZ[Data<br/>Visualizer]
    end
    
    UI <-->|Perguntas/Respostas| AG
    AG <-->|Prompts/SQL| LLM
    AG <-->|Queries| DM
    DM <-->|Execute SQL| DB
    UI <-->|DataFrames| VIZ
    
    style UI fill:#e3f2fd
    style AG fill:#fff3e0
    style LLM fill:#f3e5f5
    style DB fill:#e0f2f1
    style DM fill:#e8f5e9
    style VIZ fill:#fce4ec
```

## Componentes Principais

### 1. SQLAgent (Motor de IA)

**Arquivo:** `src/agents/sql_agent.py`

**Responsabilidade:** Core do sistema - gerencia todo o fluxo de processamento de perguntas usando uma máquina de estados.

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

```mermaid
graph TB
    Start([Pergunta do Usuário]) --> A[analyze_question]
    A --> |Schema obtido| B[generate_sql]
    B --> |Query gerada| C[execute_sql]
    C --> |Verifica resultado| D{Query OK?}
    D --> |Sim| E[format_answer]
    E --> End([Resposta Final])
    D --> |Não| F[handle_error]
    F --> |Tentativa < 3| B
    F --> |Max tentativas| G([Erro Final])
    
    style Start fill:#e1f5e1
    style End fill:#e1f5e1
    style G fill:#ffe1e1
    style A fill:#e3f2fd
    style B fill:#fff3e0
    style C fill:#f3e5f5
    style D fill:#fff9c4
    style E fill:#e0f2f1
    style F fill:#ffebee
```

**Legenda:**
- **Entrada**: Pergunta em linguagem natural
- **Análise**: Obtém schema e prepara contexto
- **Geração**: LLM cria query SQL
- **Execução**: Roda query no banco
- **Decisão**: Verifica sucesso/erro
- **Formatação**: Resposta em português
- **Tratamento**: Recuperação de erros (até 3 tentativas)

#### Fluxo Detalhado de Cada Nó

```mermaid
flowchart TD
    subgraph "analyze_question"
        A1[Recebe pergunta do usuário]
        A2[Obtém schema via DatabaseManager]
        A3[Prepara contexto para LLM]
        A4[Inicializa tracking de raciocínio]
        A1 --> A2 --> A3 --> A4
    end
    
    subgraph "generate_sql"
        B1[Monta prompt com schema + pergunta]
        B2{É retry?}
        B2 -->|Sim| B3[Adiciona erro anterior ao prompt]
        B2 -->|Não| B4[Prompt padrão]
        B3 --> B5[Invoca LLM Groq]
        B4 --> B5
        B5 --> B6[Extrai SQL da resposta]
        B6 --> B7[Remove formatação markdown]
    end
    
    subgraph "execute_sql"
        C1[Recebe query SQL]
        C2[DatabaseManager.execute_query]
        C3{Sucesso?}
        C3 -->|Sim| C4[Retorna DataFrame]
        C3 -->|Não| C5[Retorna mensagem de erro]
    end
    
    subgraph "handle_error"
        D1[Recebe erro SQL]
        D2[Incrementa contador de tentativas]
        D3{Tentativas < 3?}
        D3 -->|Sim| D4[Prepara contexto para retry]
        D3 -->|Não| D5[Retorna erro final]
    end
    
    subgraph "format_answer"
        E1[Recebe dados + query]
        E2[Invoca LLM para formatação]
        E3[Gera resposta em português]
        E4[Adiciona insights dos dados]
        E1 --> E2 --> E3 --> E4
    end
    
    style A1 fill:#e3f2fd
    style B1 fill:#fff3e0
    style C1 fill:#f3e5f5
    style D1 fill:#ffebee
    style E1 fill:#e0f2f1
```

### 2. DatabaseManager (Gerenciador de Dados)

**Arquivo:** `src/utils/database.py`

**Responsabilidade:** Abstração para operações com SQLite.

```mermaid
classDiagram
    class DatabaseManager {
        +String db_path
        +get_connection() Connection
        +get_schema() Dict
        +get_schema_text() String
        +execute_query(query) Tuple
        +get_sample_data(table, limit) DataFrame
    }
    
    class SQLiteConnection {
        <<interface>>
        +execute()
        +fetchall()
        +commit()
    }
    
    DatabaseManager --> SQLiteConnection : usa
```

#### Métodos Principais

| Método | Entrada | Saída | Descrição |
|--------|---------|-------|-----------|
| `get_schema()` | - | `Dict[str, List[Dict]]` | Schema completo (tabelas, colunas, tipos) |
| `get_schema_text()` | - | `str` | Schema formatado para LLM com exemplos |
| `execute_query()` | `str` (SQL) | `Tuple[bool, Any]` | Executa query, retorna (sucesso, dados/erro) |
| `get_sample_data()` | `str, int` | `DataFrame` | Obtém exemplos de uma tabela |

### 3. DataVisualizer (Visualizações)

**Arquivo:** `src/utils/visualizations.py`

**Responsabilidade:** Criação automática de gráficos apropriados.

```mermaid
flowchart TD
    Start([DataFrame]) --> A{Filtrar colunas ID/códigos}
    A --> B{Quantidade de dados}
    B -->|> 100 linhas| NoViz[Apenas Tabela]
    B -->|<= 100 linhas| C{Tem coluna temporal?}
    C -->|Sim| Line[Gráfico de Linhas]
    C -->|Não| D{Quantas colunas?}
    D -->|1 categórica + 1 numérica| E{Orientação apropriada?}
    E -->|Labels longos| Horizontal[Barras Horizontais]
    E -->|Labels curtos| Vertical[Barras Verticais]
    D -->|<= 10 categorias| Pie[Gráfico de Pizza]
    D -->|Outro padrão| Table[Apenas Tabela]
    
    style Start fill:#e1f5e1
    style Line fill:#e3f2fd
    style Horizontal fill:#fff3e0
    style Vertical fill:#fff3e0
    style Pie fill:#f3e5f5
    style NoViz fill:#ffebee
    style Table fill:#e0f2f1
```

#### Tipos de Gráficos

| Tipo | Quando Usar | Características |
|------|-------------|-----------------|
| **Barras** | Comparações, rankings | Horizontal se labels > 15 chars |
| **Linhas** | Tendências temporais | Detecta colunas de data automaticamente |
| **Pizza (Donut)** | Distribuições ≤ 10 categorias | Mostra proporções |
| **Tabela** | > 100 linhas ou > 10 colunas | Fallback seguro |

### 4. Interface Streamlit

**Arquivo:** `app.py`

**Responsabilidade:** UI/UX - interface web interativa.

```mermaid
graph LR
    subgraph "Interface Streamlit"
        subgraph "Sidebar"
            S1[Informações]
            S2[Exemplos]
            S3[Tecnologias]
        end
        
        subgraph "Área Principal"
            M1[Input de Pergunta]
            M2[Raciocínio Expandível]
            M3[Query SQL Gerada]
            M4[Resposta em Texto]
            M5[Visualização]
            M6[Tabela de Dados]
            M7[Download CSV]
            
            M1 --> M2
            M2 --> M3
            M3 --> M4
            M4 --> M5
            M4 --> M6
            M6 --> M7
        end
    end
    
    style S1 fill:#e3f2fd
    style S2 fill:#fff3e0
    style S3 fill:#f3e5f5
    style M1 fill:#e1f5e1
    style M2 fill:#fff9c4
    style M3 fill:#ffebee
    style M4 fill:#e0f2f1
    style M5 fill:#f3e5f5
    style M6 fill:#e3f2fd
    style M7 fill:#e8f5e9
```

#### Funcionalidades da Interface

**1. Entrada de Pergunta**
- Text area para perguntas livres
- Botões de exemplo  interativos (sidebar)
- Validação de entrada não-vazia

**2. Processamento**
- Spinner com feedback visual
- Execução assíncrona do agente
- Tratamento de erros com mensagens claras

**3. Exibição de Resultados**
- **Raciocínio**: Passos do agente (expandível)
- **Query SQL**: Código formatado com syntax highlight
- **Resposta**: Texto em linguagem natural
- **Dados**: Tabela interativa + gráfico automático
- **Download**: Exporta para CSV

**4. Estado da Sessão**
```python
st.session_state.agent              # Agente (cache)
st.session_state.current_question   # Pergunta ativa
st.session_state.agent_ready        # Status de inicialização
```

## Fluxo de Dados Completo

```mermaid
sequenceDiagram
    participant U as Usuário
    participant UI as Streamlit UI
    participant SA as SQLAgent
    participant LLM as Groq LLM
    participant DB as DatabaseManager
    participant VIZ as DataVisualizer
    
    U->>UI: Digite pergunta
    UI->>SA: query(question)
    
    rect rgb(230, 242, 255)
        Note over SA: 1. analyze_question
        SA->>DB: get_schema()
        DB-->>SA: Schema completo
    end
    
    rect rgb(255, 243, 224)
        Note over SA: 2. generate_sql
        SA->>LLM: Gere SQL para: "{question}"
        LLM-->>SA: Query SQL
    end
    
    rect rgb(243, 229, 245)
        Note over SA: 3. execute_sql
        SA->>DB: execute_query(sql)
        alt Query OK
            DB-->>SA: DataFrame com dados
        else Query com erro
            DB-->>SA: Mensagem de erro
            Note over SA: 4. handle_error
            SA->>LLM: Corrija SQL (retry)
            LLM-->>SA: Nova query
            SA->>DB: execute_query(nova_sql)
            DB-->>SA: Dados ou novo erro
        end
    end
    
    rect rgb(224, 242, 241)
        Note over SA: 5. format_answer
        SA->>LLM: Formate resposta em PT-BR
        LLM-->>SA: Resposta formatada
    end
    
    SA-->>UI: {answer, data, sql, steps}
    
    UI->>UI: Exibe raciocínio
    UI->>UI: Exibe SQL
    UI->>UI: Exibe resposta
    
    UI->>VIZ: auto_visualize(data)
    VIZ->>VIZ: Detecta tipo de dado
    VIZ-->>UI: Plotly Figure
    
    UI->>U: Mostra gráfico + tabela
```

## Padrões de Design Utilizados

```mermaid
mindmap
  root((Padrões<br/>de Design))
    State Machine
      Estados bem definidos
      Transições claras
      LangGraph
    Strategy Pattern
      Detecta tipo de dado
      Escolhe visualização
      Implementa renderização
    Singleton
      Agente instanciado 1x
      Cache de conexão
      Session state
    Facade
      Interface simples
      Esconde SQLite
      Tratamento centralizado
```

### 1. State Machine (LangGraph)
- **Estados bem definidos**: Cada nó tem responsabilidade única
- **Transições claras**: Decisões determinísticas baseadas em resultados
- **Fluxo recuperável**: Suporta retry com limite de tentativas

### 2. Strategy Pattern (Visualizações)
- **Detecta tipo de dado**: Análise automática de colunas
- **Escolhe estratégia**: Seleciona visualização apropriada
- **Implementa renderização**: Cria gráfico Plotly específico

### 3. Singleton (Session State)
- **Agente instanciado uma vez**: Cache em `st.session_state`
- **Conexão reutilizada**: Evita overhead de inicialização
- **Estado persistente**: Mantém contexto entre interações

### 4. Facade (DatabaseManager)
- **Interface simples**: Métodos de alto nível
- **Esconde detalhes**: Abstrai SQLite e pandas
- **Tratamento centralizado**: Erros capturados e formatados

## Pontos de Extensão

### 1. Adicionar Novos Tipos de Visualização

```python
# Em src/utils/visualizations.py
class DataVisualizer:
    
    @staticmethod
    def create_heatmap(df: pd.DataFrame, x_col: str, y_col: str, value_col: str) -> go.Figure:
        """Cria mapa de calor para dados cruzados."""
        pivot = df.pivot_table(values=value_col, index=y_col, columns=x_col)
        fig = go.Figure(data=go.Heatmap(z=pivot.values, x=pivot.columns, y=pivot.index))
        return fig
    
    def auto_visualize(self, df: pd.DataFrame) -> go.Figure:
        # Adicionar condição
        if self._is_cross_tabular_data(df):
            return self.create_heatmap(df, x_col, y_col, value_col)
```

### 2. Suportar Outros Bancos de Dados

```python
# Criar src/utils/postgres_manager.py
import psycopg2
from src.utils.database import DatabaseManager

class PostgresManager(DatabaseManager):
    """Adaptador para PostgreSQL."""
    
    def __init__(self, connection_string: str):
        self.conn_string = connection_string
    
    def get_connection(self):
        return psycopg2.connect(self.conn_string)
    
    def get_schema(self) -> Dict:
        # Implementar com information_schema
        pass
```

### 3. Adicionar Memória de Conversação

```python
# Em src/agents/sql_agent.py
from langchain.memory import ConversationBufferMemory

class SQLAgent:
    def __init__(self, ...):
        self.memory = ConversationBufferMemory(
            memory_key="chat_history",
            return_messages=True
        )
    
    def query(self, question: str) -> Dict:
        # Incluir histórico no contexto
        history = self.memory.load_memory_variables({})
        
        # ... processamento ...
        
        # Salvar na memória
        self.memory.save_context(
            {"input": question},
            {"output": result["answer"]}
        )
```

### 4. Implementar Agente Multi-Modal

```python
# Criar src/agents/orchestrator.py
from langgraph.graph import StateGraph

class MultiAgentOrchestrator:
    def __init__(self):
        self.sql_agent = SQLAgent(...)
        self.chart_agent = ChartAgent(...)
        self.summary_agent = SummaryAgent(...)
    
    def build_graph(self):
        workflow = StateGraph(OrchestratorState)
        
        workflow.add_node("route", self.route_question)
        workflow.add_node("sql", self.sql_agent.query)
        workflow.add_node("chart", self.chart_agent.recommend)
        workflow.add_node("summary", self.summary_agent.summarize)
        
        # Definir rotas...
        return workflow.compile()
```

## Segurança e Boas Práticas

```mermaid
graph TD
    subgraph "Camadas de Segurança"
        A[Validação de Input]
        B[Sanitização de SQL]
        C[Gestão de API Keys]
        D[Tratamento de Erros]
        E[Rate Limiting<br/>futuro]
        
        A --> B
        B --> C
        C --> D
        D --> E
    end
    
    style A fill:#e8f5e9
    style B fill:#fff3e0
    style C fill:#f3e5f5
    style D fill:#e3f2fd
    style E fill:#ffebee
```

### 1. Validação de SQL
- Apenas SELECT queries são executadas por padrão
- Sem DELETE, DROP, UPDATE sem aprovação explícita
- TODO: Timeout para queries longas (futuro)

### 2. Gestão de API Keys
- Nunca commitar `.env` (incluído em `.gitignore`)
- Usar variáveis de ambiente (`GROQ_API_KEY`)
- Validação antes de uso (`check_setup.py`)

### 3. Tratamento de Erros
- Try-catch em todos os pontos críticos
- Mensagens claras para usuário final
- Logging estruturado (via `reasoning_steps`)

### 4. Performance
- Cache do schema (não muda frequentemente)
- Limite de tentativas (max 3 retries)
- Reuso da conexão LLM (singleton)
- TODO: Conexão pool para múltiplos usuários

## Métricas e Observabilidade (Roadmap)

```mermaid
graph LR
    subgraph "Métricas Futuras"
        M1[Total de Queries]
        M2[Taxa de Sucesso]
        M3[Tempo Médio]
        M4[Taxa de Retry]
        M5[Tokens Usados]
        M6[Custo Estimado]
    end
    
    M1 --> Dashboard
    M2 --> Dashboard
    M3 --> Dashboard
    M4 --> Dashboard
    M5 --> Dashboard
    M6 --> Dashboard
    
    Dashboard[Dashboard Analytics]
    
    style M1 fill:#e3f2fd
    style M2 fill:#e8f5e9
    style M3 fill:#fff3e0
    style M4 fill:#ffebee
    style M5 fill:#f3e5f5
    style M6 fill:#fce4ec
    style Dashboard fill:#fff9c4
```

**Métricas Planejadas:**
```python
metrics = {
    "total_queries": count,           # Total de perguntas processadas
    "success_rate": percentage,       # Taxa de sucesso (query executada)
    "avg_response_time": seconds,     # Tempo médio de resposta
    "retry_rate": percentage,         # Frequência de retries necessários
    "tokens_used": count,             # Tokens consumidos (Groq)
    "estimated_cost": dollars,        # Custo estimado de API
    "popular_questions": list,        # Perguntas mais frequentes
    "error_types": dict              # Tipos de erro mais comuns
}
```

## Conclusão

```mermaid
mindmap
  root((DataDialogue<br/>Arquitetura))
    Modular
      Componentes independentes
      Fácil manutenção
      Testável
    Extensível
      Pontos de extensão claros
      Novos agentes
      Novos bancos
    Robusta
      Tratamento de erros
      Sistema de retry
      Validações
    Transparente
      Raciocínio visível
      SQL auditável
      Passos rastreáveis
    Inteligente
      LLM para decisões
      Auto-correção
      Visualização automática
```

A arquitetura foi projetada para ser:

- **Modular**: Componentes independentes com responsabilidades claras
- **Extensível**: Fácil adicionar funcionalidades sem quebrar código existente
- **Robusta**: Tratamento de erros e mecanismo de retry automático
- **Transparente**: Mostra todo o raciocínio e passos de execução
- **Inteligente**: Usa LLM para decisões complexas e auto-correção

O uso de **LangGraph** permite criar fluxos sofisticados de agentes mantendo o código limpo, testável e fácil de entender. A combinação com **Groq** (modelo llama-3.3-70b-versatile) garante respostas rápidas e precisas.

---

**Para mais detalhes técnicos:**
- [README.md](README.md) - Visão geral e quick start
- [Código-fonte](src/) - Implementação completa
- [Exemplos](EXAMPLES.md) - Casos de uso reais
- [Contribuindo](CONTRIBUTING.md) - Como colaborar

