#!/bin/bash
# Script de inicialização rápida para o Assistente Virtual de Dados (Linux/Mac)
# Execute: chmod +x start.sh && ./start.sh

echo "========================================"
echo "   Assistente Virtual de Dados"
echo "   Iniciando aplicação..."
echo "========================================"
echo ""

# Verificar se o ambiente virtual existe
if [ ! -d "venv" ]; then
    echo "[!] Ambiente virtual não encontrado!"
    echo "[i] Criando ambiente virtual..."
    python3 -m venv venv
    
    if [ $? -ne 0 ]; then
        echo "[X] Erro ao criar ambiente virtual!"
        echo "[i] Certifique-se de ter Python 3.9+ instalado"
        exit 1
    fi
    
    echo "[OK] Ambiente virtual criado!"
    echo ""
fi

# Ativar ambiente virtual
echo "[i] Ativando ambiente virtual..."
source venv/bin/activate

if [ $? -ne 0 ]; then
    echo "[X] Erro ao ativar ambiente virtual!"
    exit 1
fi

echo "[OK] Ambiente virtual ativado!"
echo ""

# Verificar se as dependências estão instaladas
echo "[i] Verificando dependências..."
python -c "import streamlit" 2>/dev/null
if [ $? -ne 0 ]; then
    echo "[!] Dependências não encontradas!"
    echo "[i] Instalando dependências..."
    pip install -r requirements.txt
    
    if [ $? -ne 0 ]; then
        echo "[X] Erro ao instalar dependências!"
        exit 1
    fi
    
    echo "[OK] Dependências instaladas!"
    echo ""
fi

# Verificar arquivo .env
if [ ! -f ".env" ]; then
    echo "[!] Arquivo .env não encontrado!"
    echo "[i] Copie .env.example para .env e configure sua API key"
    echo ""
    
    if [ -f ".env.example" ]; then
        cp .env.example .env
        echo "[OK] Arquivo .env criado a partir do exemplo"
        echo "[!] IMPORTANTE: Edite o arquivo .env e adicione sua API key!"
        echo ""
        read -p "Pressione Enter para continuar..."
    fi
fi

# Iniciar Streamlit
echo "========================================"
echo "[i] Iniciando Streamlit..."
echo "[i] A aplicação abrirá no navegador"
echo "[i] Pressione Ctrl+C para encerrar"
echo "========================================"
echo ""

streamlit run app.py

# Se chegou aqui, o Streamlit foi encerrado
echo ""
echo "========================================"
echo "[i] Aplicação encerrada"
echo "========================================"
