import logging

from xviz.builder.validator import XVIZValidator
from xviz.builder.pose_builder import XVIZPoseBuilder
from xviz.builder.primitive_builder import XVIZPrimitiveBuilder

PRIMARY_POSE_STREAM = '/vehicle_pose'

class XVIZBuilder:
    def __init__(self, metadata=None, disableStreams=None,
                 logger=logging.getLogger("xviz")):
        self._validator = XVIZValidator(logger)
        self.metadata = metadata or {}
        self.disableStreams = disableStreams or []
        self._streamBuilder = None

        self._poseBuilder = XVIZPoseBuilder(self.metadata, self.validator)
        # self._variablesBuilder = XVIZVariableBuilder(self.metadata, self.validator)
        self._primitivesBuilder = XVIZPrimitiveBuilder(self.metadata, self.validator)
        # self._futureInstanceBuilder = XVIZFutureInstanceBuilder(self.metadata, self._validator)
        # self._uiPrimitivesBuilder = XVIZUIPrimitiveBuilder(self.metadata, self.validator)
        # self._timeSeriesBuilder = XVIZTimeSeriesBuilder(self.metadata, self.validator)

    def pose(self, streamId=PRIMARY_POSE_STREAM):
        self._streamBuilder = self._poseBuilder.stream(streamId)
        return self._streamBuilder

    def variable(self, streamId):
        pass

    def primitive(self, streamId):
        pass

    def futureInstance(self, streamId, timestamp):
        pass

    def uiPrimitives(self, streamId):
        pass

    def timeSeries(self, streamId):
        pass

    def getMessage(self):
        pass

    def _reset(self):
        self._streamBuilder = None

    def getData(self):
        pass
        
