#!/usr/bin/env python3

# This test first mounts a cifs share, creates a new file on it,
# writes to it, and unmounts the share, and then tests that it
# can get exactly the data written into the file through various
# possible ways of mounting the share (combinations of users and
# ip addresses).

import testhelper
import os, sys
import pytest

test_string = 'ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz'

# Use a global test_info to get a better output when running pytest
test_info = {}

def share_names(test_info):
    share_names = []
    for sharenum in range(testhelper.get_num_shares(test_info)):
        share_names.append(testhelper.get_share(test_info, sharenum))
    return share_names

def file_content_check(f, comp_str):
    read_data = f.read()
    return read_data == comp_str

def consistency_check(mount_point, share_name):
    mount_params = testhelper.get_mount_parameters(test_info, share_name)
    try:
        flag_share_mounted = 0
        flag_file_created = 0

        # The file write cycle
        testhelper.cifs_mount(mount_params, mount_point)
        flag_share_mounted = 1
        test_file = testhelper.get_tmp_file(mount_point)
        with open(test_file, 'w') as f:
            f.write(test_string)
        testhelper.cifs_umount(mount_point)
        flag_share_mounted = 0

        # The file read cycle
        testhelper.cifs_mount(mount_params, mount_point)
        flag_share_mounted = 1
        with open(test_file, 'r') as f:
            assert file_content_check(f, test_string), "File content does not match"
        os.unlink(test_file)
        testhelper.cifs_umount(mount_point)
        flag_share_mounted = 0

    except:
        print("Error while executing test")
        raise

    finally:
        if (flag_share_mounted == 1):
            testhelper.cifs_umount(mount_point)

def generate_consistency_check(test_info_file):
    global test_info
    if test_info_file == None:
        return []
    test_info = testhelper.read_yaml(test_info_file)
    arr = []
    for share_name in share_names(test_info):
        arr.append(share_name)
    return arr

@pytest.mark.parametrize("share_name", generate_consistency_check(os.getenv("TEST_INFO_FILE")))
def test_consistency(share_name):
    tmp_root = testhelper.get_tmp_root()
    mount_point = testhelper.get_tmp_mount_point(tmp_root)
    consistency_check(mount_point, share_name)
    os.rmdir(mount_point)
    os.rmdir(tmp_root)

if __name__ == "__main__":
    if (len(sys.argv) != 2):
        print("Usage: %s <test-info.yml>" % (sys.argv[0]))
        exit(1)
    test_info_file = sys.argv[1]
    tmp_root = testhelper.get_tmp_root()
    mount_point = testhelper.get_tmp_mount_point(tmp_root)
    print("Running consistency check:")
    for share_name in generate_consistency_check(test_info_file):
        print(share_name)
        consistency_check(mount_point, share_name)
    os.rmdir(mount_point)
    os.rmdir(tmp_root)

