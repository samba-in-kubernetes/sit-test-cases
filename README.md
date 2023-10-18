# Samba integration tests

The tests are part of the Samba Integrated testing project
[sit-environment](https://github.com/samba-in-kubernetes/sit-environment)
and are primarily used to test Samba servers exporting a clustered
filesystem such as cephfs, glusterfs and others.

### Prerequisite:
The tests are designed to run against any SMB server. The only
prerequisite is that we have a SMB server exporting a filesystem which
can be accessed over the network.
Refer:
- [Server setup](https://wiki.samba.org/index.php/Setting_up_Samba_as_a_Standalone_Server)
- [Filesystem export with glusterfs](https://wiki.samba.org/index.php/Samba_CTDB_GlusterFS_Cluster_HowTo)

### Quick guide on running the test-cases:
- Install sit-test-cases
  ```
      $ git clone https://github.com/samba-in-kubernetes/sit-test-cases.git
  ```

- Rename test-info.yml.example file under sit-test-cases to test-info.yml
  ```
      $ cd sit-test-cases
      $ mv test-info.example test-info.yml
  ```

- Update the relevant information in test-info.yml such as private and
  public interfaces, exported share names and test users and passwords from the
  previously set up samba server.

- Run make sanity_test to confirm the sanity of the setup before running the tests
  (Can be used whenever new set of changes are introduced in sit-test-cases):
  ```
      $ make sanity_test
  ```

- Run full test suite using make test:
  ```
      $ make test
  ```

- Run individual test cases(can be used for debugging):
  ```
      $ pwd
      /path/to/repo/sit-test-cases
      $ PYTHONPATH=`pwd` TEST_INFO_FILE=test-info.yml pytest -v testcases/smbtorture
  ```

NOTE:
- Some tests are performed against a share mounted using the cifs kernel module.
  This particular action requires root access.
