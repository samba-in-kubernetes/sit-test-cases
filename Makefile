SELF = $(lastword $(MAKEFILE_LIST))
ROOT_DIR = $(realpath $(dir $(SELF)))

PYTHONPATH := .
TEST_INFO_FILE := test-info.yml
PATH := $(PATH):/usr/local/bin
export PYTHONPATH TEST_INFO_FILE PATH

MYPY_CMD = $(shell command -v mypy 2> /dev/null)

test:
	@pytest -v `cat testcases/tests|sed 's/^/testcases\//'`

sanity_test:
	@pytest -v testcases/consistency

.PHONY: test sanity_test

.PHONY: check-mypy
check-mypy:
	[ ! -z "$(MYPY_CMD)" ] && $(MYPY_CMD) --no-color-output "$(ROOT_DIR)"
