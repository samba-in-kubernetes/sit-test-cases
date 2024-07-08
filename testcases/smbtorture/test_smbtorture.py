#!/usr/bin/env python3

# Run smbtorture tests

import testhelper
import os
import yaml
import pytest
import typing
import subprocess
from pathlib import Path

script_root = os.path.dirname(os.path.realpath(__file__))
smbtorture_exec = "/bin/smbtorture"
selftest_dir = script_root + "/selftest"
filter_subunit_exec = selftest_dir + "/filter-subunit"
format_subunit_exec = selftest_dir + "/format-subunit"
smbtorture_tests_file = script_root + "/smbtorture-tests-info.yml"

test_info_file = os.getenv("TEST_INFO_FILE")
test_info = testhelper.read_yaml(test_info_file)


def flapping_file(backend: str, variant: str = "") -> str:
    file = "flapping." + backend
    if variant and variant != "default":
        file_variant = f"{file}-{variant}"
        if os.path.exists(os.path.join(selftest_dir, file_variant)):
            return file_variant
    if os.path.exists(os.path.join(selftest_dir, file)):
        return file
    return ""


def smbtorture(share_name: str, test: str, tmp_output: Path) -> bool:
    # build smbtorture command
    mount_params = testhelper.get_mount_parameters(test_info, share_name)
    smbtorture_cmd = [
        smbtorture_exec,
        "--fullname",
        "--option=torture:progress=no",
        "--option=torture:sharedelay=100000",
        "--option=torture:writetimeupdatedelay=500000",
        "--format=subunit",
        "--target=samba3",
        "--user=%s%%%s" % (mount_params["username"], mount_params["password"]),
        "//%s/%s" % (mount_params["host"], mount_params["share"]),
        test,
    ]

    # build filter-subunit commands
    filter_subunit_cmd = [
        "/usr/bin/python3",
        filter_subunit_exec,
        "--fail-on-empty",
        "--prefix=samba3.",
    ]
    for filter in ["knownfail", "knownfail.d", "expectedfail.d"]:
        filter_subunit_cmd.append(
            "--expected-failures=" + script_root + "/selftest/" + filter
        )
    flapping_list = ["flapping", "flapping.d"]
    share = testhelper.get_share(test_info, share_name)
    test_backend = share["backend"].get("name")
    test_backend_variant = share["backend"].get("variant")
    if test_backend is not None:
        file = flapping_file(test_backend, test_backend_variant)
        if file is not None:
            flapping_list.append(file)
    for filter in flapping_list:
        filter_subunit_cmd.append(
            "--flapping=" + script_root + "/selftest/" + filter
        )

    # build format-subunit commands
    format_subunit_cmd = ["/usr/bin/python3", format_subunit_exec]

    # run commands - smbtorture
    smbtorturec = subprocess.Popen(
        smbtorture_cmd, stderr=subprocess.STDOUT, stdout=subprocess.PIPE
    )
    assert smbtorturec.stdout is not None

    # run commands - filter_subunit
    with open(tmp_output, "w") as filter_subunit_stdout:
        filter_subunitc = subprocess.Popen(
            filter_subunit_cmd,
            stdout=filter_subunit_stdout,
            stdin=smbtorturec.stdout,
        )
        smbtorturec.stdout.close()
        filter_subunitc.communicate()

    # run commands - format_subunit
    with open(tmp_output, "r") as filter_subunit_stdout:
        format_subunitc = subprocess.run(
            format_subunit_cmd,
            stdin=filter_subunit_stdout,
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
            universal_newlines=True,
        )

    # print the commands as they will be run.
    cmd = "%s|%s|%s" % (
        " ".join(smbtorture_cmd),
        " ".join(filter_subunit_cmd),
        " ".join(format_subunit_cmd),
    )
    print("Command: " + cmd + "\n\n")
    # Print the intermediate output
    with open(tmp_output, "r") as filter_subunit_stdout:
        print(filter_subunit_stdout.read())
    print("\n" + format_subunitc.stdout)

    return format_subunitc.returncode == 0


def list_smbtorture_tests():
    with open(smbtorture_tests_file) as f:
        smbtorture_info = yaml.safe_load(f)
    return smbtorture_info


def generate_smbtorture_tests() -> typing.List[typing.Tuple[str, str]]:
    smbtorture_info = list_smbtorture_tests()
    arr = []
    for share_name in testhelper.get_exported_shares(test_info):
        for torture_test in smbtorture_info:
            arr.append((share_name, torture_test))
    return arr


@pytest.mark.parametrize("share_name,test", generate_smbtorture_tests())
def test_smbtorture(share_name: str, test: str) -> None:
    output = testhelper.get_tmp_file()
    ret = smbtorture(share_name, test, output)
    if os.path.exists(output):
        os.unlink(output)
    if not ret:
        pytest.fail("Failure in running test - %s" % (test), pytrace=False)
