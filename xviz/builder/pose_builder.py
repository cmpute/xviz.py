
from easydict import EasyDict as edict

from xviz.builder.base_builder import XVIZBaseBuilder
from xviz.builder.validator import CATEGORY

class XVIZPoseBuilder(XVIZBaseBuilder):
    """
    # Reference
    [@xviz/builder/xviz-pose-builder]/(https://github.com/uber/xviz/blob/master/modules/builder/src/builders/xviz-pose-builder.js)
    """
    def __init__(self, metadata, validator):
        super().__init__(CATEGORY.POSE, metadata, validator)

        self._poses = None
        self.reset()

    def reset(self):
        super().reset()

        self._category = CATEGORY.POSE
        self._timestamp = None
        self._map_origin = None
        self._position = None
        self._orientation = None

    def map_origin(self, longitude, latitude, altitude):
        self._map_origin = dict(longitude=longitude, latitude=latitude, altitude=altitude)
        return self

    def position(self, x, y, z):
        self._position = [x, y, z]
        return self

    def orientation(self, roll, pitch, yaw):
        self._orientation = [roll, pitch, yaw]
        return self

    def timestamp(self, timestamp):
        self._timestamp = timestamp
        return self

    def _flush(self):
        if not self._poses:
            self._poses = {}

        data = dict(
            timestamp = self._timestamp,
            map_origin = self._map_origin,
            position = self._position,
            orientation = self._orientation,
        )
        self._poses[self._stream_id] = edict({k:v for k,v in data.items() if v})

    def get_data(self):
        if self._stream_id:
            self._flush()

        return edict(poses=self._poses)
