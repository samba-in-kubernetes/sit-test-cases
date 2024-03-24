from smb.SMBConnection import SMBConnection  # type: ignore
import typing
import io


class SMBClient:
    """Use pysmb to access the SMB server"""

    def __init__(self, hostname: str, share: str, username: str, passwd: str):
        self.server = hostname
        self.share = share
        self.username = username
        self.password = passwd
        self.connect()

    def connect(self) -> None:
        self.ctx = SMBConnection(
            self.username,
            self.password,
            "smbclient",
            self.server,
            use_ntlm_v2=True,
        )
        self.ctx.connect(self.server)

    def disconnect(self) -> None:
        self.ctx.close()

    def readdir(self, path: str = "/") -> typing.List:
        return [dent.filename for dent in self.ctx.listPath(self.share, path)]

    def mkdir(self, dpath: str) -> None:
        self.ctx.createDirectory(self.share, dpath)

    def rmdir(self, dpath: str) -> None:
        self.ctx.deleteDirectory(self.share, dpath)

    def unlink(self, fpath: str) -> None:
        self.ctx.deleteFiles(self.share, fpath)

    def simple_write(self, fpath: str, teststr: str) -> None:
        file_obj = io.BytesIO(teststr.encode())
        self.ctx.storeFile(self.share, fpath, file_obj)

    def simple_read(self, fpath: str) -> str:
        readobj = io.BytesIO()
        self.ctx.retrieveFile(self.share, fpath, readobj)
        ret = readobj.getvalue().decode("ascii")
        readobj.close()
        return ret
