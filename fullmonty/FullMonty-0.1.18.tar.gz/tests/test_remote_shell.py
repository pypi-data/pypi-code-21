# coding=utf-8

"""
Test the remote shell
"""
from fullmonty.local_shell import LocalShell
from fullmonty.remote_shell import RemoteShell


def test_remote_run():
    with LocalShell() as local:
        dir = local.run("pwd")
        local_ls = local.run("/bin/ls -l")
    with RemoteShell(user='wrighroy', password='yakityYak52', host='localhost') as remote:
        remote_ls = remote.run("/bin/ls -1 {dir}".format(dir=dir))
    assert local_ls == remote_ls
