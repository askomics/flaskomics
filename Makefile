SHELL := /bin/bash

PYTHON=python3
PIP=pip3
PIPENV=pipenv
TESTPYTHON:=$(shell $(PYTHON) --version 2>/dev/null)
PIPENVOPTS=
FLASKOPTS=
PYTESTOPTS=
TESTFILE?=tests
NTASKS?=1

HOST?=0.0.0.0
PORT?=5000

DOCPORT?=8000

NPM=npm
TESTNPM:=$(shell $(NPM) -v 2>/dev/null)
NPMOPTS=

BASEDIR=$(CURDIR)
VENVDIR=$(BASEDIR)/venv
NODEDIR=$(BASEDIR)/node_modules
ACTIVATE=$(VENVDIR)/bin/activate
PYCACHE=$(BASEDIR)/__pycache__
CONFIG=$(BASEDIR)/config/askomics.ini

MODE?=prod
ifeq ($(MODE), dev)
	PIPENVOPTS+=--dev
	NPMOPTS+=dev
	FLASKOPTS+=production
	PYTESTOPTS+=-vv
else
	NPMOPTS+=prod
	FLASKOPTS+=development
	PYTESTOPTS+=-q --disable-warnings
endif

TRAVIS?=false
ifeq ($(TRAVIS), true)
	PYTESTOPTS+=--cov=. --cov-config=.coveragerc
endif


help:
	@echo 'Makefile for AskOmics'
	@echo ''
	@echo 'Usage:'
	@echo '    make help                                                          Display help'
	@echo '    make clean                                                         Uninstall everything'
	@echo '    make install [MODE=dev]                                            Install Python and Js dependencies (+ dev dependencies if MODE=dev)'
	@echo '    make build [MODE=dev]                                              Build javascript (and watch for update if MODE=DEV)'
	@echo '    make serve [MODE=dev] [HOST=0.0.0.0] [PORT=5000] [NTASKS=1]        Serve AskOmics at $(HOST):$(PORT)'
	@echo '    make test                                                          Lint and test javascript and python code'
	@echo '    make serve-doc [DOCPORT=8000]                                      Serve documentation at localhost:$(DOCPORT)'
	@echo '    make update-base-url                                               Update all graphs from an old base_url to a new base_url'
	@echo '    make clear-cache                                                   Clear abstraction cache'
	@echo ''
	@echo 'Examples:'
	@echo '    make clean install build serve NTASKS=10                           Clean install and serve AskOmics in production mode, 10 celery tasks in parallel'
	@echo '    make clean install serve MODE=dev NTASKS=10                        Clean install and serve AskOmics in development mode, 10 celery tasks in parallel'
	@echo ''
	@echo '    make clean install                                                 Clean install AskOmics'
	@echo '    make clean install  MODE=dev                                       Clean install AskOmics in development mode'
	@echo '    make serve NTASKS=10                                               Serve AskOmics, 10 celery tasks in parallel'
	@echo '    make serve MODE=dev NTASKS=10                                      Serve AskOmics in development mode, 10 celery tasks in parallel'
	@echo ''
	@echo '    make pytest MODE=dev TESTFILE=tests/test_api.py                    Test tests/test_api file only'


serve-doc: check-venv
	@echo "Serving docs..."
	. $(ACTIVATE)
	mkdocs serve -a localhost:$(DOCPORT)

test: test-js test-python

test-js: eslint

eslint: check-node-modules
	@echo -n 'Linting javascript...                                        '
	$(NODEDIR)/.bin/eslint --config $(BASEDIR)/.eslintrc.yml "$(BASEDIR)/askomics/react/src/**"
	@echo "Done"

test-python: pylint pytest

pytest: check-venv
	@echo 'Testing python...'
	. $(ACTIVATE)
	pytest $(PYTESTOPTS) $(TESTFILE)

pylint: check-venv
	@echo -n 'Linting python...                                            '
	. $(ACTIVATE)
	flake8 $(BASEDIR)/askomics $(BASEDIR)/tests --ignore=E501,W504
	@echo "Done"

serve: check-venv build-config create-user
	$(MAKE) -j 3 serve-askomics serve-celery build-js

serve-askomics: check-venv build-config create-user
	@echo 'Serving AskOmics...'
	. $(ACTIVATE)
ifeq ($(MODE), dev)
	FLASK_ENV=development FLASK_APP=app flask run --host=$(HOST) --port $(PORT)
else
	FLASK_ENV=production FLASK_APP=app gunicorn -b $(HOST):$(PORT) app
endif

serve-celery: check-venv build-config create-user
	@echo 'Serving Celery...'
	. $(ACTIVATE)
ifeq ($(MODE), dev)
	FLASK_ENV=development FLASK_APP=app watchmedo auto-restart -d $(BASEDIR)/askomics --recursive -p '*.py' --ignore-patterns='*.pyc' -- celery -A askomics.tasks.celery worker -Q default -c $(NTASKS) -n default -l info
else
	FLASK_ENV=production FLASK_APP=app celery -A askomics.tasks.celery worker -Q default -c $(NTASKS) -n default -l info
endif

check-venv:
	test -s $(ACTIVATE) || { echo "$(ACTIVATE) not found. Run make install first"; exit 1; }

check-node-modules:
	test -s $(NODEDIR) || { echo "$(NODEDIR) not found. Run make install first"; exit 1; }

build-config:
	@echo -n 'Building config file...                                      '
	bash cli/set_config.sh
	@echo 'Done'

create-user:
	@echo -n 'Creating first user...                                       '
	. $(ACTIVATE)
	bash cli/set_user.sh
	@echo 'Done'

update-base-url: check-venv
	@echo 'Updating base url...'
	. $(ACTIVATE)
	bash cli/update_base_url.sh
	@echo 'Done'

clear-cache: check-venv
	@echo 'Clearing abstraction cache...'
	. $(ACTIVATE)
	bash cli/clear_cache.sh
	@echo 'Done'

build: build-js

build-js: check-node-modules
	@echo 'Building askomics.js...                                        '
	$(NPM) run --silent $(NPMOPTS)
	@echo '                                                             Done'

install: install-python install-js

fast-install:
	$(MAKE) -j 2 install-python install-js

install-python: check-python
	@echo -n 'Building python virtual environment...                       '
	$(PYTHON) -m venv $(VENVDIR)
	@echo 'Done'
	@echo -n 'Sourcing Python virtual environment...                       '
	. $(ACTIVATE)
	@echo 'Done'
	@echo -n 'Upgrading pip...                                             '
	$(PIP) install --upgrade pip > /dev/null
	@echo 'Done'
	@echo 'Installing Python dependencies inside virtual environment... '
	$(PIP) install -e . > /dev/null
	PIPENV_VERBOSITY=-1 $(PIPENV) install $(PIPENVOPTS)
	@echo '                                                             Done'

install-js: check-npm
	@echo  'Installing javascript dependencies inside node_modules...    '
	$(NPM) cache verify
	$(NPM) install
	@echo '                                                             Done'

clean: clean-js clean-python

clean-lock: clean-lockfile-python clean-lockfile-js

clean-lockfile-python:
	@echo -n 'Cleaning Pipfile.lock files...                                     '
	$(RM) -rf Pipfile.lock
	@echo 'Done'

clean-lockfile-js:
	@echo -n 'Cleaning package-lock.json files...                                     '
	$(RM) -rf package-lock.json
	@echo 'Done'

clean-python:
	@echo -n 'Cleaning python files...                                     '
	$(RM) -rf $(VENVDIR)
	$(RM) -rf $(PYCACHE)
	@echo 'Done'

clean-js:
	@echo -n 'Cleaning javascript files...                                 '
	$(RM) -rf $(NODEDIR)
	@echo 'Done'

clean-config:
	@echo -n 'Removing config/askomics.ini...                              '
	$(RM) $(CONFIG)
	@echo 'Done'

force-update: force-update-js force-update-python

force-update-js: update-js clean-js
	@echo -n 'Removing package-lock.json...                                '
	$(RM) package-lock.json
	@echo "Done"
	$(MAKE) install-js

force-update-python: clean-python
	@echo -n 'Removing Pipfile.lock...                                     '
	$(RM) Pipfile.lock
	@echo "Done"
	$(MAKE) install-python

update-js:
	@echo 'Updating js dependencies...'
	$(NODEDIR)/.bin/ncu -u

check: check-python	check-npm

check-python:
ifndef TESTPYTHON
	$(error $(PYTHON) not found. Abording)
endif

check-npm:
ifndef TESTNPM
	$(error $(NPM) not found. Abording)
endif

.PHONY: test test-js eslint test-python pytest pylint build build-js help clean-install install install-python install-js check check-python check-npm clean clean-python clean-js serve-celery serve-askomics serve clean-lock clean-lockfile-python clean-lockfile-js
.SILENT: serve test test-js check-venv check-node-modules
.ONESHELL:
