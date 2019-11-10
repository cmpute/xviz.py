'''
This module contains `sources` that can read and write data from certain source by key-value strategy.
Here the source is the combine definition of `source` and `sink` as from xviz JS library.
'''
import os

class DirectorySource:
    def __init__(self, directory):
        self._dir = directory
        assert os.path.isdir(self._dir)

    def read(self, name):
        fin = open(os.path.join(self._dir, name), 'r')
        return fin

    def write(self, name, data):
        with open(os.path.join(self._dir, name), 'w') as fout:
            fout.write(fout, data)

    def close(self):
        pass

class ZipSource:
    pass

class MemorySource:
    pass

class SQLiteSource:
    pass
