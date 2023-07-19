#!/usr/bin/env python3

# Run smbtorture tests

import testhelper
import sys
import os
import yaml
import pytest
import typing

script_root = os.path.dirname(os.path.realpath(__file__))
smbtorture_exec = "/bin/smbtorture"
filter_subunit_exec = (
    "/usr/bin/python3 " + script_root + "/selftest/filter-subunit"
)
format_subunit_exec = (
    "/usr/bin/python3 " + script_root + "/selftest/format-subunit"
)
smbtorture_tests_file = script_root + "/smbtorture-tests-info.yml"

test_info: typing.Dict[str, typing.Any] = {}
output = testhelper.get_tmp_file("/tmp")


def smbtorture(share_name: str, test: str, output: str) -> bool:
    mount_params = testhelper.get_mount_parameters(test_info, share_name)

    smbtorture_options_str = (
        "--fullname --option=torture:progress=no "
        + "--option=torture:sharedelay=100000 "
        + "--option=torture:writetimeupdatedelay=500000"
    )
    smbtorture_cmd = (
        "%s %s --format=subunit --target=samba3 --user=%s%%%s //%s/%s %s 2>&1"
        % (
            smbtorture_exec,
            smbtorture_options_str,
            mount_params["username"],
            mount_params["password"],
            mount_params["host"],
            mount_params["share"],
            test,
        )
    )

    filter_subunit_options_str = "--fail-on-empty --prefix='samba3.'"
    filter_subunit_filters = ""
    for filter in ["knownfail", "knownfail.d"]:
        filter_subunit_filters = (
            filter_subunit_filters
            + " --expected-failures="
            + script_root
            + "/selftest/"
            + filter
        )
    for filter in ["flapping", "flapping.d", "flapping.gluster"]:
        filter_subunit_filters = (
            filter_subunit_filters
            + " --flapping="
            + script_root
            + "/selftest/"
            + filter
        )

    filter_subunit_cmd = "%s %s %s" % (
        filter_subunit_exec,
        filter_subunit_options_str,
        filter_subunit_filters,
    )

    cmd = "%s|%s|/usr/bin/tee -a %s|%s >/dev/null" % (
        smbtorture_cmd,
        filter_subunit_cmd,
        output,
        format_subunit_exec,
    )

    with open(output, "w") as f:
        f.write("Command: " + cmd + "\n\n")

    ret = os.system(cmd)
    return ret == 0


def list_smbtorture_tests(test_info):
    with open(smbtorture_tests_file) as f:
        smbtorture_info = yaml.safe_load(f)
    return smbtorture_info


def generate_smbtorture_tests(
    test_info_file: typing.Optional[str],
) -> typing.List[typing.Tuple[str, str]]:
    global test_info
    if not test_info_file:
        return []
    test_info = testhelper.read_yaml(test_info_file)
    smbtorture_info = list_smbtorture_tests(test_info)
    arr = []
    for sharenum in range(testhelper.get_num_shares(test_info)):
        share_name = testhelper.get_share(test_info, sharenum)
        for torture_test in smbtorture_info:
            arr.append((share_name, torture_test))
    return arr


@pytest.mark.parametrize(
    "share_name,test", generate_smbtorture_tests(os.getenv("TEST_INFO_FILE"))
)
def test_smbtorture(share_name: str, test: str) -> bool:
    ret = smbtorture(share_name, test, output)
    if not ret:
        with open(output) as f:
            print(f.read())
        pytest.fail("Failure in running test - %s" % (test), pytrace=False)
    return True


if __name__ == "__main__":
    if len(sys.argv) != 2:
        print("Usage: %s <test-info.yml>" % (sys.argv[0]))
        exit(1)

    test_info_file = sys.argv[1]
    print("Running smbtorture test:")
    for share_name, test in generate_smbtorture_tests(test_info_file):
        print(share_name + " - " + test)
        test_smbtorture(share_name, test)
