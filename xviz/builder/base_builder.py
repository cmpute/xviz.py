
class XVIZBaseBuilder:
    """
    # Reference
    [@xviz/builder/xviz-base-builder]/(https://github.com/uber/xviz/blob/master/modules/builder/src/builders/xviz-base-builder.js)
    """
    def __init__(self, category, metadata, validator):
        self._streamId = None
        self._category = category
        self._metadata = metadata
        self._validator = validator

    def stream(self, streamId):
        if self._streamId:
            self._flush()
        self._streamId = streamId
        return self

    @property
    def StreamId(self):
        return self._streamId
    @property
    def Category(self):
        return self._category
    @property
    def Metadata(self):
        return self._metadata

    def _flush(self):
        raise NotImplementedError("Derived class should implement this method")
    def reset(self):
        self._category = None

    def _validate(self):
        self._validator.hasProp(self, '_streamId')
        self._validator.hasProp(self, '_category')
        self._validator.matchMetadata(self)

    def validateWarn(self, msg):
        self._validator.warn(msg)
    def validateError(self, msg):
        self._validator.error(msg)
    def validatePropSetOnce(self, prop):
        self._validator.propSetOnce(self, prop)
