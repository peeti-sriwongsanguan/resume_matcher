CONDA_ENV_NAME := resume-matcher
CONDA_ACTIVATE := source $$(conda info --base)/etc/profile.d/conda.sh ; conda activate ; conda activate

export PYTHONPATH := $(CURDIR)

.PHONY: build run test clean ensure_environment clean_env rebuild_env run_local test_local setup_env test_parser

# Function to check if the environment exists and create it if it doesn't
define ensure_environment
	@echo "Current working directory: $$(pwd)"
	@echo "Contents of current directory:"
	@ls -la
	@if ! conda info --envs | grep -q $(CONDA_ENV_NAME); then \
		echo "Conda environment '$(CONDA_ENV_NAME)' not found. Creating it now..."; \
		conda env create -f environment.yml; \
	else \
		echo "Updating Conda environment '$(CONDA_ENV_NAME)'..."; \
		conda env update -f environment.yml; \
	fi
	$(CONDA_ACTIVATE) $(CONDA_ENV_NAME) && pip install --upgrade pip setuptools wheel
	$(CONDA_ACTIVATE) $(CONDA_ENV_NAME) && pip install --no-cache-dir -r requirements.txt
	$(CONDA_ACTIVATE) $(CONDA_ENV_NAME) && pip install --no-build-isolation spacy==3.7.6
	$(CONDA_ACTIVATE) $(CONDA_ENV_NAME) && python -m spacy download en_core_web_sm
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
	$(CONDA_ACTIVATE) $(CONDA_ENV_NAME) && python -m app.main

test_parser:
	$(CONDA_ACTIVATE) $(CONDA_ENV_NAME) && python -m tests.test_resume_parser

test_local: setup_env test_parser
	$(CONDA_ACTIVATE) $(CONDA_ENV_NAME) && PYTHONPATH=$(PYTHONPATH) pytest -v




