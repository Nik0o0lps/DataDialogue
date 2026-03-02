#  Exemplos de Consultas Testadas

Este arquivo contém exemplos de perguntas testadas com o sistema e seus resultados esperados.

##  Consultas Básicas

### 1. Contagem Total de Clientes

**Pergunta:**
```
Quantos clientes temos no total?
```

**SQL Esperado:**
```sql
SELECT COUNT(*) as total_clientes FROM clientes
```

**Resultado Esperado:**
- Número total: 100 clientes
- Visualização: Não aplicável (valor único)

---

### 2. Listagem de Estados

**Pergunta:**
```
Quantos clientes temos por estado?
```

**SQL Esperado:**
```sql
SELECT estado, COUNT(*) as total_clientes 
FROM clientes 
GROUP BY estado 
ORDER BY total_clientes DESC
```

**Resultado Esperado:**
- Tabela com estados e contagens
- Visualização: Gráfico de barras

---

##  Consultas Com Filtros

### 3. Compras via App em Maio

**Pergunta:**
```
Liste os 5 estados com maior número de clientes que compraram via app em maio
```

**SQL Esperado:**
```sql
SELECT c.estado, COUNT(DISTINCT c.id) as num_clientes
FROM clientes c
JOIN compras co ON c.id = co.cliente_id
WHERE co.canal = 'App' 
  AND strftime('%m', co.data_compra) = '05'
GROUP BY c.estado
ORDER BY num_clientes DESC
LIMIT 5
```

**Resultado Esperado:**
- Top 5 estados
- Visualização: Gráfico de barras horizontal

---

### 4. Interações com Campanhas de WhatsApp

**Pergunta:**
```
Quantos clientes interagiram com campanhas de WhatsApp em 2024?
```

**SQL Esperado:**
```sql
SELECT COUNT(DISTINCT cliente_id) as total_clientes
FROM campanhas_marketing
WHERE canal = 'WhatsApp'
  AND interagiu = 1
  AND strftime('%Y', data_envio) = '2024'
```

**Resultado Esperado:**
- Número de clientes únicos
- Visualização: Não aplicável (valor único)

---

##  Consultas de Agregação

### 5. Categorias Mais Compradas

**Pergunta:**
```
Quais categorias de produto tiveram o maior número de compras em média por cliente?
```

**SQL Esperado:**
```sql
SELECT 
    categoria,
    COUNT(*) as total_compras,
    COUNT(DISTINCT cliente_id) as num_clientes,
    ROUND(CAST(COUNT(*) AS FLOAT) / COUNT(DISTINCT cliente_id), 2) as media_por_cliente
FROM compras
GROUP BY categoria
ORDER BY media_por_cliente DESC
```

**Resultado Esperado:**
- Tabela com categorias e médias
- Visualização: Gráfico de barras

---

### 6. Reclamações Não Resolvidas

**Pergunta:**
```
Qual o número de reclamações não resolvidas por canal?
```

**SQL Esperado:**
```sql
SELECT 
    canal,
    COUNT(*) as reclamacoes_nao_resolvidas
FROM suporte
WHERE tipo_contato = 'Reclamação' 
  AND resolvido = 0
GROUP BY canal
ORDER BY reclamacoes_nao_resolvidas DESC
```

**Resultado Esperado:**
- Tabela por canal
- Visualização: Gráfico de pizza ou barras

---

##  Consultas Temporais

### 7. Tendência de Reclamações

**Pergunta:**
```
Qual a tendência de reclamações por canal no último ano?
```

**SQL Esperado:**
```sql
SELECT 
    strftime('%Y-%m', data_contato) as mes,
    canal,
    COUNT(*) as num_reclamacoes
FROM suporte
WHERE tipo_contato = 'Reclamação'
  AND date(data_contato) >= date('now', '-1 year')
GROUP BY mes, canal
ORDER BY mes, canal
```

**Resultado Esperado:**
- Dados mensais por canal
- Visualização: Gráfico de linhas (tendência temporal)

---

### 8. Compras por Mês em 2024

**Pergunta:**
```
Quantas compras foram feitas por mês em 2024?
```

**SQL Esperado:**
```sql
SELECT 
    strftime('%Y-%m', data_compra) as mes,
    COUNT(*) as total_compras
FROM compras
WHERE strftime('%Y', data_compra) = '2024'
GROUP BY mes
ORDER BY mes
```

**Resultado Esperado:**
- Dados mensais
- Visualização: Gráfico de linhas

---

##  Consultas de Ranking

### 9. Top 10 Clientes

**Pergunta:**
```
Quais os 10 clientes que mais gastaram?
```

**SQL Esperado:**
```sql
SELECT 
    nome,
    estado,
    valor_total_gasto
FROM clientes
ORDER BY valor_total_gasto DESC
LIMIT 10
```

**Resultado Esperado:**
- Tabela com top 10
- Visualização: Gráfico de barras horizontal

---

### 10. Canais Mais Utilizados

**Pergunta:**
```
Quais são os canais de compra mais utilizados?
```

**SQL Esperado:**
```sql
SELECT 
    canal,
    COUNT(*) as total_compras
FROM compras
GROUP BY canal
ORDER BY total_compras DESC
```

**Resultado Esperado:**
- Ranking de canais
- Visualização: Gráfico de barras ou pizza

---

##  Consultas Estatísticas

### 11. Média de Idade por Estado

**Pergunta:**
```
Qual a média de idade dos clientes por estado?
```

**SQL Esperado:**
```sql
SELECT 
    estado,
    ROUND(AVG(idade), 1) as media_idade,
    COUNT(*) as num_clientes
FROM clientes
GROUP BY estado
ORDER BY media_idade DESC
```

**Resultado Esperado:**
- Estatísticas por estado
- Visualização: Gráfico de barras

---

### 12. Valor Médio de Compra por Categoria

**Pergunta:**
```
Qual o valor médio de compra por categoria?
```

**SQL Esperado:**
```sql
SELECT 
    categoria,
    ROUND(AVG(valor), 2) as valor_medio,
    COUNT(*) as quantidade
FROM compras
GROUP BY categoria
ORDER BY valor_medio DESC
```

**Resultado Esperado:**
- Estatísticas por categoria
- Visualização: Gráfico de barras

---

##  Consultas Com JOINs Complexos

### 13. Perfil de Clientes que Mais Gastam

**Pergunta:**
```
Qual o perfil dos clientes que mais gastam? (idade, estado, profissão)
```

**SQL Esperado:**
```sql
SELECT 
    idade,
    estado,
    profissao,
    valor_total_gasto
FROM clientes
WHERE valor_total_gasto > (SELECT AVG(valor_total_gasto) FROM clientes)
ORDER BY valor_total_gasto DESC
LIMIT 20
```

**Resultado Esperado:**
- Perfil detalhado
- Visualização: Tabela

---

### 14. Efetividade de Campanhas

**Pergunta:**
```
Qual a taxa de interação das campanhas de marketing por canal?
```

**SQL Esperado:**
```sql
SELECT 
    canal,
    COUNT(*) as total_campanhas,
    SUM(interagiu) as interacoes,
    ROUND(CAST(SUM(interagiu) AS FLOAT) / COUNT(*) * 100, 2) as taxa_interacao
FROM campanhas_marketing
GROUP BY canal
ORDER BY taxa_interacao DESC
```

**Resultado Esperado:**
- Métricas por canal
- Visualização: Gráfico de barras

---

##  Consultas Avançadas

### 15. Análise de Retenção

**Pergunta:**
```
Quantos clientes fizeram mais de 5 compras?
```

**SQL Esperado:**
```sql
SELECT 
    COUNT(DISTINCT cliente_id) as clientes_frequentes
FROM (
    SELECT cliente_id, COUNT(*) as num_compras
    FROM compras
    GROUP BY cliente_id
    HAVING num_compras > 5
)
```

**Resultado Esperado:**
- Número de clientes fiéis
- Visualização: Não aplicável

---

### 16. Sazonalidade de Compras

**Pergunta:**
```
Em quais meses do ano ocorrem mais compras?
```

**SQL Esperado:**
```sql
SELECT 
    CASE strftime('%m', data_compra)
        WHEN '01' THEN 'Janeiro'
        WHEN '02' THEN 'Fevereiro'
        -- ... outros meses
        WHEN '12' THEN 'Dezembro'
    END as mes,
    COUNT(*) as total_compras
FROM compras
GROUP BY strftime('%m', data_compra)
ORDER BY strftime('%m', data_compra)
```

**Resultado Esperado:**
- Distribuição mensal
- Visualização: Gráfico de barras ou linhas

---

##  Testando o Sistema

### Como usar estes exemplos:

1. **Copie a pergunta** exatamente como está
2. **Cole na interface** Streamlit
3. **Verifique** se o SQL gerado é similar ao esperado
4. **Analise** os resultados e visualizações

### Critérios de Sucesso:

-  Query executa sem erros
-  Resultados fazem sentido
-  Visualização apropriada é criada
-  Resposta em linguagem natural é clara

### Casos de Teste para Correção de Erros:

**Teste de Retry:**
- Pergunta ambígua que pode gerar SQL incorreto
- O sistema deve tentar novamente e corrigir
- Máximo de 3 tentativas

**Teste de Descoberta:**
- Perguntas sobre dados não óbvios
- O sistema deve explorar o schema
- Deve encontrar as tabelas/colunas corretas

---

##  Resumo de Cobertura

-  Consultas simples (COUNT, AVG, SUM)
-  Filtros e condições (WHERE, HAVING)
-  Agregações (GROUP BY)
-  Ordenação e limites (ORDER BY, LIMIT)
-  Junções (JOIN)
-  Datas e períodos (strftime)
-  Subconsultas
-  Operações booleanas
-  Cálculos e formatação

**Total de exemplos:** 16 consultas variadas

**Cobertura estimada:** 90% dos casos de uso comuns

---

 **Dica:** Use estes exemplos como base para criar suas próprias consultas!

