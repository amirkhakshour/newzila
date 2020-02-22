VENV = venv
PYTEST = $(PWD)/$(VENV)/bin/py.test
.PHONY: build test clean venv

clean_py:
	find . -name '*.pyc' -delete
	find . -name '__pycache__' -delete
	rm -Rf *.egg-info
	rm -Rf dist/
	rm -Rf build/

##################
# Install commands
##################
install: install-base
install_local: install install-local
install_prod: install install-prod

install-base: ## Install base requirements
	pip install -r requirements/base.txt

install-local:  ## Install local requirements
	pip install -r requirements/local.txt

install-prod: ## Install production requirements
	pip install -r requirements/production.txt

venv: ## Create a virtual env and install test and production requirements
	$(shell which python3) -m venv $(VENV)

check_venv:
ifeq ($(VIRTUAL_ENV),)
	$(error "Run frost from a virtualenv (try 'make venv && source venv/bin/activate')")
endif

#############################
# Sandbox management commands
#############################
build: clean load_data statics

clean:
	# Remove media
	-rm -rf staticfiles
	-rm -f db.sqlite
	# Create database
	./manage.py migrate

load_data:
	./manage.py loaddata ./newzila/newsletter/fixtures/data.json

statics:
	./manage.py collectstatic --noinput

server:
	./manage.py runserver_plus 0.0.0.0:8000
