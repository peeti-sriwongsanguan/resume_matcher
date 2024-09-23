CONDA_ENV_NAME := resume-matcher
CONDA_ACTIVATE := source $$(conda info --base)/etc/profile.d/conda.sh && conda activate $(CONDA_ENV_NAME)

export PYTHONPATH := $(CURDIR)

.PHONY: build run test clean ensure_environment clean_env rebuild_env run_local test_local setup_env test_parser test_job_scraper test_matching_engine test_database

# Function to check if the environment exists and create it if it doesn't
define ensure_environment
	@echo "Current working directory: $$(pwd)"
	@if ! conda info --envs | grep -q $(CONDA_ENV_NAME); then \
		echo "Conda environment '$(CONDA_ENV_NAME)' not found. Creating it now..."; \
		conda env create -f environment.yml; \
	else \
		echo "Updating Conda environment '$(CONDA_ENV_NAME)'..."; \
		conda env update -f environment.yml; \
	fi
	@$(CONDA_ACTIVATE) && python -m spacy download en_core_web_sm
	@if [ ! -f .env ]; then \
		echo "WARNING: .env file not found. Please create a .env file with your Adzuna API credentials (ADZUNA_APP_ID and ADZUNA_API_KEY)."; \
	else \
		echo ".env file found. Ensure it contains your Adzuna API credentials."; \
	fi
endef

build:
	docker-compose build

run:
	docker-compose up

test:
	docker-compose run web python -m pytest

clean:
	docker-compose down
	docker system prune -f

setup_env:
	$(call ensure_environment)

clean_env:
	conda env remove -n $(CONDA_ENV_NAME)

rebuild_env:
	conda env remove -n $(CONDA_ENV_NAME) --yes
	$(call ensure_environment)

run_local: setup_env
	$(CONDA_ACTIVATE) && python run.py

test_parser:
	$(CONDA_ACTIVATE) && python -m tests.test_resume_parser

test_job_scraper:
	$(CONDA_ACTIVATE) && python -m tests.test_job_scraper

test_matching_engine:
	$(CONDA_ACTIVATE) && python -m tests.test_matching_engine

test_database:
	$(CONDA_ACTIVATE) && python -m tests.test_database

test_local: setup_env test_parser test_job_scraper test_matching_engine test_database
	$(CONDA_ACTIVATE) && PYTHONPATH=$(PYTHONPATH) pytest -v
