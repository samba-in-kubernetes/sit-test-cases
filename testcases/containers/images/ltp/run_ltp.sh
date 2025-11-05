#!/bin/bash

SELF=$(basename "${BASH_SOURCE[0]}")
TESTDIR="${1:-"/testdir"}"

declare -a LTP_TESTS=(
	"aio01"
	"aio02"
	"chdir01"
	"chdir04"
	"close01"
	"close02"
	"close_range01"
	"close_range02"
	"creat01"
	"creat03"
	"creat04"
	"diotest1"
	"diotest2"
	"diotest3"
	"diotest5"
	"diotest6"
	"faccessat01"
	"dup01"
	"dup02"
	"dup03"
	"dup04"
	"fallocate02"
	"fallocate04"
	"fallocate05"
	"fallocate06"
	"fchdir01"
	"fchdir02"
	"fchmod06"
	"fchmodat02"
	"fchown01"
	"fchown04"
	"fcntl01"
	"fcntl02"
	"fcntl03"
	"fcntl04"
	"fcntl05"
	"fdatasync01"
	"fdatasync02"
	"fgetxattr01"
	"fgetxattr03"
	"flock01"
	"flock03"
	"flock04"
	"flock06"
	"fremovexattr01"
	"fremovexattr02"
	"fsetxattr01"
	"fstat03"
	"fstatat01"
	"fstatfs01"
	"fstatfs02"
	"fsync01"
	"fsync02"
	"ftest01"
	"ftest02"
	"ftest03"
	"ftest04"
	"ftest05"
	"ftest06"
	"ftest07"
	"ftest08"
	"ftruncate01"
	"ftruncate03"
	"getcwd01"
	"getcwd02"
	"getdents01"
	"getdents02"
	"inode01"
	"inode02"
	"lftest"
	"link02"
	"link05"
	"llseek01"
	"llseek02"
	"llseek03"
	"lremovexattr01"
	"lseek01"
	"lseek07"
	"mkdir04"
	"mkdir09"
	"mmap01"
	"mmap02"
	"mmap03"
	"mmap04"
	"mmap05"
	"mmap06"
	"mmap08"
	"mmap09"
	"mmap12"
	"mmap13"
	"mmap17"
	"mmap18"
	"mmap19"
	"mmap20"
	"munmap01"
	"munmap03"
	"open02"
	"open03"
	"open09"
	"open13"
	"openat01"
	"openat02"
	"openfile"
	"open_tree01"
	"open_tree02"
	"pread01"
	"pread02"
	"preadv01"
	"preadv02"
	"pwrite01"
	"pwrite02"
	"pwrite03"
	"pwrite04"
	"pwritev01"
	"pwritev02"
	"read01"
	"read02"
	"read04"
	"readahead01"
	"readdir01"
	"readv01"
	"readv02"
	"realpath01"
	"removexattr01"
	"removexattr02"
	"rename01"
	"rename03"
	"rename04"
	"rename05"
	"rename06"
	"rename07"
	"rename08"
	"rename10"
	"rename12"
	"rename13"
	"rename14"
	"rmdir01"
	"rmdir03"
	"setxattr01"
	"stat02"
	"statfs01"
	"statx03"
	"statx04"
	"statx08"
	"truncate02"
	"unlink07"
	"unlinkat01"
	"ustat01"
	"ustat02"
	"write01"
	"write02"
	"writev01"
	"writev02"
)

ERROR_MSG=()
_msg() { echo "$SELF: $*" >&2; }
_try() { ( "$@" ) || ERROR_MSG+=("$*"); }
_run() { echo "$SELF: $*" >&2; _try "$@"; }

_sit_check_errors() {
	if [ ${#ERROR_MSG[@]} -ne 0 ]; then
		echo "Errors occurred during LTP tests:"
		for err in "${ERROR_MSG[@]}"; do
			echo "$err" >&2
		done
		exit 1
	else
		echo "All LTP tests completed successfully."
	fi
}

_sit_pre_ltp_tests() {
	export LTPROOT="/opt/ltp"
	export LTP_COLORIZE_OUTPUT=0
	export LTP_TIMEOUT_MUL=10
	export TMPDIR="${TESTDIR}"
	export PATH="${PATH}:${LTPROOT}/testcases/bin"
	export FSSTRESS_PROG="${LTPROOT}/testcases/bin/fsstress"

	mkdir -p "${TESTDIR}"
	_msg "LTPROOT=${LTPROOT}"
	_msg "TMPDIR=${TMPDIR}"
}

_sit_run_ltp_tests() {
	local test_path

	for test in "${LTP_TESTS[@]}"; do
		test_path="${LTPROOT}/testcases/bin/${test}"
		_run "${test_path}"
	done
}

_sit_run_ltp_fsstress_with() {
	_run ${FSSTRESS_PROG} "$@" -d "${TMPDIR}"
}

_sit_run_ltp_fsstress() {
	_sit_run_ltp_fsstress_with -n 1 -p 1 -r
	_sit_run_ltp_fsstress_with -n 10 -p 10 -r
	_sit_run_ltp_fsstress_with -n 1000 -p 10 -r \
		-f creat=1000 -f read=100 -f write=100 \
		-f stat=100 -f mkdir=100 -f getdents=100 \
		-f truncate=10
}


_sit_pre_ltp_tests
_sit_run_ltp_tests
_sit_run_ltp_fsstress
printf "\n\n\n"
_sit_check_errors


