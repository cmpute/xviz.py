
class XVIZBaseBuilder:
    """
    # Reference
    [@xviz/builder/xviz-base-builder]/(https://github.com/uber/xviz/blob/master/modules/builder/src/builders/xviz-base-builder.js)
    """
    def __init__(self, category, metadata, validator):
        self._stream_id = None
        self._category = category
        self._metadata = metadata
        self._validator = validator

    def stream(self, stream_id):
        if self._stream_id:
            self._flush()
        self._stream_id = stream_id
        return self

    @property
    def stream_id(self):
        return self._stream_id
    @property
    def category(self):
        return self._category
    @property
    def metadata(self):
        return self._metadata

    def _flush(self):
        raise NotImplementedError("Derived class should implement this method")
    def reset(self):
        self._category = None

    def _validate(self):
        self._validator.has_prop(self, '_stream_id')
        self._validator.has_prop(self, '_category')
        self._validator.match_metadata(self)

    def validate_warn(self, msg):
        self._validator.warn(msg)
    def validate_error(self, msg):
        self._validator.error(msg)
    def validate_prop_set_once(self, prop):
        self._validator.prop_set_once(self, prop)
