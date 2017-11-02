# content of test_sample.py
import rocksdb_iota
import pytest
import shutil
import os


def clean_db():
    if os.path.exists('/tmp/test'):
        shutil.rmtree("/tmp/test")

def test_open_skiplist_memtable_factory():
    clean_db()
    opts = rocksdb_iota.Options()
    opts.memtable_factory = rocksdb_iota.SkipListMemtableFactory()
    opts.create_if_missing = True
    test_db = rocksdb_iota.DB("/tmp/test", opts)

def test_open_vector_memtable_factory():
    clean_db()
    opts = rocksdb_iota.Options()
    opts.allow_concurrent_memtable_write = False
    opts.memtable_factory = rocksdb_iota.VectorMemtableFactory()
    opts.create_if_missing = True
    test_db = rocksdb_iota.DB("/tmp/test", opts)
