PYTHONPATH := .
TEST_INFO_FILE := test-info.yml
PATH := $(PATH):/usr/local/bin
export PYTHONPATH TEST_INFO_FILE PATH

test:
	@pytest -v `cat testcases/tests|sed 's/^/testcases\//'`

sanity_test:
	@pytest -v testcases/consistency

.PHONY: test sanity_test
