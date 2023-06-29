SELF = $(lastword $(MAKEFILE_LIST))
ROOT_DIR = $(realpath $(dir $(SELF)))

PYTHONPATH := .
TEST_INFO_FILE := test-info.yml
PATH := $(PATH):/usr/local/bin
export PYTHONPATH TEST_INFO_FILE PATH

MYPY_CMD = $(shell command -v mypy 2> /dev/null)
FLAKE8_CMD = $(shell command -v flake8 2> /dev/null)
BLACK_CMD = $(shell command -v black 2> /dev/null)

test:
	@pytest -v `cat testcases/tests|sed 's/^/testcases\//'`

sanity_test:
	@pytest -v testcases/consistency

.PHONY: test sanity_test

.PHONY: check-mypy
check-mypy:
	[ ! -z "$(MYPY_CMD)" ] && $(MYPY_CMD) --no-color-output "$(ROOT_DIR)"

.PHONY: check-flake8
check-flake8:
	[ ! -z "$(FLAKE8_CMD)" ] && $(FLAKE8_CMD) "$(ROOT_DIR)"

PHONY: check-black
check-black:
	[ ! -z "$(BLACK_CMD)" ] && $(BLACK_CMD) -l 79 --check "$(ROOT_DIR)"
	
PHONY: fmt-black
fmt-black:
	[ ! -z "$(BLACK_CMD)" ] && $(BLACK_CMD) -q -l 79 "$(ROOT_DIR)"	
