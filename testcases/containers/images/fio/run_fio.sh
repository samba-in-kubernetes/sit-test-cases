#!/usr/bin/env bash
set -o nounset
set -o pipefail
export LC_ALL=C
unset CDPATH

# Global parameters
SELF=$(basename "${BASH_SOURCE[0]}")
FIO_SIZE="${FIO_SIZE:-1G}"
FIO_VERIFY_SIZE="${FIO_VERIFY_SIZE:-256M}"
FIO_RUNTIME="${FIO_RUNTIME:-120}"
FIO_TESTDIR="${1:-"/testdir"}"

# Helper functions
_msg() {
	echo "${SELF}: $*" >&2
}

_die() {
	_msg "$*"
	exit 1
}

_run() {
	_msg "$*"
	( "$@" ) || _die "failed: $*"
}

# Run fio with basic workloads
_fio_simple() {
	local name="${FUNCNAME[1]}"

	# Run fio with json output format
	_run mkdir -p "${FIO_TESTDIR}/${name}"
	_run fio \
		--name="${name}" \
		--size="${FIO_SIZE}" \
		--directory="${FIO_TESTDIR}/${name}" \
		--runtime="${FIO_RUNTIME}" \
		--ioengine=pvsync2 \
		--group_reporting \
		--time_based \
		--sync=1 \
		--direct=0 \
		--rw=readwrite \
		--output-format=json \
		"$@"

	# Cleanup leftovers
	_run rm -rf "${FIO_TESTDIR}/${name}"
}

fio_simple_64k() {
	_fio_simple --bs=64K --numjobs=1
}

fio_simple_1m() {
	_fio_simple --bs=1M --numjobs=1
}

fio_simple_4jobs() {
	_fio_simple --bs=8K --numjobs=4
}

# Run fio with verify workloads
_fio_verify() {
	local name="${FUNCNAME[1]}"

	# Run fio in verify mode
	_run mkdir -p "${FIO_TESTDIR}/${name}"
	_run fio \
		--name="${name}" \
		--size="${FIO_VERIFY_SIZE}" \
		--directory="${FIO_TESTDIR}/${name}" \
		--ioengine=pvsync2 \
		--group_reporting \
		--sync=1 \
		--direct=0 \
		--rw=randwrite \
		--do_verify=1 \
		--verify_state_save=0 \
		--verify=xxhash \
		--output-format=json \
		"$@"

	# Cleanup leftovers
	_run rm -rf "${FIO_TESTDIR}/${name}"
}

fio_verify_64k() {
	_fio_verify --bs=64K --numjobs=1
}

fio_verify_1m() {
	_fio_verify --bs=1M --numjobs=1
}

fio_verify_4jobs() {
	_fio_verify --bs=64K --numjobs=4
}

fio_version() {
	_run fio --version
}

# Tests
fio_version
fio_simple_64k
fio_simple_1m
fio_simple_4jobs
fio_verify_64k
fio_verify_1m
fio_verify_4jobs

