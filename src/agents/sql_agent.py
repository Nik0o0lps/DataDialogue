"""
Agente SQL inteligente usando LangGraph.
Este agente pode analisar perguntas, gerar SQL, executar queries e corrigir erros automaticamente.
"""
import os
from typing import TypedDict, Annotated, Sequence, Dict, Any, List
from langchain_core.messages import BaseMessage, HumanMessage, AIMessage, SystemMessage
try:
    from langchain_groq import ChatGroq
    USE_GROQ = True
except ImportError:
    from langchain_openai import ChatOpenAI
    USE_GROQ = False
from langgraph.graph import StateGraph, END
import operator
import sys
from pathlib import Path

# Adicionar o diretório src ao path
sys.path.append(str(Path(__file__).parent.parent.parent))

from src.utils.database import DatabaseManager


class AgentState(TypedDict):
    """Estado do agente."""
    messages: Annotated[Sequence[BaseMessage], operator.add]
    question: str
    schema: str
    sql_query: str
    query_result: Any
    error_message: str
    attempt_count: int
    final_answer: str
    reasoning_steps: List[str]


class SQLAgent:
    """Agente inteligente para consultas SQL usando LangGraph."""
    
    def __init__(self, db_path: str = "anexo_desafio_1.db", 
                 model_name: str = None,
                 temperature: float = 0):
        """
        Inicializa o agente SQL.
        
        Args:
            db_path: Caminho para o banco de dados SQLite
            model_name: Nome do modelo (Groq ou OpenAI)
            temperature: Temperatura para geração (0 = determinístico)
        """
        self.db_manager = DatabaseManager(db_path)
        
        # Detectar qual API usar
        if USE_GROQ and os.getenv("GROQ_API_KEY"):
            # Usar Groq (mais rápido e gratuito!)
            model_name = model_name or os.getenv("GROQ_MODEL", "llama-3.3-70b-versatile")
            temperature = temperature or float(os.getenv("GROQ_TEMPERATURE", "0"))
            self.llm = ChatGroq(
                model=model_name,
                temperature=temperature,
                groq_api_key=os.getenv("GROQ_API_KEY")
            )
        else:
            # Fallback para OpenAI
            model_name = model_name or os.getenv("LANGCHAIN_MODEL", "gpt-4o-mini")
            self.llm = ChatOpenAI(model=model_name, temperature=temperature)
        
        self.max_attempts = 3
        
        # Construir o grafo do agente
        self.graph = self._build_graph()
    
    def _build_graph(self) -> StateGraph:
        """Constrói o grafo de estados do agente usando LangGraph."""
        workflow = StateGraph(AgentState)
        
        # Adicionar nós
        workflow.add_node("analyze_question", self._analyze_question)
        workflow.add_node("generate_sql", self._generate_sql)
        workflow.add_node("execute_sql", self._execute_sql)
        workflow.add_node("handle_error", self._handle_error)
        workflow.add_node("format_answer", self._format_answer)
        
        # Definir edges
        workflow.set_entry_point("analyze_question")
        workflow.add_edge("analyze_question", "generate_sql")
        workflow.add_edge("generate_sql", "execute_sql")
        
        # Condicional: sucesso -> format_answer, erro -> handle_error
        workflow.add_conditional_edges(
            "execute_sql",
            self._should_retry,
            {
                "success": "format_answer",
                "retry": "handle_error",
                "end": END
            }
        )
        
        workflow.add_edge("handle_error", "generate_sql")
        workflow.add_edge("format_answer", END)
        
        return workflow.compile()
    
    def _analyze_question(self, state: AgentState) -> AgentState:
        """Analisa a pergunta e obtém o schema do banco."""
        reasoning_steps = state.get("reasoning_steps", [])
        reasoning_steps.append("Analisando pergunta e obtendo schema do banco de dados...")
        
        schema = self.db_manager.get_schema_text()
        
        # Adicionar contexto sobre o schema
        system_message = f"""Você é um analista de dados especializado em SQL.
Sua tarefa é entender a pergunta do usuário e preparar para gerar uma query SQL apropriada.

Schema do banco de dados:
{schema}

Informações importantes:
- O banco usa SQLite
- Datas estão no formato YYYY-MM-DD
- BOOLEAN é representado como 0 (falso) ou 1 (verdadeiro)
- Para joins, use as colunas cliente_id como chave estrangeira
"""
        
        messages = [
            SystemMessage(content=system_message),
            HumanMessage(content=state["question"])
        ]
        
        return {
            **state,
            "schema": schema,
            "messages": messages,
            "reasoning_steps": reasoning_steps,
            "attempt_count": 0
        }
    
    def _generate_sql(self, state: AgentState) -> AgentState:
        """Gera a query SQL baseada na pergunta."""
        reasoning_steps = state.get("reasoning_steps", [])
        attempt = state.get("attempt_count", 0)
        
        if attempt == 0:
            reasoning_steps.append("Gerando query SQL...")
        else:
            reasoning_steps.append(f"Tentativa {attempt + 1}: Corrigindo query SQL...")
        
        # Se houver erro anterior, adicionar ao contexto
        error_context = ""
        if state.get("error_message"):
            error_context = f"""

ERRO ANTERIOR:
{state['error_message']}

QUERY QUE FALHOU:
{state.get('sql_query', 'N/A')}

Por favor, corrija o erro e gere uma nova query.
"""
        
        prompt = f"""Com base na pergunta do usuário e no schema fornecido, gere uma query SQL válida.

Pergunta: {state['question']}

{error_context}

REGRAS IMPORTANTES:
1. Retorne APENAS o código SQL, sem explicações
2. Use sintaxe SQLite
3. Para datas, use o formato YYYY-MM-DD
4. Para contar registros com condições booleanas, use WHERE condicao = 1 (verdadeiro) ou = 0 (falso)
5. Para extrair mês/ano de datas, use strftime('%Y-%m', data_coluna)
6. Use JOINs quando precisar combinar tabelas
7. Se a pergunta pedir "top N" ou "maiores", use ORDER BY e LIMIT
8. Para agregações por período, use GROUP BY com strftime
9. Seja preciso com os nomes das colunas e tabelas

PLURAL vs SINGULAR - IMPORTANTE:
10. Se a pergunta usar PLURAL (ex: "categorias", "estados", "clientes", "produtos"), 
    liste PELO MENOS 5 itens (LIMIT 5 ou mais), mesmo que a pergunta use "o maior" ou "qual teve".
    - "Quais CATEGORIAS tiveram..." → LIMIT 5
    - "Quais ESTADOS com maior..." → LIMIT 5
    - "Qual CATEGORIA teve..." → LIMIT 1
11. Se a pergunta não especificar número e usar plural, use LIMIT 5 como padrão
12. Se a pergunta especificar um número ("top 3", "5 maiores"), use esse número

ALIASES E NOMENCLATURA:
13. SEMPRE use aliases (AS) para funções agregadas e colunas calculadas com nomes DESCRITIVOS em português:
    - Bom: COUNT(*) AS total_clientes, AVG(valor) AS media_valor, SUM(valor) AS total_vendas
    - Ruim: COUNT(*), AVG(valor), SUM(valor)
14. Use nomes de aliases que façam sentido para o usuário final:
    - total, quantidade, media, soma, minimo, maximo, etc.
    - Evite nomes técnicos como num_clientes, val_total
15. Para queries que retornam apenas um valor agregado, use um alias descritivo como 'total' ou 'quantidade'

ATENÇÃO ESPECIAL - DATAS E VALORES:
16. IMPORTANTE: Quando o usuário mencionar um mês sem especificar o ano (ex: "em maio"), 
    você deve usar o ano mais recente disponível nos dados. Para isso, considere que 
    os dados podem estar em diferentes anos. Se não houver especificação de ano,
    considere todos os anos ou use uma subconsulta para encontrar o ano mais recente.
17. CASE-SENSITIVE: Valores de texto são case-sensitive. Por exemplo:
    - 'App' é diferente de 'app' ou 'APP'
    - 'Site' é diferente de 'site'
    - Sempre use a capitalização exata conforme o schema
18. Antes de filtrar por valores categóricos (como canal, estado, categoria), verifique
    os valores exatos no schema fornecido.

ORDENAÇÃO E SELEÇÃO DE COLUNAS:
19. SEMPRE adicione ORDER BY para resultados organizados e previsíveis:
    - Para análises temporais/tendências: ORDER BY periodo ASC, metrica DESC
    - Para rankings (top N, maiores, etc): ORDER BY metrica DESC
    - Para listagens simples: ORDER BY campo_principal ASC
20. SELEÇÃO INTELIGENTE DE COLUNAS - quando a pergunta for sobre análise de UM atributo específico:
    - Perguntas como "reclamações POR CANAL", "vendas POR CATEGORIA", "clientes POR ESTADO"
    - Selecione APENAS: o atributo principal (canal, categoria, estado) + a métrica (total, média, soma)
    - NÃO inclua períodos/datas como colunas no SELECT, use apenas no GROUP BY e ORDER BY
    - Exemplo: Para "tendência por canal no último ano":
      * BOM: SELECT canal, COUNT(*) AS total FROM ... GROUP BY periodo, canal ORDER BY periodo, total DESC
      * RUIM: SELECT periodo, canal, COUNT(*) AS total FROM ... (período não deve aparecer no resultado final)
21. Se a pergunta pedir explicitamente "por período" ou "ao longo do tempo", aí sim inclua o período no SELECT

Query SQL:"""
        
        messages = state["messages"] + [HumanMessage(content=prompt)]
        response = self.llm.invoke(messages)
        
        # Extrair apenas o SQL da resposta
        sql_query = response.content.strip()
        
        # Remover markdown se presente
        if "```sql" in sql_query:
            sql_query = sql_query.split("```sql")[1].split("```")[0].strip()
        elif "```" in sql_query:
            sql_query = sql_query.split("```")[1].split("```")[0].strip()
        
        reasoning_steps.append(f"Query gerada: {sql_query}")
        
        return {
            **state,
            "sql_query": sql_query,
            "messages": messages + [response],
            "reasoning_steps": reasoning_steps,
            "attempt_count": attempt + 1
        }
    
    def _execute_sql(self, state: AgentState) -> AgentState:
        """Executa a query SQL."""
        reasoning_steps = state.get("reasoning_steps", [])
        reasoning_steps.append("Executando query no banco de dados...")
        
        success, result = self.db_manager.execute_query(state["sql_query"])
        
        if success:
            reasoning_steps.append(f"Query executada com sucesso! {len(result) if hasattr(result, '__len__') else 0} registros retornados.")
            return {
                **state,
                "query_result": result,
                "error_message": "",
                "reasoning_steps": reasoning_steps
            }
        else:
            reasoning_steps.append(f"Erro na execução: {result}")
            return {
                **state,
                "error_message": result,
                "reasoning_steps": reasoning_steps
            }
    
    def _should_retry(self, state: AgentState) -> str:
        """Decide se deve tentar novamente após um erro."""
        if state.get("error_message"):
            if state["attempt_count"] < self.max_attempts:
                return "retry"
            else:
                return "end"
        return "success"
    
    def _handle_error(self, state: AgentState) -> AgentState:
        """Lida com erros e prepara para nova tentativa."""
        reasoning_steps = state.get("reasoning_steps", [])
        reasoning_steps.append("Analisando erro e preparando correção...")
        
        return {
            **state,
            "reasoning_steps": reasoning_steps
        }
    
    def _format_answer(self, state: AgentState) -> AgentState:
        """Formata a resposta final."""
        reasoning_steps = state.get("reasoning_steps", [])
        reasoning_steps.append("Formatando resposta final...")
        
        # Gerar resposta em linguagem natural
        prompt = f"""Com base nos resultados da query SQL, forneça uma resposta clara e concisa em português.

Pergunta original: {state['question']}

Query executada: {state['sql_query']}

Resultados:
{state['query_result'].to_string() if hasattr(state['query_result'], 'to_string') else state['query_result']}

INSTRUÇÕES IMPORTANTES:
1. Forneça uma resposta direta e informativa, mencionando os dados mais relevantes.
2. Se a pergunta pedir "top N", "liste N", "os N maiores/menores", etc., você DEVE listar 
   TODOS os N itens INDIVIDUALMENTE, mesmo que alguns tenham o mesmo valor.
3. Use uma lista numerada clara (1., 2., 3., etc.) quando houver múltiplos itens para listar.
4. Não agrupe itens com valores iguais - liste cada um separadamente.
5. Se houver empate nos valores, mencione isso, mas ainda assim liste todos os itens.

EXEMPLO CORRETO:
"Os 5 estados com maior número de clientes que compraram via app em maio são:
1. São Paulo - 6 clientes
2. Santa Catarina - 3 clientes
3. Minas Gerais - 3 clientes
4. Paraná - 2 clientes
5. Espírito Santo - 2 clientes"

Resposta:
"""
        
        response = self.llm.invoke([HumanMessage(content=prompt)])
        
        reasoning_steps.append("Resposta pronta!")
        
        return {
            **state,
            "final_answer": response.content,
            "reasoning_steps": reasoning_steps
        }
    
    def query(self, question: str) -> Dict[str, Any]:
        """
        Processa uma pergunta e retorna os resultados.
        
        Args:
            question: Pergunta em linguagem natural
            
        Returns:
            Dicionário com resposta, dados, query SQL e passos de raciocínio
        """
        initial_state = {
            "messages": [],
            "question": question,
            "schema": "",
            "sql_query": "",
            "query_result": None,
            "error_message": "",
            "attempt_count": 0,
            "final_answer": "",
            "reasoning_steps": []
        }
        
        # Executar o grafo
        final_state = self.graph.invoke(initial_state)
        
        return {
            "answer": final_state.get("final_answer", "Não foi possível gerar uma resposta."),
            "data": final_state.get("query_result"),
            "sql_query": final_state.get("sql_query", ""),
            "reasoning_steps": final_state.get("reasoning_steps", []),
            "success": bool(final_state.get("query_result") is not None)
        }
