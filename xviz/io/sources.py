'''
This module contains `sources` that can read and write data from certain source by key-value strategy.
Here the source is the combine definition of `source` and `sink` as from xviz JS library.
'''
import os
import io
from collections import defaultdict

class BaseSource:
    def __init__(self):
        pass

    def open(self, name, mode='r'):
        raise NotImplementedError("Derived class should implement this method")

    def read(self, name):
        raise NotImplementedError("Derived class should implement this method")

    def write(self, data, name):
        raise NotImplementedError("Derived class should implement this method")

class DirectorySource:
    def __init__(self, directory):
        self._dir = directory
        assert os.path.isdir(self._dir)

    def open(self, name, mode='r'):
        fpath = os.path.join(self._dir, name)
        if mode == 'r':
            return open(fpath, 'rb')
        elif mode == 'w':
            return open(fpath, 'wb')

    def read(self, name):
        with open(os.path.join(self._dir, name), 'rb') as fin:
            return fin.read()

    def write(self, data, name):
        with open(os.path.join(self._dir, name), 'wb') as fout:
            fout.write(fout, data)

    def close(self):
        pass

class ZipSource:
    pass

class MemorySource:
    def __init__(self, latest_only=False):
        self._latest_only = latest_only
        if latest_only:
            self._data = io.BytesIO()
        else:
            self._data = defaultdict(io.BytesIO)

    def open(self, name, mode=None):
        if self._latest_only:
            return self._data
        else:
            return self._data[name]

    def read(self, name=None):
        if self._latest_only:
            self._data.seek(0)
            return self._data.read()
        else:
            self._data[name].seek(0)
            return self._data[name].read()

    def write(self, data, name=None):
        if self._latest_only:
            self._data = io.BytesIO()
            self._data.write(data)
        else:
            self._data[name].write(data)

    def close(self):
        if self._latest_only:
            self._data.close()
        else:
            for value in self._data.values():
                value.close()

class SQLiteSource:
    pass
