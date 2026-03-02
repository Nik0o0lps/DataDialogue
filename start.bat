@echo off
REM Script de inicializacao rapida para o Assistente Virtual de Dados
REM Execute este arquivo para iniciar a aplicacao

echo ========================================
echo    Assistente Virtual de Dados
echo    Iniciando aplicacao...
echo ========================================
echo.

REM Verificar se o ambiente virtual existe
if not exist "venv\" (
    echo [!] Ambiente virtual nao encontrado!
    echo [i] Criando ambiente virtual...
    python -m venv venv
    
    if errorlevel 1 (
        echo [X] Erro ao criar ambiente virtual!
        echo [i] Certifique-se de ter Python 3.9+ instalado
        pause
        exit /b 1
    )
    
    echo [OK] Ambiente virtual criado!
    echo.
)

REM Ativar ambiente virtual
echo [i] Ativando ambiente virtual...
call venv\Scripts\activate.bat

if errorlevel 1 (
    echo [X] Erro ao ativar ambiente virtual!
    pause
    exit /b 1
)

echo [OK] Ambiente virtual ativado!
echo.

REM Verificar se as dependencias estao instaladas
echo [i] Verificando dependencias...
python -c "import streamlit" 2>nul
if errorlevel 1 (
    echo [!] Dependencias nao encontradas!
    echo [i] Instalando dependencias...
    pip install -r requirements.txt
    
    if errorlevel 1 (
        echo [X] Erro ao instalar dependencias!
        pause
        exit /b 1
    )
    
    echo [OK] Dependencias instaladas!
    echo.
)

REM Verificar arquivo .env
if not exist ".env" (
    echo [!] Arquivo .env nao encontrado!
    echo [i] Copie .env.example para .env e configure sua API key
    echo.
    
    if exist ".env.example" (
        copy .env.example .env >nul
        echo [OK] Arquivo .env criado a partir do exemplo
        echo [!] IMPORTANTE: Edite o arquivo .env e adicione sua API key!
        echo.
        pause
    )
)

REM Iniciar Streamlit
echo ========================================
echo [i] Iniciando Streamlit...
echo [i] A aplicacao abrira no navegador
echo [i] Pressione Ctrl+C para encerrar
echo ========================================
echo.

streamlit run app.py

REM Se chegou aqui, o Streamlit foi encerrado
echo.
echo ========================================
echo [i] Aplicacao encerrada
echo ========================================
pause
