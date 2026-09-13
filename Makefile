.PHONY: help install install-dev test cov cov-html lint clean ci run

PYTHON := python
PYTEST := pytest
COV_ARGS := --cov=app --cov=cinelog_core --cov-branch --cov-report=term-missing

help:  ## Mostra esta ajuda
	@grep -E '^[a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) | \
		awk 'BEGIN {FS = ":.*?## "}; {printf "  \033[36m%-15s\033[0m %s\n", $$1, $$2}'

install:  ## Instala só dependências de produção
	$(PYTHON) -m pip install -r requirements.txt

install-dev:  ## Instala produção + dev (pytest, coverage)
	$(PYTHON) -m pip install -r requirements-dev.txt

test:  ## Roda todos os testes (rápido, sem cobertura)
	$(PYTEST)

cov:  ## Roda testes com cobertura (terminal)
	$(PYTEST) $(COV_ARGS)

cov-html:  ## Gera relatório HTML em htmlcov/
	$(PYTEST) $(COV_ARGS) --cov-report=html
	@echo "Abra: htmlcov/index.html"

cov-fail:  ## Roda cobertura e FALHA se < 100%
	$(PYTEST) $(COV_ARGS) --cov-fail-under=100

lint:  ## Checagem básica de sintaxe e imports
	$(PYTHON) -m py_compile app.py cinelog_core.py
	$(PYTHON) -m compileall -q tests/
	@echo "OK"

run:  ## Sobe a API local
	$(PYTHON) app.py

clean:  ## Limpa artefatos de teste
	rm -rf .pytest_cache htmlcov .coverage .coverage.*
	find . -type d -name __pycache__ -exec rm -rf {} +
	find . -type f -name '*.py[co]' -delete

ci: test cov-fail  ## Roda o que o CI roda
