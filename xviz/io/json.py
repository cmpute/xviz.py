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

    def convert_json(self, obj, key_name, nested_depth=0):
        '''
        This function recursively walk object performing the following conversions
        - primitives with typed array fields are turned into arrays
        - primtives of type image have the data turned into a base64 string

        Reference: @xviz/modules/io/src/writers/xviz-json-encoder.js
        '''
        if isinstance(obj, [list, tuple]):
            return [self.convert_json(item, key_name, nested_depth+1) for item in obj]

        if isinstance(obj, np.ndarray):
            if (not(key_name == "vertices" or key_name == "points") or nested_depth > 0):
                return obj.tolist()

            if len(obj) % 3 != 0:
                raise ValueError("TypeArray conversion failure. The array is expect to be divisible by 3")
            new_obj = []
            for i in range(len(obj) / 3):
                new_obj.append(new_obj[3*i:3*(i+1)])
            return new_obj

        if obj is not None:
            if hasattr(obj, 'data') and key_name == "images":
                obj.data = base64.b64encode(obj.data)
                return obj

            new_obj = {}
            for key in obj.keys:
                new_obj[key] = self.convert_json(obj[key], key)
            return new_obj

        return obj
