import os
from pathlib import Path


def get_tmp_root(tmp_dir: Path = Path("/tmp")) -> Path:
    """
    Returns a temporary directory for use

    Parameters:
    tmp_dir: Temporary location to use. Set to "/tmp" by default

    Returns:
    tmp_root: Location of the temporary directory.
    """
    tmp_root = tmp_dir / str(os.getpid())
    i = 0
    while tmp_root.exists():
        tmp_root = tmp_root / str(i)
        i = i + 1
    tmp_root.mkdir()
    return tmp_root


def get_tmp_mount_point(tmp_root: Path) -> Path:
    """
    Return a mount point within the temporary directory

    Parameters:
    tmp_root: Directory in which to create mount point.

    Returns:
    mnt_point: Directory location in which you can mount a share.
    """
    i = 0
    mnt_point = tmp_root / str("mnt_" + str(i))
    while mnt_point.exists():
        i = i + 1
        mnt_point = tmp_root / str("mnt_" + str(i))
    mnt_point.mkdir()
    return mnt_point


def get_tmp_file(tmp_root: Path) -> Path:
    """
    Return a temporary file within the temporary directory

    Parameters:
    tmp_root: Directory in which to create temporary file.

    Returns:
    tmp_file: Location of temporary file.
    """
    i = 0
    tmp_file = tmp_root / str("tmp_file_" + str(i))
    while tmp_file.exists():
        i = i + 1
        tmp_file = tmp_root / str("tmp_file_" + str(i))
    tmp_file.touch()
    return tmp_file


def get_tmp_dir(tmp_root: Path) -> Path:
    """
    Return a temporary directory within the temporary directory

    Parameters:
    tmp_root: Directory in which to create temporary directory.

    Returns:
    tmp_dir: Location of temporary directory.
    """
    i = 0
    tmp_dir = tmp_root / str("tmp_dir_" + str(i))
    while tmp_dir.exists():
        i = i + 1
        tmp_dir = tmp_root / str("tmp_dir_" + str(i))
        tmp_dir.mkdir()
    return tmp_dir
