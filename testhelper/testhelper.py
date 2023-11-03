import yaml
import typing
import random
from pathlib import Path


def read_yaml(test_info):
    """Returns a dict containing the contents of the yaml file.

    Parameters:
    test_info: filename of yaml file.

    Returns:
    dict: The parsed test information yml as a dictionary.
    """
    with open(test_info) as f:
        test_info = yaml.load(f, Loader=yaml.FullLoader)
    return test_info


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


def get_default_mount_params(test_info: dict) -> typing.Dict[str, str]:
    """Pass a dict of type mount_params containing the first parameters to
    mount the share.

    Parameters:
    test_info: Dict containing the parsed yaml file.

    Returns:
    Dict: of type mount_params containing the parameters to mount the share.
    """
    return gen_mount_params(
        test_info["public_interfaces"][0],
        test_info["exported_sharenames"][0],
        test_info["test_users"][0]["username"],
        test_info["test_users"][0]["password"],
    )


def get_total_mount_parameter_combinations(test_info: dict) -> int:
    """Get total number of combinations of mount parameters for each share.
    This is essentially "number of public  interfaces * number of test users"

    Parameters:
    test_info: Dict containing the parsed yaml file.

    Returns:
    int: number of possible combinations.
    """
    return len(test_info["public_interfaces"]) * len(test_info["test_users"])


def get_mount_parameters(
    test_info: dict, share: str, combonum: int = 0
) -> typing.Dict[str, str]:
    """Get the mount_params dict for a given share and given combination number

    Parameters:
    test_info: Dict containing the parsed yaml file.
    share: The share for which to get the mount_params
    combonum: The combination number to use.
    """
    if combonum >= get_total_mount_parameter_combinations(test_info):
        assert False, "Invalid combination number"
    num_public = int(combonum / len(test_info["test_users"]))
    num_users = combonum % len(test_info["test_users"])
    return gen_mount_params(
        test_info["public_interfaces"][num_public],
        share,
        test_info["test_users"][num_users]["username"],
        test_info["test_users"][num_users]["password"],
    )


def get_num_shares(test_info: dict) -> int:
    """Get number of exported shares

    Parameters:
    test_info: Dict containing the parsed yml file.

    Returns:
    int: number of exported shares
    """
    return len(test_info["exported_sharenames"])


def get_share(test_info: dict, share_num: int) -> str:
    """Get exported share name

    Parameters:
    test_info: Dict containing the parsed yml file.
    share_num: The index within the exported sharenames list

    Returns:
    str: exported sharename at index share_num
    """
    return test_info["exported_sharenames"][share_num]


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


def get_premounted_shares(test_info: dict) -> typing.List[Path]:
    """
    Get list of premounted shares

    Parameters:
    None
    Returns:
    list of paths with shares
    """
    premounted_shares = test_info.get("premounted_shares", [])
    return [Path(mnt) for mnt in premounted_shares]
