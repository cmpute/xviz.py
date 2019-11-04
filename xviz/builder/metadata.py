import logging
from easydict import EasyDict as edict
import numpy as np

from .validator import CATEGORY, XVIZValidator

class XVIZMetadataBuilder:
    def __init__(self, logger=logging.getLogger("xviz")):
        self._validator = XVIZValidator(logger)

        self._data = edict(streams=edict())
        self._stream_id = None
        self._tmp_ui_builder = None
        self._tmp_stream = edict()
        self._tmp_matrix_transform = None
        self._tmp_pose_transform = None
        self._tmp_log_info = edict()
        self._tmp_type = None

    def get_metadata(self):
        self._flush()
        
        metadata = edict(version="2.0.0", **self._data)

        if len(self._tmp_log_info.keys()) > 0:
            metadata.log_info = self._tmp_log_info
        if self._tmp_ui_builder:
            panels = self._tmp_ui_builder.get_ui()
            metadata.ui_config = edict()

            for panel_key in panels.keys():
                metadata.ui_config = edict(
                    name=panels[panel_key].name,
                    config=panels[panel_key]
                )
        return metadata

    def start_time(self, time):
        self._tmp_log_info.start_time = time
        return self

    def end_time(self, time):
        self._tmp_log_info.end_time = time
        return self

    def ui(self, ui_builder):
        self._tmp_ui_builder = ui_builder
        return self

    def stream(self, stream_id):
        if self._stream_id:
            self._flush()

        self._stream_id = stream_id
        return self

    # Used for validation in XVIZBuilder
    def category(self, category):
        self._tmp_stream.category = category.upper()
        return self

    # Used for validation in XVIZBuilder
    def type(self, t):
        self._tmp_type = t.upper()
        return self

    def source(self, source):
        self._tmp_stream.source = source
        return self

    def unit(self, u):
        self._tmp_stream.units = u
        return self

    def coordinate(self, coordinate):
        self._tmp_stream.coordinate = coordinate
        return self

    def transform_matrix(self, matrix):
        if isinstance(matrix, list):
            matrix = np.array(matrix)

        self._tmp_matrix_transform = matrix
        return self

    def pose(self, position={}, orientation={}):
        raise NotImplementedError() # TODO: implement transformation

    def stream_style(self, style):
        self._tmp_stream.stream_style = style
        return self

    def style_class(self, name, style):
        if not self._stream_id:
            self._validator.error('A stream must set before adding a style rule.')
            return self

        stream_rule = edict(name=name, style=style)
        if 'style_classes' not in self._tmp_stream:
            self._tmp_stream.style_classes = [stream_rule]
        else:
            self._tmp_stream.style_classes.append(stream_rule)
        return self

    def log_info(self, data):
        self._tmp_log_info.data = data
        return self

    def _flush(self):
        if self._stream_id:
            stream_data = self._tmp_stream

            transform = None
            if self._tmp_pose_transform and self._tmp_matrix_transform:
                self._validator.error('`pose` and `transformMatrix` cannot be applied at the same time.')
            else:
                transform = self._tmp_matrix_transform or self._tmp_pose_transform

            if transform:
                stream_data.transform = transform

            if "category" not in stream_data:
                stream_data.category = None
            if stream_data.category not in [CATEGORY.PRIMITIVE, CATEGORY.FUTURE_INSTANCE]:
                stream_data.primitive_type = self._tmp_type
            elif stream_data.category not in [CATEGORY.VARIABLE, CATEGORY.TIME_SERIES]:
                stream_data.scalar_type = self._tmp_type
            else:
                stream_data.scalar_type = self._tmp_type

            self._data.streams[self._stream_id] = stream_data
        
        self._reset()

    def _reset(self):
        self._stream_id = None
        self._tmp_stream = edict()
        self._tmp_matrix_transform = None
        self._tmp_pose_transform = None
        self._tmp_type = None
