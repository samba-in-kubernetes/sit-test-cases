#!/usr/bin/env python3
# Test various database operations via SMB mount-point.

import pytest
import dbm
import hashlib
import pickle
import shutil
import typing
import random
from pathlib import Path
from .conftest import gen_params, gen_params_premounted


class Record:
    def __init__(self, ikey: int) -> None:
        self.key = str(ikey)
        self.val = self._hashof(self.key)
        self.rnd = random.randint(0, 0x3FFFFFFF)

    def ikey(self) -> int:
        return int(self.key)

    def has_val_of(self, key: str) -> bool:
        return self.val == self._hashof(key)

    @staticmethod
    def _hashof(key: str) -> str:
        kh = hashlib.sha3_512(key.encode())
        return kh.hexdigest()


def _check_consistent(rec: Record) -> None:
    if not rec.has_val_of(rec.key):
        raise ValueError(f"not consistent: {rec.key} {rec.val}")


def _check_equal(rec1: Record, rec2: Record) -> None:
    if rec1.key != rec2.key:
        raise ValueError(f"key mismatch: {rec1.key} != {rec2.key}")
    if rec1.val != rec2.val:
        raise ValueError(f"value mismatch: {rec1.val} != {rec2.val}")
    if rec1.rnd != rec2.rnd:
        raise ValueError(f"random-tag mismatch: {rec1.rnd} != {rec2.rnd}")


class Database:
    def __init__(self, path: Path) -> None:
        self.path = path

    def create(self) -> None:
        self.db = dbm.open(str(self.path), flag="n", mode=0o600)

    def destroy(self):
        self.db.close()
        self.path.unlink()

    def store(self, recs: typing.List[Record]) -> None:
        for rec in recs:
            db_val = pickle.dumps(rec)
            self.db[rec.key] = db_val

    def query(self, recs: typing.List[Record]) -> None:
        for rec in recs:
            db_val = self.db.get(rec.key)
            rec2 = pickle.loads(db_val)  # type: ignore
            _check_consistent(rec2)
            _check_equal(rec, rec2)


def _make_records(ikeys: typing.Iterable[int]) -> typing.List[Record]:
    return [Record(ikey) for ikey in ikeys]


def _check_dbm_consistency(base: Path, nrecs: int) -> None:
    path = base / f"dbm-{nrecs}"
    recs1 = _make_records(range(0, int(nrecs / 2)))
    recs2 = _make_records(range(int(nrecs / 2), nrecs))
    recs = recs1 + recs2
    db = Database(path)
    db.create()
    try:
        db.store(recs1)
        db.query(recs1)
        random.shuffle(recs1)
        db.query(recs1)
        random.shuffle(recs2)
        db.store(recs2)
        db.query(recs)
    finally:
        db.destroy()


def _run_dbm_consistency_checks(base_path: Path) -> None:
    base_path.mkdir(exist_ok=True)
    try:
        _check_dbm_consistency(base_path, 10)
        _check_dbm_consistency(base_path, 100)
        _check_dbm_consistency(base_path, 10000)
    finally:
        shutil.rmtree(base_path, ignore_errors=True)


@pytest.mark.privileged
@pytest.mark.parametrize("setup_mount", gen_params(), indirect=True)
def test_dbm_consistency(setup_mount: Path) -> None:
    base = setup_mount / "dbm-consistency"
    _run_dbm_consistency_checks(base)


@pytest.mark.parametrize("test_dir", gen_params_premounted())
def test_dbm_consistency_premounted(test_dir: Path) -> None:
    base = test_dir / "dbm-consistency"
    _run_dbm_consistency_checks(base)
