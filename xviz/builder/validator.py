
import logging

from xviz.builder.base_builder import PRIMITIVE_STYLE_MAP

# TODO: Integrate XVIZValidator into base builder
class XVIZValidator:
    """
    # Reference
    [@xviz/builder/xviz-validator]/(https://github.com/uber/xviz/blob/master/modules/builder/src/builders/xviz-validator.js)
    """
    def __init__(self, logger=logging.getLogger("xviz")):
        self._logger = logger

    def warn(self, msg):
        self._logger.warning(msg)

    def error(self, msg):
        self._logger.error(msg)
        raise ValueError("Error triggered: " + msg)

    def has_prop(self, builder, prop, msg=None):
        if hasattr(builder, prop):
            return
        self._logger.warn(msg or "Stream {}: {} is missing"\
            .format(builder.stream_id, prop))

    def prop_set_once(self, builder, prop, msg=None):
        if not hasattr(builder, prop):
            return
        val = getattr(builder, prop)
        if not val:
            return
        if isinstance(val, list) and len(val) == 0:
            return

        self._logger.warn(msg or "Stream {}: {} has been already set."\
            .format(builder.stream_id, prop))

    def match_metadata(self, builder):
        metadata = builder.metadata
        stream_id = builder.stream_id
        category = builder.category

        if metadata and hasattr(metadata, "streams"):
            stream_metadata = metadata.streams[stream_id]
            if not stream_metadata:
                self._logger.warning("{} is not defined in metadata.".format(stream_id))
            elif category != metadata.category:
                self._logger.warning("Stream {} category '{}' does not match metadata definition ({})."\
                    .format(stream_id, category, stream_metadata.category))

    def validateStyle(self, builder):
        properties = builder._style.keys()
        if builder._type in PRIMITIVE_STYLE_MAP.keys():
            validProperties = PRIMITIVE_STYLE_MAP[builder._type]
            invalidProps = [prop for prop in properties if prop not in validProperties]
            if len(invalidProps) > 0:
                self.warn("Invalid style properties {} for stream {}".format(
                    ','.join(invalidProps), builder.stream_id))
        else:
            self.warn("Missing style validations for stream {} with type {}".format(builder.stream_id, builder._type))
