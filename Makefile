#!make
include .env

.ONESHELL:

.DEFAULT_GOAL := run

PYTHON = ./venv/bin/python3
PIP = ./venv/bin/pip

venv:
	python3 -m venv venv
	. ./venv/bin/activate

install: venv
ifeq (${DEV_ENV}, true)
	echo "You are intalling development dependencies"
	$(PIP) install git+https://github.com/nosix/raspberry-gpio-emulator/
	$(PIP) install black
	$(PIP) install pylint
	$(PIP) install pytest coverage
else
	$(PIP) install RPi.GPIO==0.7.1
endif
	$(PIP) install -r requirements.txt

format: install
	$(PYTHON) -m black .
	
lint: install
	$(PYTHON) -m pylint --exit-zero app.py ./home_controller ./tests

test: install
	$(PYTHON) -m coverage run -m pytest -v
	$(PYTHON) -m coverage report

beauty: format lint test	

build: install
	export LOGS_DIR=${LOGS_DIR} && \
    export DATA_DIR=${DATA_DIR} && \
    export CONFIG_DIR=${CONFIG_DIR} && \
	mkdir -p ${LOGS_DIR} ${DATA_DIR}

run: build
	$(PYTHON) -m gunicorn --worker-class=eventlet --bind=0.0.0.0:5000 app:app

install-docker:
	sudo apt-get update -y
	sudo apt-get install -y ca-certificates curl gnupg lsb-release
	sudo mkdir -m 0755 -p /etc/apt/keyrings
	curl -fsSL https://download.docker.com/linux/debian/gpg | sudo gpg --dearmor -o /etc/apt/keyrings/docker.gpg
	echo "deb [arch=$(dpkg --print-architecture) signed-by=/etc/apt/keyrings/docker.gpg] https://download.docker.com/linux/debian \
  		$(lsb_release -cs) stable" | sudo tee /etc/apt/sources.list.d/docker.list > /dev/null
	sudo apt-get update -y
	sudo apt-get install -y docker-ce docker-ce-cli containerd.io docker-buildx-plugin docker-compose-plugin

deploy: install-docker
	docker-compose -f docker-compose.pro.yml up --build