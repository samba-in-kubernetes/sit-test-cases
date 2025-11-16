#!/usr/bin/env bash
set -o nounset
set -o pipefail
export LC_ALL=C
unset CDPATH

# Global parameters
SELF=$(basename "${BASH_SOURCE[0]}")
TESTDIR="${1:-"/testdir"}"

# Helper functions
_msg() { echo "${SELF}: $*" >&2 ; }
_die() { _msg "$*" ; exit 1; }
_run() { _msg "$*"  ; ( "$@" ) || _die "failed: $*" ; }
_cdx() { _msg "cd $*" ; cd "$@" || _die "failed: cd $*" ; }

# Build CPython from source
_cdx "${TESTDIR}"
_run cp /src/cpython.tar.gz ./
_run tar xvfz cpython.tar.gz
_cdx cpython
_run ./configure
_run make

# Run a subset of CPython built-in tests
_run make test \
  TESTOPTS="-v test_io test_gzip test_bz2 test_fileutils test_filecmp test_dbm"

# Post-op cleanup
_cdx "${TESTDIR}"
_run rm -rf ./cpython*
_msg "CPython tests completed OK"
