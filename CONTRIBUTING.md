#  Guia de Contribuição

Obrigado por considerar contribuir com o Assistente Virtual de Dados! Este documento fornece diretrizes para contribuições.

##  Como Contribuir

### 1. Reportar Bugs

Se encontrou um bug, abra uma issue incluindo:
- Descrição clara do problema
- Passos para reproduzir
- Comportamento esperado vs. atual
- Logs de erro (se houver)
- Ambiente (OS, Python version, etc.)

### 2. Sugerir Melhorias

Para sugestões de features:
- Descreva o problema que resolve
- Explique a solução proposta
- Considere alternativas
- Impacto no sistema existente

### 3. Contribuir com Código

#### Setup do Ambiente de Desenvolvimento

```bash
# Fork o repositório
# Clone seu fork
git clone https://github.com/seu-usuario/desafio-franq.git
cd desafio-franq/Desafio1

# Crie um branch para sua feature
git checkout -b feature/minha-feature

# Instale dependências de dev
pip install -r requirements.txt
pip install pytest black flake8
```

#### Padrões de Código

**Python:**
- PEP 8 para estilo
- Type hints quando possível
- Docstrings para funções públicas
- Máximo 100 caracteres por linha

**Exemplo:**
```python
def processar_query(pergunta: str, contexto: Dict[str, Any]) -> QueryResult:
    """
    Processa uma pergunta e retorna resultado estruturado.
    
    Args:
        pergunta: Pergunta em linguagem natural
        contexto: Contexto adicional (schema, etc.)
        
    Returns:
        QueryResult com dados e metadados
        
    Raises:
        ValueError: Se pergunta for inválida
    """
    # Implementação
    pass
```

#### Testes

Adicione testes para novas funcionalidades:

```python
# tests/test_sql_agent.py
def test_query_simples():
    agent = SQLAgent(db_path="test.db")
    resultado = agent.query("Quantos clientes?")
    
    assert resultado['success'] is True
    assert resultado['data'] is not None
```

#### Commit Messages

Use mensagens claras e descritivas:

```bash
#  Ruim
git commit -m "fix"

#  Bom
git commit -m "fix: corrigir erro de parsing em queries com JOIN"
git commit -m "feat: adicionar suporte para gráficos de área"
git commit -m "docs: atualizar README com novos exemplos"
```

**Convenção:**
- `feat:` nova funcionalidade
- `fix:` correção de bug
- `docs:` documentação
- `style:` formatação
- `refactor:` refatoração
- `test:` testes
- `chore:` tarefas gerais

### 4. Pull Request

Antes de submeter:

1.  Código segue os padrões
2.  Testes passam
3.  Documentação atualizada
4.  Sem conflitos com main

**Template de PR:**

```markdown
## Descrição
[Descrição clara das mudanças]

## Tipo de Mudança
- [ ] Bug fix
- [ ] Nova feature
- [ ] Breaking change
- [ ] Documentação

## Como Testar
1. [Passo 1]
2. [Passo 2]

## Checklist
- [ ] Código segue style guide
- [ ] Testes adicionados
- [ ] Documentação atualizada
- [ ] Sem warnings
```

##  Áreas para Contribuir

### Features Desejadas

#### 1. Memória de Conversação
**Dificuldade:** Média
**Objetivo:** Manter contexto entre perguntas

```python
# Exemplo
"Quantos clientes temos?" 
→ "120 clientes"

"E quantos compraram via app?"  # ← referenciar contexto anterior
→ "45 clientes compraram via app"
```

#### 2. Suporte a PostgreSQL/MySQL
**Dificuldade:** Média
**Objetivo:** Não limitar a SQLite

#### 3. Cache Inteligente
**Dificuldade:** Alta
**Objetivo:** Guardar queries similares

#### 4. Exportação de Relatórios
**Dificuldade:** Baixa
**Objetivo:** Gerar PDF/Excel com análises

#### 5. Autenticação de Usuários
**Dificuldade:** Alta
**Objetivo:** Multi-usuário com histórico separado

#### 6. Testes Automatizados
**Dificuldade:** Média
**Objetivo:** Cobertura de 80%+

### Melhorias de UX

- [ ] Dark mode
- [ ] Histórico de queries
- [ ] Favoritar perguntas
- [ ] Compartilhar análises
- [ ] Customizar temas
- [ ] Atalhos de teclado

### Performance

- [ ] Otimizar queries geradas
- [ ] Caching de schema
- [ ] Paralelização
- [ ] Lazy loading de dados

##  Recursos

- [LangChain Docs](https://python.langchain.com/docs/get_started/introduction)
- [LangGraph Tutorial](https://langchain-ai.github.io/langgraph/)
- [Streamlit Docs](https://docs.streamlit.io/)
- [Plotly Examples](https://plotly.com/python/)

##  Comunicação

- Issues: Para bugs e features
- Discussions: Para perguntas e ideias
- Pull Requests: Para contribuições de código

##  Código de Conduta

- Seja respeitoso e inclusivo
- Aceite críticas construtivas
- Foque no que é melhor para a comunidade
- Mostre empatia com outros membros

##  Reconhecimento

Todos os contribuidores serão reconhecidos no README!

---

**Obrigado por contribuir! **

