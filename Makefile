CONDA_ENV_NAME := resume-matcher
CONDA_ACTIVATE := source $$(conda info --base)/etc/profile.d/conda.sh ; conda activate ; conda activate

.PHONY: build run test clean ensure_environment clean_env rebuild_env run_local test_local

# Function to check if the environment exists and create it if it doesn't
define ensure_environment
	@if ! conda info --envs | grep -q $(CONDA_ENV_NAME); then \
		echo "Conda environment '$(CONDA_ENV_NAME)' not found. Creating it now..."; \
		conda create -n $(CONDA_ENV_NAME) python=3.9 -y; \
		$(CONDA_ACTIVATE) $(CONDA_ENV_NAME) && pip install --no-cache-dir -r requirements.txt; \
	else \
		echo "Updating Conda environment '$(CONDA_ENV_NAME)'..."; \
		$(CONDA_ACTIVATE) $(CONDA_ENV_NAME) && pip install --no-cache-dir -r requirements.txt; \
	fi
	@$(CONDA_ACTIVATE) $(CONDA_ENV_NAME) && python -m spacy download en_core_web_sm
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

rebuild_env: clean_env setup_env

run_local: setup_env
	$(CONDA_ACTIVATE) $(CONDA_ENV_NAME) && python app/main.py

test_local: setup_env
	$(CONDA_ACTIVATE) $(CONDA_ENV_NAME) && cd $(CURDIR) && python -m pytest