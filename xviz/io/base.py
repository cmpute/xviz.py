
class XVIZBaseWriter:
    def __init__(self, source):
        '''
        :param sink: object of type in xviz.io.sources
        '''
        if source is None:
            raise ValueError("Data source must be specified!")
        self._source = source

    def close(self):
        if self._source:
            self._source.close()
            self._source = None

    def _check_valid(self):
        if not self._source:
            raise ValueError("The writer has been closed!")

class XVIZBaseReader:
    def __init__(self, source):
        pass
