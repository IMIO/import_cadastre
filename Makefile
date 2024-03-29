CONFIG = config.cfg
include $(CONFIG)
export

SHELL :=/bin/bash

all: printenv install seedpostgres

install:
	virtualenv -p python3 env; \
	source env/bin/activate; \
	pip install -r requirements.txt; \

parsecadastre: printenv
	source env/bin/activate; \
	python3 import.py; \

seedpostgres: printenv
	source env/bin/activate; \
	python3 seedPostgres.py; \

clean:
	rm -Rf env;

printenv:
	@echo Current ENV used for the script
	@echo
	@echo CADASTREDIR is $$CADASTREDIR
	@echo CAD_PG_HOST is $$CAD_PG_HOST
	@echo CAD_DATABASE_NAME is $$CAD_DATABASE_NAME
	@echo CAD_DB_USER_NAME is $$CAD_DB_USER_NAME
	@echo CAD_DB_USER_PASSWORD is $$CAD_DB_USER_PASSWORD
	@echo
