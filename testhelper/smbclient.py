from smbprotocol.exceptions import SMBException  # type: ignore
import smbclient  # type: ignore
import typing

rw_chunk_size = 1 << 21  # 2MB


class SMBClient:
    """Use smbprotocol python module to access the SMB server"""

    def __init__(
        self,
        hostname: str,
        share: str,
        username: str,
        passwd: str,
        port: int = 445,
    ):
        self.server = hostname
        self.share = share
        self.port = port
        self.client_params = {
            "username": username,
            "password": passwd,
            "connection_cache": {},
        }
        self.prepath = f"\\\\{self.server}\\{self.share}\\"
        self.connected = False
        self.connect()

    def _path(self, path: str = "/") -> str:
        path.replace("/", "\\")
        return self.prepath + path

    def connect(self) -> None:
        if self.connected:
            return
        try:
            smbclient.register_session(
                self.server, port=self.port, **self.client_params
            )
            self.connected = True
        except SMBException as error:
            raise IOError(f"failed to connect: {error}")

    def disconnect(self) -> None:
        self.connected = False
        smbclient.reset_connection_cache(
            connection_cache=self.client_params["connection_cache"]
        )

    def _check_connected(self, action: str) -> None:
        if not self.connected:
            raise ConnectionError(f"{action}: server not connected")

    def listdir(self, path: str = "/") -> typing.List[str]:
        self._check_connected("listdir")
        try:
            filenames = smbclient.listdir(
                self._path(path), **self.client_params
            )
        except SMBException as error:
            raise IOError(f"listdir: {error}")
        return filenames

    def mkdir(self, dpath: str) -> None:
        self._check_connected("mkdir")
        if not self.connected:
            raise ConnectionError("listdir: server not connected")
        try:
            smbclient.mkdir(self._path(dpath), **self.client_params)
        except SMBException as error:
            raise IOError(f"mkdir: {error}")

    def rmdir(self, dpath: str) -> None:
        self._check_connected("rmdir")
        try:
            smbclient.rmdir(self._path(dpath), **self.client_params)
        except SMBException as error:
            raise IOError(f"rmdir: {error}")

    def unlink(self, fpath: str) -> None:
        self._check_connected("unlink")
        try:
            smbclient.remove(self._path(fpath), **self.client_params)
        except SMBException as error:
            raise IOError(f"unlink: {error}")

    def _read_write_fd(self, fd_from: typing.IO, fd_to: typing.IO) -> None:
        while True:
            data = fd_from.read(rw_chunk_size)
            if not data:
                break
            n = 0
            while n < len(data):
                n += fd_to.write(data[n:])

    def write(self, fpath: str, writeobj: typing.IO) -> None:
        self._check_connected("write")
        try:
            with smbclient.open_file(
                self._path(fpath), mode="wb", **self.client_params
            ) as fd:
                self._read_write_fd(writeobj, fd)
        except SMBException as error:
            raise IOError(f"write: {error}")

    def read(self, fpath: str, readobj: typing.IO) -> None:
        self._check_connected("read")
        try:
            with smbclient.open_file(
                self._path(fpath), mode="rb", **self.client_params
            ) as fd:
                self._read_write_fd(fd, readobj)
        except SMBException as error:
            raise IOError(f"write: {error}")

    def write_text(self, fpath: str, teststr: str) -> None:
        self._check_connected("write_text")
        try:
            with smbclient.open_file(
                self._path(fpath), mode="w", **self.client_params
            ) as fd:
                fd.write(teststr)
        except SMBException as error:
            raise IOError(f"write: {error}")

    def read_text(self, fpath: str) -> str:
        self._check_connected("read_text")
        try:
            with smbclient.open_file(
                self._path(fpath), **self.client_params
            ) as fd:
                ret = fd.read()
        except SMBException as error:
            raise IOError(f"write: {error}")
        return ret
