from .base import XVIZBaseWriter
from easydict import EasyDict
import base64
import numpy as np

class XVIZJsonWriter(XVIZBaseWriter):
    def __init__(self, sink, envelope=True, precision=10, as_array_buffer=False):
        super().__init__(sink)

        self.wrote_message_index = None
        self.options = EasyDict(envelope=envelope,
            precision=precision, as_array_buffer=as_array_buffer)

    def _save_timestamp(self, xviz_data, index):
        pass

    def write_metadata(self, xviz_metadata):
        self._check_valid()
        self._save_timestamp(xviz_metadata)

        if self.options.envelope:
            raise NotImplementedError() # TODO: implement envelope
        raise NotImplementedError() # TODO: continue
