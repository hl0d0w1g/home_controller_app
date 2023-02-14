.ONESHELL:

.DEFAULT_GOAL := deploy

PYTHON = ./venv/bin/python3
PIP = ./venv/bin/pip

install-docker:
	sudo apt-get update -y
	sudo apt-get install -y ca-certificates curl gnupg lsb-release
	sudo mkdir -m 0755 -p /etc/apt/keyrings
	curl -fsSL https://download.docker.com/linux/debian/gpg | sudo gpg --dearmor -o /etc/apt/keyrings/docker.gpg
	echo "deb [arch=$(dpkg --print-architecture) signed-by=/etc/apt/keyrings/docker.gpg] https://download.docker.com/linux/debian \
  		$(lsb_release -cs) stable" | sudo tee /etc/apt/sources.list.d/docker.list > /dev/null
	sudo apt-get update -y
	sudo apt-get install -y docker-ce docker-ce-cli containerd.io docker-buildx-plugin docker-compose-plugin

venv:
	python3 -m venv venv
	. ./venv/bin/activate

install: venv
	$(PIP) install -r requirements.txt
	$(PIP) install black
	$(PIP) install pylint
	$(PIP) install pytest
	$(PIP) install pytest-custom_exit_code

format: install
	$(PYTHON) -m black .
	
lint: install
	$(PYTHON) -m pylint --exit-zero app.py ./home_controller ./tests

test: install
	$(PYTHON) -m pytest --suppress-no-test-exit-code

beauty: format lint test

run: beauty
	$(PYTHON) -m flask run --host=0.0.0.0

deploy-dev:
	docker-compose -f docker-compose.dev.yml up --build

deploy: install-docker
	docker-compose -f docker-compose.pro.yml up --build