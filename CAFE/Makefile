# Makefile для проекта Cafe
# Автоматизация основных задач разработки

.PHONY: help setup run test test-smoke test-unit coverage build-lib install-lib docs clean check lint

# Цвета для вывода
BLUE := \033[34m
GREEN := \033[32m
YELLOW := \033[33m
RED := \033[31m
NC := \033[0m

# Пути
SRC_DIR := src
TESTS_DIR := tests
CORE_DIR := packages/core
DOCS_DIR := docs

help:
	@echo "$(BLUE)====================================$(NC)"
	@echo "$(GREEN)  CAFE Project - Available Commands$(NC)"
	@echo "$(BLUE)====================================$(NC)"
	@echo ""
	@echo "$(GREEN)Development:$(NC)"
	@echo "  make setup           Install dependencies and setup environment"
	@echo "  make run             Run the Tkinter application"
	@echo ""
	@echo "$(GREEN)Testing:$(NC)"
	@echo "  make test            Run all tests"
	@echo "  make test-smoke      Run smoke tests only"
	@echo "  make test-unit       Run unit tests only"
	@echo "  make coverage        Run tests with coverage report"
	@echo ""
	@echo "$(GREEN)Build & Package:$(NC)"
	@echo "  make build-lib       Build reusable core component"
	@echo "  make install-lib     Install core component locally"
	@echo ""
	@echo "$(GREEN)Documentation:$(NC)"
	@echo "  make docs            Build documentation (if configured)"
	@echo ""
	@echo "$(GREEN)Utilities:$(NC)"
	@echo "  make check           Full verification (test + build)"
	@echo "  make clean           Remove generated files"
	@echo "  make lint            Run linter"
	@echo ""

setup:
	@echo "$(GREEN)Setting up environment...$(NC)"
	pip install -r requirements.txt
	pip install -e ./packages/core
	@echo "$(GREEN)✓ Setup complete!$(NC)"

run:
	@echo "$(GREEN)Starting Cafe Application...$(NC)"
	python -m src.main

test:
	@echo "$(GREEN)Running all tests...$(NC)"
	py -m pytest $(TESTS_DIR)/ -v --tb=short

test-smoke:
	@echo "$(GREEN)Running smoke tests...$(NC)"
	py -m pytest $(TESTS_DIR)/test_smoke.py -v

test-unit:
	@echo "$(GREEN)Running unit tests...$(NC)"
	py -m pytest $(TESTS_DIR)/test_core_*.py -v

coverage:
	@echo "$(GREEN)Running tests with coverage...$(NC)"
	py -m pytest $(TESTS_DIR)/ \
		--cov=$(CORE_DIR) \
		--cov=$(SRC_DIR) \
		--cov=app \
		--cov-report=html \
		--cov-report=term-missing
	@echo ""
	@echo "$(YELLOW)Coverage report: htmlcov/index.html$(NC)"
	@echo "Open it in browser: open htmlcov/index.html"

build-lib:
	@echo "$(GREEN)Building core component...$(NC)"
	cd $(CORE_DIR) && py -m build
	@echo "$(GREEN)✓ Build complete: $(CORE_DIR)/dist/$(NC)"

install-lib:
	@echo "$(GREEN)Installing core component locally...$(NC)"
	pip install -e ./$(CORE_DIR)
	@echo "$(GREEN)✓ Core component installed$(NC)"

docs:
	@echo "$(GREEN)Building documentation...$(NC)"
	@if [ -d "$(DOCS_DIR)" ]; then \
		if [ -f "$(DOCS_DIR)/mkdocs.yml" ]; then \
			cd $(DOCS_DIR) && mkdocs build; \
			echo "$(GREEN)✓ Documentation built: $(DOCS_DIR)/site/$(NC)"; \
		else \
			echo "$(YELLOW)MkDocs config not found. Skipping docs build.$(NC)"; \
		fi; \
	else \
		echo "$(YELLOW)Docs directory not found. Skipping docs build.$(NC)"; \
	fi

check: test build-lib
	@echo ""
	@echo "$(GREEN)====================================$(NC)"
	@echo "$(GREEN)✓ All checks passed!$(NC)"
	@echo "$(GREEN)====================================$(NC)"

clean:
	@echo "$(YELLOW)Cleaning generated files...$(NC)"
	rm -rf __pycache__ */__pycache__ */*/__pycache__
	rm -rf .pytest_cache .coverage htmlcov/
	rm -rf $(CORE_DIR)/dist $(CORE_DIR)/build $(CORE_DIR)/*.egg-info
	rm -rf $(DOCS_DIR)/site
	rm -rf *.db data/*.db
	find . -type d -name "*.pyc" -exec rm -rf {} +
	find . -type f -name "*.pyc" -delete
	@echo "$(GREEN)✓ Clean complete!$(NC)"

lint:
	@echo "$(GREEN)Running linter...$(NC)"
	@if command -v flake8 >/dev/null 2>&1; then \
		flake8 $(SRC_DIR)/ $(CORE_DIR)/ app/ tests/ \
			--max-line-length=100 \
			--ignore=E203,W503; \
	else \
		echo "$(YELLOW)flake8 not installed. Install with: pip install flake8$(NC)"; \
	fi

compose-up:
	docker-compose up --build -d

compose-down:
	docker-compose down
