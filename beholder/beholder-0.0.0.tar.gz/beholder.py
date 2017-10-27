"""
A lightweight and easy to use folder watcher
"""
import time
import os

__version__ = '0.0.0'

class Directory:
    def __init__(self, folder):
        self.folder = folder
        self.cached_conts = set()
        self.cached_files = set()

    def cache_contents(self):
        for file in os.listdir(self.folder):
            file = self.folder + '\\' + file
            with open(file, 'rb') as _:
                self.cached_conts.add(file.encode() + _.read())

    def cache_files(self, ext=''):
        files = [file for file in os.listdir(self.folder) if file.endswith(ext)]
        self.cached_files = set(files)

def _change(dir1, dir2, wait):
    dir1.cache_contents()
    dir2.cache_contents()
    while dir1.cached_conts == dir2.cached_conts:
        dir1.cache_contents()
        time.sleep(wait)

def _new(dir1, dir2, wait, ext):
    dir1.cache_files(ext)
    dir2.cache_files(ext)
    while dir1.cached_files == dir2.cached_files:
        dir1.cache_files(ext)
        time.sleep(wait)

def watch_any(directory, wait=0.05):
    dir1 = Directory(directory)
    dir2 = Directory(directory)
    _change(dir1, dir2, wait)

def watch_new(directory, wait=0.05, ext=''):
    dir1 = Directory(directory)
    dir2 = Directory(directory)
    _new(dir1, dir2, wait, ext)

