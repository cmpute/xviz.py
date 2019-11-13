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

import array
from xviz.v2.style_pb2 import StyleObjectValue, StyleStreamValue

def build_object_style(style):
    '''
    Create StyleObjectValue from dictionary. It basically deal with list of bytes.
    '''
    if 'fill_color' in style.keys():
        style['fill_color'] = bytes(style['fill_color'])
    if 'stroke_color' in style.keys():
        style['stroke_color'] = bytes(style['stroke_color'])
    return StyleObjectValue(**style)

def build_stream_style(style):
    '''
    Create StyleStreamValue from dictionary. It basically deal with list of bytes.
    '''
    if 'fill_color' in style.keys():
        style['fill_color'] = bytes(style['fill_color'])
    if 'stroke_color' in style.keys():
        style['stroke_color'] = bytes(style['stroke_color'])
    return StyleStreamValue(**style)
