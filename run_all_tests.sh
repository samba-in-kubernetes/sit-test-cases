#!/bin/bash

TESTS_FILE="tests"
if [ -n "$2" ]
then
	TESTS_FILE=$2
fi

echo_success() {
	echo  "[ OK ] "
	return 0
}

test_info_file_dir=$(cd `dirname $1` && pwd)
test_info_file=$test_info_file_dir/`basename $1`

cd testcases
for i in `cat ${TESTS_FILE}|sed 's/#.*//'|sed 's/  +//g'|grep -v '^ *$'`
do
	echo -n "$i "
	if [ -x $i/run_test ] && ! $i/run_test $test_info_file
	then
		exit 1
	fi
	echo_success

done
