import logging
from easydict import EasyDict as edict

from xviz.builder.validator import XVIZValidator
from xviz.builder.pose_builder import XVIZPoseBuilder
from xviz.builder.primitive_builder import XVIZPrimitiveBuilder

PRIMARY_POSE_STREAM = '/vehicle_pose'

class XVIZBuilder:
    def __init__(self, metadata=None, disable_streams=None,
                 logger=logging.getLogger("xviz")):
        self._validator = XVIZValidator(logger)
        self.metadata = metadata or {}
        self.disable_streams = disable_streams or []
        self._stream_builder = None

        self._pose_builder = XVIZPoseBuilder(self.metadata, self._validator)
        # self._variables_builder = XVIZVariableBuilder(self.metadata, self._validator)
        self._primitives_builder = XVIZPrimitiveBuilder(self.metadata, self._validator)
        # self._future_instance_builder = XVIZFutureInstanceBuilder(self.metadata, self._validator)
        # self._ui_primitives_builder = XVIZUIPrimitiveBuilder(self.metadata, self._validator)
        # self._time_series_builder = XVIZTimeSeriesBuilder(self.metadata, self._validator)

    def pose(self, stream_id=PRIMARY_POSE_STREAM):
        self._stream_builder = self._pose_builder.stream(stream_id)
        return self._stream_builder

    def variable(self, stream_id):
        pass

    def primitive(self, stream_id):
        self._stream_builder = self._primitives_builder.stream(stream_id)
        return self._stream_builder

    def futureInstance(self, stream_id, timestamp):
        pass

    def uiPrimitives(self, stream_id):
        pass

    def timeSeries(self, stream_id):
        pass

    def getMessage(self):
        pass

    def _reset(self):
        self._stream_builder = None

    def get_message(self):
        poses = self._pose_builder.get_data().poses
        print(poses)
        if (not poses) or (PRIMARY_POSE_STREAM not in poses):
            self._validator.error('Every message requires a %s stream' % PRIMARY_POSE_STREAM)

        data = dict(
            timestamp = poses[PRIMARY_POSE_STREAM].timestamp, # TODO: is timestamp required?
            poses = poses,
            primitives = self._primitives_builder.get_data(),
            # futures = self._future_instance_builder.get_data(),
            # variables = self._variables_builder.get_data(),
            # time_series = self._time_series_builder.get_data(),
            # ui_primitives = self._ui_primitives_builder.get_data(),
        )
        data = edict({k:v for k,v in data.items() if v})

        message = dict(
            update_type = 'SNAPSHOT',
            updates = [data]
        )

        return message
