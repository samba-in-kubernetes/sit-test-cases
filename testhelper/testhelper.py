import os
import yaml
import typing
import random
from pathlib import Path


def read_yaml():
    """Returns a dict containing the contents of the yaml file.

    Returns:
    dict: The parsed test information yml as a dictionary.
    """
    with open(os.getenv("TEST_INFO_FILE")) as f:
        test_info = yaml.load(f, Loader=yaml.FullLoader)
    return test_info


test_info = read_yaml()


def gen_mount_params(
    host: str, share: str, username: str, password: str
) -> typing.Dict[str, str]:
    """Generate a dict of parameters required to mount a SMB share.

    Parameters:
    host: hostname
    share: exported share name
    username: username
    password: password for the user

    Returns:
    dict: mount parameters in a dict
    """
    ret = {
        "host": host,
        "share": share,
        "username": username,
        "password": password,
    }
    return ret


def get_mount_parameters(share: str) -> typing.Dict[str, str]:
    """Get the default mount_params dict for a given share

    Parameters:
    share: The share for which to get the mount_point
    """
    return gen_mount_params(
        test_info["public_interfaces"][0],
        share,
        test_info["test_users"][0]["username"],
        test_info["test_users"][0]["password"],
    )


def generate_random_bytes(size: int) -> bytes:
    """
    Creates sequence of semi-random bytes.

    A wrapper over standard 'random.randbytes()' which should be used in
    cases where caller wants to avoid exhausting of host's random pool (which
    may also yield high CPU usage). Uses an existing random bytes-array to
    re-construct a new one, double in size, plus up-to 1K of newly random
    bytes. This method creats only "pseudo" (or "semi") random bytes instead
    of true random bytes-sequence, which should be good enough for I/O
    integrity testings.
    """
    rba = bytearray(random.randbytes(min(size, 1024)))
    while len(rba) < size:
        rem = size - len(rba)
        rnd = bytearray(random.randbytes(min(rem, 1024)))
        rba = rba + rnd + rba
    return rba[:size]


def get_premounted_shares() -> typing.List[Path]:
    """
    Get list of premounted shares

    Parameters:
    None
    Returns:
    list of paths with shares
    """
    premounted_shares = test_info.get("premounted_shares", [])
    return [Path(mnt) for mnt in premounted_shares]


def generate_consistency_check() -> typing.List[typing.Tuple[str, str]]:
    arr = []
    for ipaddr in test_info["public_interfaces"]:
        for share_name in test_info["exported_sharenames"]:
            arr.append((ipaddr, share_name))
    return arr


def generate_mount_check() -> typing.List[typing.Tuple[str, str]]:
    public_interfaces = test_info.get("public_interfaces", [])
    exported_sharenames = test_info.get("exported_sharenames", [])
    arr = []
    for ipaddr in public_interfaces:
        for share_name in exported_sharenames:
            arr.append((ipaddr, share_name))
    return arr
