import json
from .base import XVIZBaseWriter

from xviz.message import XVIZEnvelope, XVIZMessage, Metadata

class XVIZJsonWriter(XVIZBaseWriter):
    def __init__(self, sink, wrap_envelope=True, float_precision=10, as_array_buffer=False):
        super().__init__(sink)
        self._wrap_envelop = wrap_envelope
        self._json_precision = float_precision
        self._counter = 2

    def write_message(self, message: XVIZMessage, index: int = None):
        self._check_valid()
        if self._wrap_envelop:
            obj = XVIZEnvelope(message).to_object()
        else:
            obj = message.to_object()

        # Process necessary information
        if isinstance(message.data, Metadata):
            self._save_timestamp(message.data)
            fname = "1-frame.glb"
        else:
            if not index:
                index = self._counter
                self._counter += 1

            self._save_timestamp(message.data, index)
            fname = "%d-frame.glb" % index

        # Encode GLB into file
        result = [] # These codes are for float truncation
        for part in json.JSONEncoder(separators=(',', ':')).iterencode(obj):
            try:
                rounded = round(float(part), self._json_precision)
            except ValueError:
                pass
            else: part = str(rounded)
            result.append(part)
        self._source.write(''.join(result).encode('ascii'), fname)
