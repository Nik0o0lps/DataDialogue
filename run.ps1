# Script PowerShell para gerenciar o projeto
# Uso: .\run.ps1 <comando>

param(
    [Parameter(Position=0)]
    [string]$Command = "help"
)

function Show-Help {
    Write-Host "==================================" -ForegroundColor Cyan
    Write-Host "  Comandos Disponíveis" -ForegroundColor Cyan
    Write-Host "==================================" -ForegroundColor Cyan
    Write-Host ""
    Write-Host "Instalação e Setup:" -ForegroundColor Yellow
    Write-Host "  install       - Instalar dependências"
    Write-Host "  setup         - Setup completo (venv + install)"
    Write-Host ""
    Write-Host "Testes:" -ForegroundColor Yellow
    Write-Host "  test          - Executar testes"
    Write-Host "  test-cov      - Testes com cobertura"
    Write-Host "  lint          - Executar pylint"
    Write-Host ""
    Write-Host "Execução:" -ForegroundColor Yellow
    Write-Host "  run           - Iniciar aplicação"
    Write-Host "  check         - Verificar setup"
    Write-Host ""
    Write-Host "Docker:" -ForegroundColor Yellow
    Write-Host "  docker-build  - Build da imagem"
    Write-Host "  docker-run    - Executar container"
    Write-Host "  docker-stop   - Parar container"
    Write-Host "  docker-logs   - Ver logs"
    Write-Host ""
    Write-Host "Limpeza:" -ForegroundColor Yellow
    Write-Host "  clean         - Limpar arquivos temporários"
    Write-Host ""
}

function Install-Dependencies {
    Write-Host "Instalando dependências..." -ForegroundColor Green
    python -m pip install --upgrade pip
    pip install -r requirements.txt
    Write-Host "Dependências instaladas!" -ForegroundColor Green
}

function Setup-Environment {
    Write-Host "Configurando ambiente..." -ForegroundColor Green
    
    if (-not (Test-Path "venv")) {
        Write-Host "Criando ambiente virtual..."
        python -m venv venv
    }
    
    Write-Host "Ativando ambiente virtual..."
    & ".\venv\Scripts\Activate.ps1"
    
    Install-Dependencies
    
    if (-not (Test-Path ".env")) {
        Write-Host "Criando arquivo .env..."
        Copy-Item ".env.example" ".env"
        Write-Host "IMPORTANTE: Configure suas API keys no arquivo .env" -ForegroundColor Yellow
    }
    
    Write-Host "Setup completo!" -ForegroundColor Green
}

function Run-Tests {
    Write-Host "Executando testes..." -ForegroundColor Green
    pytest tests/ -v
}

function Run-TestsCoverage {
    Write-Host "Executando testes com cobertura..." -ForegroundColor Green
    pytest tests/ -v --cov=src --cov-report=html --cov-report=term
    Write-Host ""
    Write-Host "Relatório HTML gerado em: htmlcov/index.html" -ForegroundColor Cyan
}

function Run-Lint {
    Write-Host "Executando pylint..." -ForegroundColor Green
    pylint src/ --fail-under=7.0
}

function Run-App {
    Write-Host "Iniciando aplicação..." -ForegroundColor Green
    streamlit run app.py
}

function Check-Setup {
    Write-Host "Verificando setup..." -ForegroundColor Green
    python check_setup.py
}

function Docker-Build {
    Write-Host "Building Docker image..." -ForegroundColor Green
    docker-compose build
}

function Docker-Run {
    Write-Host "Iniciando container..." -ForegroundColor Green
    docker-compose up -d
    Write-Host "Container rodando em: http://localhost:8501" -ForegroundColor Cyan
}

function Docker-Stop {
    Write-Host "Parando container..." -ForegroundColor Green
    docker-compose down
}

function Docker-Logs {
    Write-Host "Logs do container:" -ForegroundColor Green
    docker-compose logs -f
}

function Clean-Temp {
    Write-Host "Limpando arquivos temporários..." -ForegroundColor Green
    
    Get-ChildItem -Path . -Include __pycache__ -Recurse -Force | Remove-Item -Force -Recurse -ErrorAction SilentlyContinue
    Get-ChildItem -Path . -Include *.pyc -Recurse -Force | Remove-Item -Force -ErrorAction SilentlyContinue
    
    Remove-Item -Path ".pytest_cache" -Recurse -Force -ErrorAction SilentlyContinue
    Remove-Item -Path "htmlcov" -Recurse -Force -ErrorAction SilentlyContinue
    Remove-Item -Path ".coverage" -Force -ErrorAction SilentlyContinue
    
    Write-Host "Limpeza concluída!" -ForegroundColor Green
}

# Executar comando
switch ($Command.ToLower()) {
    "help" { Show-Help }
    "install" { Install-Dependencies }
    "setup" { Setup-Environment }
    "test" { Run-Tests }
    "test-cov" { Run-TestsCoverage }
    "lint" { Run-Lint }
    "run" { Run-App }
    "check" { Check-Setup }
    "docker-build" { Docker-Build }
    "docker-run" { Docker-Run }
    "docker-stop" { Docker-Stop }
    "docker-logs" { Docker-Logs }
    "clean" { Clean-Temp }
    default {
        Write-Host "Comando desconhecido: $Command" -ForegroundColor Red
        Write-Host ""
        Show-Help
    }
}
