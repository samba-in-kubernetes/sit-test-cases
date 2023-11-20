SELF = $(lastword $(MAKEFILE_LIST))
ROOT_DIR = $(realpath $(dir $(SELF)))
TOX_OUTPUT_FILE ?= /var/log/tox.out

PYTHONPATH := .
TEST_INFO_FILE := test-info.yml
PATH := $(PATH):/usr/local/bin
export PYTHONPATH TEST_INFO_FILE PATH

define runtox
	@cd "$(ROOT_DIR)" && tox -e $1
endef

define runtox_outfile
	@cd "$(ROOT_DIR)" && tox -e $1 > $(TOX_OUTPUT_FILE)
endef

.PHONY: test
test:
	$(call runtox_outfile, "pytest")

.PHONY: sanity_test
sanity_test:
	$(call runtox_outfile, "sanity")

.PHONY: check-mypy
check-mypy:
	$(call runtox, "mypy")

.PHONY: check-flake8
check-flake8:
	$(call runtox, "flake8")

PHONY: check-black
check-black:
	$(call runtox, "black")

