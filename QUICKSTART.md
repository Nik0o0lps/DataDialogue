#  Guia de Início Rápido - 5 Minutos

##  3 Passos para Começar

### 1. Instalar Dependências (2 min)

```bash
# Criar ambiente virtual
python -m venv venv

# Ativar (Windows)
venv\Scripts\activate

# Ativar (Linux/Mac)
source venv/bin/activate

# Instalar
pip install -r requirements.txt
```

### 2. Configurar API Key (1 min)

```bash
# Copiar exemplo
copy .env.example .env    # Windows
cp .env.example .env      # Linux/Mac

# Editar .env e adicionar:
OPENAI_API_KEY=sk-sua-chave-aqui
```

Obtenha sua chave em: https://platform.openai.com/api-keys

### 3. Executar (1 min)

```bash
streamlit run app.py
```

Ou use os scripts:
- **Windows:** Duplo clique em `start.bat`
- **Linux/Mac:** `./start.sh`

---

##  Primeiro Uso

1. Aplicação abre no navegador
2. Veja exemplos na sidebar →
3. Clique em um exemplo ou digite sua pergunta
4. Clique em " Buscar"
5. Veja o raciocínio, SQL, resposta e gráfico!

---

##  Perguntas de Exemplo

Copie e cole:

```
Quantos clientes temos no total?
```

```
Liste os 5 estados com maior número de clientes
```

```
Qual a tendência de vendas no último ano?
```

---

##  Problemas?

Execute o diagnóstico:
```bash
python check_setup.py
```

---

##  Próximos Passos

-  Leia [README.md](README.md) para detalhes
-  Veja [EXAMPLES.md](EXAMPLES.md) para mais consultas
-  Explore [ARCHITECTURE.md](ARCHITECTURE.md) para entender o código

---

** Pronto! Comece a fazer perguntas aos seus dados!**

*Tempo total: ~5 minutos*

