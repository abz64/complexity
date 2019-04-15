SHELL := /bin/bash
CURR_DIR:=$(shell dirname $(realpath $(lastword $(MAKEFILE_LIST))))
export PYTHONPATH:=.:$(PYTHONPATH)


.PHONY: algos
algos:
	pipenv run python3 algos.py --log-level INFO


.PHONY: complexity
complexity:
	pipenv run python3 complexity.py --log-level INFO


.PHONY: data_gen
data_gen:
	pipenv run python3 data_gen.py --log-level INFO


.PHONY: env
env:
	pipenv lock
	pipenv sync


.PHONY: clean
clean:
	pipenv --rm
