#  Guia Rápido de Instalação

Este guia irá te ajudar a colocar o Assistente Virtual de Dados funcionando em menos de 5 minutos.

##  Instalação Rápida

### 1. Pré-requisitos
- Python 3.9 ou superior ([Download](https://www.python.org/downloads/))
- Uma chave da API OpenAI ([Criar conta](https://platform.openai.com/signup))

### 2. Comandos de Instalação

Abra o terminal/PowerShell na pasta do projeto e execute:

```bash
# Criar ambiente virtual
python -m venv venv

# Ativar ambiente virtual
# No Windows:
venv\Scripts\activate
# No Linux/Mac:
source venv/bin/activate

# Instalar dependências
pip install -r requirements.txt

# Configurar API Key
copy .env.example .env
# Edite o arquivo .env e adicione sua chave OpenAI
```

### 3. Executar

```bash
streamlit run app.py
```

O navegador abrirá automaticamente em `http://localhost:8501`

##  Obtendo a API Key da OpenAI

1. Acesse: https://platform.openai.com/api-keys
2. Faça login ou crie uma conta
3. Clique em "Create new secret key"
4. Copie a chave (começa com `sk-...`)
5. Cole no arquivo `.env`:
   ```
   OPENAI_API_KEY=sk-sua-chave-aqui
   ```

** IMPORTANTE:** 
- A API da OpenAI é paga (preços muito baixos para teste)
- Você pode usar o crédito gratuito para novos usuários
- Modelo padrão: `gpt-4o-mini` (mais barato)

##  Testar sem Interface

Para testar o agente via linha de comando:

```bash
python test_agent.py
```

##  Problemas Comuns

### "No module named 'streamlit'"
**Solução:** Ativar o ambiente virtual antes
```bash
venv\Scripts\activate  # Windows
pip install -r requirements.txt
```

### "API key not found"
**Solução:** Verificar arquivo .env
- Deve estar na raiz do projeto
- Deve ter o formato: `OPENAI_API_KEY=sk-...`
- Sem espaços antes ou depois do =

### "Unable to open database"
**Solução:** Executar da pasta correta
```bash
cd Desafio1
streamlit run app.py
```

##  Próximos Passos

1.  Abra a aplicação
2.  Experimente os exemplos da sidebar
3.  Faça suas próprias perguntas
4.  Veja o código e customize!

##  Custos Estimados

Usando `gpt-4o-mini`:
- ~$0.15 por 1000 perguntas
- Praticamente gratuito para testes
- Crédito inicial da OpenAI: $5

** Pronto! Comece a fazer perguntas aos seus dados!**

