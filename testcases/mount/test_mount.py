#!/usr/bin/env python3

# Test mounts a cifs share, creates a new file on it, writes to it,
# deletes the file and unmounts

import testhelper
import os
import pytest
import typing
import shutil

from .mount_io import check_io_consistency
from .mount_dbm import check_dbm_consistency

test_info = os.getenv("TEST_INFO_FILE")
test_info_dict = testhelper.read_yaml(test_info)


def mount_check(ipaddr: str, share_name: str) -> None:
    mount_params = testhelper.get_mount_parameters(test_info_dict, share_name)
    mount_params["host"] = ipaddr
    tmp_root = testhelper.get_tmp_root()
    mount_point = testhelper.get_tmp_mount_point(tmp_root)
    flag_mounted = False
    try:
        testhelper.cifs_mount(mount_params, mount_point)
        flag_mounted = True
        test_dir = mount_point + "/mount_test"
        os.mkdir(test_dir)
        check_io_consistency(test_dir)
        check_dbm_consistency(test_dir)
    finally:
        if flag_mounted:
            shutil.rmtree(test_dir, ignore_errors=True)
            testhelper.cifs_umount(mount_point)
        os.rmdir(mount_point)
        os.rmdir(tmp_root)


def generate_mount_check(
    test_info_file: dict,
) -> typing.List[typing.Tuple[str, str]]:
    if not test_info_file:
        return []
    arr = []
    for ipaddr in test_info_file["public_interfaces"]:
        for share_name in test_info_file["exported_sharenames"]:
            arr.append((ipaddr, share_name))
    return arr


@pytest.mark.parametrize(
    "ipaddr,share_name", generate_mount_check(test_info_dict)
)
def test_mount(ipaddr: str, share_name: str) -> None:
    mount_check(ipaddr, share_name)
