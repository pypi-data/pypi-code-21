# coding=utf-8
"""
test LocalShell
"""
import Queue
import multiprocessing
from threading import Thread

from multiprocessing import Process

from fullmonty.local_shell import LocalShell


CMD_LINE = 'pwd'


def test_local_shell():
    """ test normal LocalShell usage """
    with LocalShell() as local:
        result = local.run(CMD_LINE)
        assert result


def test_local_shell_no_signal():
    """ test with signal usage diabled """
    with LocalShell() as local:
        result = local.run(CMD_LINE, use_signals=False)
        assert result


def test_local_shell_multitheaded():
    """ test using threads """

    N_ATTEMPTS = 100

    q = Queue.Queue()

    def get_pwd(q):
        with LocalShell() as local:
            result_ = local.run(CMD_LINE, use_signals=False)
            q.put(result_)

    threads = []
    for i in range(0, N_ATTEMPTS):
        thread = Thread(target=get_pwd, args=(q,))
        threads.append(thread)
        thread.start()

    for thread in threads:
        thread.join()

    count = 0
    while not q.empty():
        count += 1
        results = q.get()
        for result in results:
            assert result

    assert count == N_ATTEMPTS


def test_local_shell_multiprocess():
    """ test using processes """
    N_ATTEMPTS = 100

    q = multiprocessing.Queue()

    def get_pwd(q):
        with LocalShell() as local:
            result_ = local.run(CMD_LINE, use_signals=False)
            q.put(result_)

    processes = []
    for i in range(0, N_ATTEMPTS):
        process = Process(target=get_pwd, args=(q,))
        processes.append(process)
        process.start()

    for process in processes:
        process.join()

    count = 0
    while not q.empty():
        count += 1
        results = q.get()
        for result in results:
            assert result

    assert count == N_ATTEMPTS
