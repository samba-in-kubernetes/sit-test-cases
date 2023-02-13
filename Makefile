test:
	@ PYTHONPATH=`pwd` ./run_all_tests.sh test-info.yml

sanity_test:
	@ PYTHONPATH=`pwd` ./run_all_tests.sh test-info.yml sanity_tests
