#
# A simple load test
#
# We use python threads to open up several consecutive connections
# on the SMB server and perform either open/write, open/read and delete
# operations with an interval of 0-0.5 seconds between each operation.
# The tests are run for  fixed duration of time before we stop and
# print out the stats for the number of operations performed
#


import testhelper
import random
import time
import threading
import typing
import pytest
import os


class SimpleLoadTest:
    """A helper class to generate a simple load on a SMB server"""

    instance_num = 0
    max_files = 10
    test_string = "ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz"

    def __init__(
        self,
        hostname: str,
        share: str,
        username: str,
        passwd: str,
        testdir: str,
    ):
        self.idnum = type(self).instance_num
        type(self).instance_num += 1
        self.testdir = testdir
        self.rootpath = f"{testdir}/test{self.idnum}"
        self.files: typing.List[str] = []
        self.thread = None
        self.run_test = False
        self.stats = {"read": 0, "open": 0, "delete": 0}
        self.scon = testhelper.SMBClient(hostname, share, username, passwd)

    def disconnect(self) -> None:
        del self.scon.ctx

    def _new_file(self) -> str:
        # Don't go above max_files
        if len(self.files) >= self.max_files:
            return ""
        file = "file" + str(random.randint(0, 1000))
        if file not in self.files:
            self.files.append(file)
            return f"{self.rootpath}/{file}"
        return self._new_file()

    def _get_file(self) -> str:
        if not self.files:
            return ""
        file = random.choice(self.files)
        return f"{self.rootpath}/{file}"

    def _del_file(self) -> str:
        if not self.files:
            return ""
        file = random.choice(self.files)
        self.files.remove(file)
        return f"{self.rootpath}/{file}"

    def _simple_run(self, op=""):
        if op == "":
            op = random.choice(["open", "read", "read", "read", "delete"])
        if op == "read":
            file = self._get_file()
            if not file:
                # If file doesn't exist, then run an open op first
                self._simple_run(op="open")
                return
            self.stats["read"] += 1
            self.scon.simple_read(file)
        elif op == "open":
            file = self._new_file()
            if not file:
                return
            self.stats["open"] += 1
            self.scon.simple_write(file, type(self).test_string)
        elif op == "delete":
            file = self._del_file()
            if not file:
                return
            self.stats["delete"] += 1
            self.scon.unlink(file)
        # sleep between 0-0.5 seconds between each op
        time.sleep(random.random() * 0.5)

    def _clean_up(self):
        for file in self.files:
            self.scon.unlink(f"{self.rootpath}/{file}")
        self.files = []

    def simple_load(self):
        self.scon.mkdir(self.rootpath)
        while self.run_test is True:
            self._simple_run()
        self._clean_up()
        self.scon.rmdir(self.rootpath)

    def start(self):
        self.run_test = True
        self.thread = threading.Thread(target=self.simple_load, args=())
        self.thread.start()

    def stop(self):
        self.run_test = False

    def cleanup(self):
        self.thread.join()
        self.disconnect()


class LoadTest:
    def __init__(
        self,
        hostname: str,
        share: str,
        username: str,
        passwd: str,
        testdir: str,
    ):
        self.server = hostname
        self.share = share
        self.username = username
        self.password = passwd
        self.testdir = testdir
        self.connections: typing.List[SimpleLoadTest] = []

    def get_connection_num(self) -> int:
        return len(self.connections)

    def set_connection_num(self, num: int) -> None:
        cn = self.get_connection_num()
        if cn < num:
            for _ in range(0, num - cn):
                self.connections.append(
                    SimpleLoadTest(
                        self.server,
                        self.share,
                        self.username,
                        self.password,
                        self.testdir,
                    )
                )
        elif cn >= num:
            for s in self.connections[num:]:
                s.disconnect()
            del self.connections[num:]

    def start_tests(self):
        for s in self.connections:
            s.start()

    def stop_tests(self):
        total_stats = {"open": 0, "read": 0, "delete": 0}
        for smbcon in self.connections:
            smbcon.stop()
        for smbcon in self.connections:
            smbcon.cleanup()
        for smbcon in self.connections:
            stats = smbcon.stats
            total_stats["open"] += stats["open"]
            total_stats["read"] += stats["read"]
            total_stats["delete"] += stats["delete"]
            print(
                f'{smbcon.idnum} - open: {stats["open"]} '
                f'read: {stats["read"]} delete: {stats["delete"]}'
            )
        print(
            f'Total - open: {total_stats["open"]} '
            f'read: {total_stats["read"]} delete: {total_stats["delete"]}'
        )


test_info_file = os.getenv("TEST_INFO_FILE")
test_info = testhelper.read_yaml(test_info_file)


def generate_loading_check() -> typing.List[tuple[str, str]]:
    arr = []
    for sharename in testhelper.get_exported_shares(test_info):
        share = testhelper.get_share(test_info, sharename)
        arr.append((share["server"], share["name"]))
    return arr


@pytest.mark.parametrize("hostname,sharename", generate_loading_check())
def test_loading(hostname: str, sharename: str) -> None:
    mount_params = testhelper.get_mount_parameters(test_info, sharename)
    testdir = "/loadtest"
    # Open a connection to create and finally remove the testdir
    smbcon = testhelper.SMBClient(
        hostname,
        mount_params["share"],
        mount_params["username"],
        mount_params["password"],
    )
    smbcon.mkdir(testdir)

    # Start load test
    loadtest = LoadTest(
        hostname,
        mount_params["share"],
        mount_params["username"],
        mount_params["password"],
        testdir,
    )
    # 100 consecutive connections
    loadtest.set_connection_num(100)
    loadtest.start_tests()
    # 30 seconds of runtime
    time.sleep(30)
    loadtest.stop_tests()
    # End load test

    smbcon.rmdir(testdir)
