SHELL = /usr/bin/env bash -e -o pipefail

# Python
PYTHON = python3
PYTHON_PIP = $(PYTHON) -m pip
PYTHON_PIP_VERSION_SPECIFIER = ~=22.3.1
PYTHON_SETUPTOOLS_VERSION_SPECIFIER = ~=65.6.1
PYTHON_WHEEL_VERSION_SPECIFIER = ~=0.38.4
PYTHON_VIRTUALENV_DIR = .pyenv
PYTHON_PIP_TOOLS_VERSION_SPECIFIER = ~=6.10.0
PYTHON_PIP_TOOLS_SRC_FILES = requirements.in requirements-dev.in

# Django Admin
DJANGO_ADMIN = $(PYTHON) $(CURDIR)/manage.py

# Black
BLACK = black --config .black.cfg.toml

# Mypy
MYPY_CACHE_DIR = $(CURDIR)/.mypy_cache

# Coverage.py
COVERAGE = coverage
COVERAGE_TEST_RCFILE = $(CURDIR)/.coveragerc.test.ini
COVERAGE_TEST_DATA_FILE = $(CURDIR)/.test.coverage

# Test Reports
TEST_REPORT_DIR = $(CURDIR)/test_reports

include make/_common/help.mk
include make/django.mk
include make/python.mk
include make/vcs.mk

.DEFAULT_GOAL := help

.PHONY: help
help:
	@echo "$@: Read README.md"
	@echo
	@$(MAKE) -s help-tasks

.PHONY: clean
clean: clean-build
clean: ## Delete temporary files, logs, cached files, build artifacts, etc.
	find . -iname __pycache__ -type d -prune -exec rm -r {} \;
	find . -iname '*.py[cod]' -delete

	$(RM) -r "$(MYPY_CACHE_DIR)"
	$(RM) -r "$(COVERAGE_TEST_DATA_FILE)"
	$(RM) -r "$(TEST_REPORT_DIR)"

.PHONY: clean-all
clean-all: clean
clean-all: ## Delete (almost) everything that can be reconstructed later
	$(RM) -r *.egg-info/

.PHONY: clean-build
clean-build: ## Remove build artifacts
	$(RM) -r .eggs/
	$(RM) -r build/
	$(RM) -r dist/

	find . -name '*.egg-info' -exec $(RM) -r {} +
	find . -name '*.egg' -exec $(RM) {} +

.PHONY: install
install: install-deps
install: ## Install
	$(PYTHON_PIP) install --editable .
	$(PYTHON_PIP) check

.PHONY: install-dev
install-dev: install-deps-dev
install-dev: ## Install for development
	$(PYTHON_PIP) install --editable .
	$(PYTHON_PIP) check

.PHONY: install-deps
install-deps: ## Install dependencies
	$(PYTHON_PIP) install -r requirements.txt
	$(PYTHON_PIP) check

.PHONY: install-deps-dev
install-deps-dev: install-deps
install-deps-dev: python-pip-tools-install
install-deps-dev: ## Install dependencies for development
	$(PYTHON_PIP) install -r requirements-dev.txt
	$(PYTHON_PIP) check

.PHONY: build
build: ## Build Python package
	$(PYTHON) setup.py build

.PHONY: dist
dist: build
dist: ## Create Python package distribution
	$(PYTHON) setup.py sdist
	$(PYTHON) setup.py bdist_wheel

.PHONY: upload-release
upload-release: ## Upload dist packages
	$(PYTHON) -m twine upload 'dist/*'

.PHONY: deploy
deploy: upload-release
deploy: ## Deploy or publish

.PHONY: lint
lint: ## Run linters
	flake8
	mypy
	isort --check-only .
	$(PYTHON) setup.py check --metadata
	$(BLACK) --check .

.PHONY: lint-report
lint-report: FLAKE8_JUNIT_REPORT_DIR = $(TEST_REPORT_DIR)/junit/flake8
lint-report: MYPY_JUNIT_REPORT_DIR = $(TEST_REPORT_DIR)/junit/mypy
lint-report: ## Run linters and generate reports
	mkdir -p "$(FLAKE8_JUNIT_REPORT_DIR)"
	-flake8 --format junit-xml --output-file "$(FLAKE8_JUNIT_REPORT_DIR)/report.junit.xml"

	mkdir -p "$(MYPY_JUNIT_REPORT_DIR)"
	-mypy --no-pretty --junit-xml "$(MYPY_JUNIT_REPORT_DIR)/report.junit.xml"

.PHONY: lint-fix
lint-fix: ## Fix lint errors
	$(BLACK) .
	isort .

.PHONY: test
test: django-test
test: ## Run tests

.PHONY: test-report
test-report: django-test-report
test-report: ## Run tests and generate reports

.PHONY: test-coverage
test-coverage: PYTHON =
test-coverage: export COVERAGE_RCFILE = $(COVERAGE_TEST_RCFILE)
test-coverage: export COVERAGE_FILE = $(COVERAGE_TEST_DATA_FILE)
test-coverage: django-test-coverage
test-coverage: ## Run tests and measure code coverage

.PHONY: test-coverage-report
test-coverage-report: export COVERAGE_RCFILE = $(COVERAGE_TEST_RCFILE)
test-coverage-report: export COVERAGE_FILE = $(COVERAGE_TEST_DATA_FILE)
test-coverage-report: ## Run tests, measure code coverage, and generate reports
	$(COVERAGE) report
	$(COVERAGE) html
