
import logging
from easydict import EasyDict as edict

PRIMITIVE_TYPES = edict(
    # Geometry primitives
    circle='circle',
    image='image',
    point='point',
    polygon='polygon',
    polyline='polyline',
    stadium='stadium',
    text='text',

    # UI primitives
    treetable='treetable'
)

STYLES = edict(
    stroke_color='stroke_color',
    fill_color='fill_color',
    radius='radius',
    radius_pixels='radius_pixels',
    radius_min_pixels='radius_min_pixels',
    radius_max_pixels='radius_max_pixels',
    stroke_width='stroke_width',
    stroke_width_min_pixels='stroke_width_min_pixels',
    stroke_width_max_pixels='stroke_width_max_pixels',
    height='height',
    opacity='opacity',
    stroked='stroked',
    filled='filled',
    extruded='extruded',
    font_family='font_family',
    font_weight='font_weight',
    text_size='text_size',
    text_rotation='text_rotation',
    text_anchor='text_anchor',
    text_baseline='text_baseline',
    point_color_mode='point_color_mode',
    point_color_domain='point_color_domain'
)

CATEGORY = edict(
    ANNOTATION='ANNOTATION',
    FUTURE_INSTANCE='FUTURE_INSTANCE',
    POSE='POSE',
    PRIMITIVE='PRIMITIVE',
    UI_PRIMITIVE='UI_PRIMITIVE',
    TIME_SERIES='TIME_SERIES',
    VARIABLE='VARIABLE'
)

PRIMITIVE_STYLE_MAP = edict(dict([
    (PRIMITIVE_TYPES.circle, [
        STYLES.opacity,
        STYLES.stroked,
        STYLES.filled,
        STYLES.stroke_color,
        STYLES.fill_color,
        STYLES.radius,
        STYLES.radius_min_pixels,
        STYLES.radius_max_pixels,
        STYLES.stroke_width,
        STYLES.stroke_width_min_pixels,
        STYLES.stroke_width_max_pixels
    ]),
    (PRIMITIVE_TYPES.point, [
        STYLES.opacity,
        STYLES.fill_color,
        STYLES.radius_pixels,
        STYLES.point_color_mode,
        STYLES.point_color_domain
    ]),
    (PRIMITIVE_TYPES.polygon, [
        STYLES.stroke_color,
        STYLES.fill_color,
        STYLES.stroke_width,
        STYLES.stroke_width_min_pixels,
        STYLES.stroke_width_max_pixels,
        STYLES.height,
        STYLES.opacity,
        STYLES.stroked,
        STYLES.filled,
        STYLES.extruded
    ]),
    # XXX: xviz need verify from here
    (PRIMITIVE_TYPES.text, [
        STYLES.opacity,
        STYLES.font_family,
        STYLES.font_weight,
        STYLES.text_size,
        STYLES.text_rotation,
        STYLES.text_anchor,
        STYLES.text_baseline,
        STYLES.fill_color
    ]),
    (PRIMITIVE_TYPES.polyline, [
        STYLES.opacity,
        STYLES.stroke_color,
        STYLES.stroke_width,
        STYLES.stroke_width_min_pixels,
        STYLES.stroke_width_max_pixels
    ]),
    (PRIMITIVE_TYPES.stadium, [
        STYLES.opacity,
        STYLES.fill_color,
        STYLES.radius,
        STYLES.radius_min_pixels,
        STYLES.radius_max_pixels
    ])
]))

# TODO: Integrate XVIZValidator into base builder
class XVIZValidator:
    """
    # Reference
    [@xviz/builder/xviz-validator]/(https://github.com/uber/xviz/blob/master/modules/builder/src/builders/xviz-validator.js)
    """
    def __init__(self, looger=logging.getLogger("xviz")):
        self._logger = looger

    def warn(self, msg):
        self._logger.warn(msg)

    def error(self, msg):
        self._logger.error(msg)
        raise ValueError("Error triggered: " + msg)

    def hasProp(self, builder, prop, msg=None):
        if hasattr(builder, prop):
            return
        self._logger.warn(msg or "Stream {}: {} is missing"\
            .format(builder.StreamId, prop))

    def propSetOnce(self, builder, prop, msg=None):
        if not hasattr(builder, prop):
            return
        if len(getattr(builder, prop)) == 0:
            return

        self._logger.warn(msg or "Stream {}: {} has been already set."\
            .format(builder.StreamId, prop))

    def matchMetaData(self, builder):
        metadata = builder.Metadata
        streamId = builder.StreamId
        category = builder.Category

        if metadata and hasattr(metadata):
            streamMetadata = metadata.streams[streamId]
            if not streamMetadata:
                self._logger.warn("{} is not defined in metadata.".format(streamId))
            elif category != metadata.category:
                self._logger.warn("Stream {} category '{}' does not match metadata definition ({})."\
                    .format(streamId, category, streamMetadata.category))

    def validateStyle(self, builder):
        properties = builder._style.keys()
        if builder._type in PRIMITIVE_STYLE_MAP.keys():
            validProperties = PRIMITIVE_STYLE_MAP[builder._type]
            invalidProps = [prop for prop in properties if prop not in validProperties]
            if len(invalidProps) > 0:
                self.warn("Invalid style properties {} for stream {}".format(
                    ','.join(invalidProps), builder.StreamId))
        else:
            self.warn("Missing style validations for stream {} with type {}".format(builder.StreamId, builder._type))
