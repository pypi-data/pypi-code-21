# coding=utf-8
try:
    from .gcs import GCSObjectStore, BackendGCSObjectStore
except ImportError:
    GCSObjectStore = None
    BackendGCSObjectStore = None

from .null_storage import NullObjectStore
