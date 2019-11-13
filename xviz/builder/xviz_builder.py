import logging
from easydict import EasyDict as edict

from xviz.message import XVIZData
from xviz.builder.pose import XVIZPoseBuilder
from xviz.builder.primitive import XVIZPrimitiveBuilder
from xviz.builder.variable import XVIZVariableBuilder
from xviz.builder.ui_primitive import XVIZUIPrimitiveBuilder
from xviz.builder.time_series import XVIZTimeSeriesBuilder

from xviz.v2.core_pb2 import StreamSet
from google.protobuf.json_format import MessageToDict

PRIMARY_POSE_STREAM = '/vehicle_pose'

class XVIZBuilder:
    def __init__(self, metadata=None, disable_streams=None,
                 logger=logging.getLogger("xviz")):
        self._logger = logger
        self._metadata = metadata
        self._disable_streams = disable_streams or []
        self._stream_builder = None

        # self._links_builder = XVIZLinkBuilder(self._metadata, self._logger)
        self._pose_builder = XVIZPoseBuilder(self._metadata, self._logger)
        self._variables_builder = XVIZVariableBuilder(self._metadata, self._logger)
        self._primitives_builder = XVIZPrimitiveBuilder(self._metadata, self._logger)
        # self._future_instance_builder = XVIZFutureInstanceBuilder(self._metadata, self._logger)
        self._ui_primitives_builder = XVIZUIPrimitiveBuilder(self._metadata, self._logger)
        self._time_series_builder = XVIZTimeSeriesBuilder(self._metadata, self._logger)

    def pose(self, stream_id=PRIMARY_POSE_STREAM):
        self._stream_builder = self._pose_builder.stream(stream_id)
        return self._stream_builder

    def variable(self, stream_id):
        self._stream_builder = self._variables_builder.stream(stream_id)
        return self._stream_builder

    def primitive(self, stream_id):
        self._stream_builder = self._primitives_builder.stream(stream_id)
        return self._stream_builder

    def future_instance(self, stream_id, timestamp):
        pass

    def ui_primitives(self, stream_id):
        self._stream_builder = self._ui_primitives_builder.stream(stream_id)
        return self._stream_builder

    def time_series(self, stream_id):
        self._stream_builder = self._time_series_builder.stream(stream_id)
        return self._stream_builder

    def link(self, parent, child):
        pass

    def _reset(self):
        self._stream_builder = None

    def get_data(self):
        poses = self._pose_builder.get_data()
        if (not poses) or (PRIMARY_POSE_STREAM not in poses):
            self._logger.error('Every message requires a %s stream', PRIMARY_POSE_STREAM)

        data = XVIZData(StreamSet(
            timestamp=poses[PRIMARY_POSE_STREAM].timestamp, # FIXME: is timestamp required?
            poses=poses,
            primitives=self._primitives_builder.get_data(),
            # futures=self._future_instance_builder.get_data(),
            variables=self._variables_builder.get_data(),
            time_series=self._time_series_builder.get_data(),
            ui_primitives=self._ui_primitives_builder.get_data(),
            # links=self._link_builder.get_data()
        ))

        return data

    def get_message(self):

        message = dict( # TODO: return XVIZ message
            update_type='SNAPSHOT',
            updates=[self.get_data().to_object()] # TODO: pass raw data
        )
        return message
