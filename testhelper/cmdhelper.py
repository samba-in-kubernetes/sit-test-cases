import os
import subprocess
import typing


def cifs_mount(
    mount_params: typing.Dict[str, str], mount_point: str, opts: str = ""
) -> int:
    """Use the cifs module to mount a share.

    Parameters:
    mount_params: Dict containing mount parameters
    mount_point: Directory location to mount the share.
    opts: Additional options to pass to the mount command

    Returns:
    int: return value of the mount command.
    """

    if not opts:
        mount_options = (
            "username="
            + mount_params["username"]
            + ",password="
            + mount_params["password"]
        )
    else:
        mount_options = (
            opts
            + ",username="
            + mount_params["username"]
            + ",password="
            + mount_params["password"]
        )
    share = "//" + mount_params["host"] + "/" + mount_params["share"]
    cmd = "mount -t cifs -o " + mount_options + " " + share + " " + mount_point
    ret = os.system(cmd)
    assert ret == 0, "Error mounting: ret %d cmd: %s\n" % (ret, cmd)
    return ret


def cifs_umount(mount_point: str) -> int:
    """Unmount a mounted filesystem.

    Parameters:
    mount_point: Directory of the mount point.

    Returns:
    int: return value of the umount command.
    """
    cmd = "umount -fl %s" % (mount_point)
    ret = os.system(cmd)
    assert ret == 0, "Error mounting: ret %d cmd: %s\n" % (ret, cmd)
    return ret


def smbclient(
    mount_params: typing.Dict[str, str], cmds: str
) -> typing.Tuple[int, str]:
    """Run the following command on smbclient and return the output.

    Parameters:
    mount_params: Dict containing the mount parameters.
    cmds: String containg the ';' separated commands to run.

    Returns:
    int: Return value from the shell execution
    string: stdout
    """
    smbclient_cmd = [
        "smbclient",
        "--user=%s%%%s" % (mount_params["username"], mount_params["password"]),
        "//%s/%s" % (mount_params["host"], mount_params["share"]),
        "-c",
        cmds,
    ]
    ret = subprocess.run(
        smbclient_cmd,
        universal_newlines=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
    )
    return (ret.returncode, ret.stdout)
