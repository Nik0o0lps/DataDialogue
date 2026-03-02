.PHONY: help install test lint run docker-build docker-run docker-stop clean

help:
	@echo "Comandos disponíveis:"
	@echo "  make install       - Instalar dependências Python"
	@echo "  make test          - Executar testes com pytest"
	@echo "  make test-cov      - Testes com relatório de cobertura"
	@echo "  make lint          - Executar pylint"
	@echo "  make run           - Iniciar aplicação Streamlit"
	@echo "  make docker-build  - Build da imagem Docker"
	@echo "  make docker-run    - Executar container Docker"
	@echo "  make docker-stop   - Parar container Docker"
	@echo "  make docker-logs   - Ver logs do container"
	@echo "  make clean         - Limpar arquivos temporários"

install:
	pip install --upgrade pip
	pip install -r requirements.txt

test:
	pytest tests/ -v

test-cov:
	pytest tests/ -v --cov=src --cov-report=html --cov-report=term

lint:
	pylint src/ --fail-under=7.0

run:
	streamlit run app.py

docker-build:
	docker-compose build

docker-run:
	docker-compose up -d

docker-logs:
	docker-compose logs -f

docker-stop:
	docker-compose down

docker-restart:
	docker-compose restart

clean:
	find . -type d -name __pycache__ -exec rm -rf {} + 2>/dev/null || true
	find . -type f -name "*.pyc" -delete 2>/dev/null || true
	find . -type f -name "*.pyo" -delete 2>/dev/null || true
	rm -rf .pytest_cache 2>/dev/null || true
	rm -rf htmlcov 2>/dev/null || true
	rm -rf .coverage 2>/dev/null || true
	rm -rf *.egg-info 2>/dev/null || true
	rm -rf dist build 2>/dev/null || true

check-setup:
	python check_setup.py

test-agent:
	python test_agent.py
