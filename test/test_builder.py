import json
from easydict import EasyDict as edict

from xviz.builder import XVIZBuilder
from xviz.builder.ui_primitive import XVIZUIPrimitiveBuilder
from google.protobuf.json_format import MessageToDict
import unittest

PRIMARY_POSE_STREAM = '/vehicle_pose'

DEFAULT_POSE = edict(
  timestamp=1.0,
  map_origin=edict(longitude=1.1, latitude=2.2, altitude=3.3),
  position=[11., 22., 33.],
  orientation=[0.11, 0.22, 0.33]
)

def setup_pose(builder):
    builder.pose(PRIMARY_POSE_STREAM)\
        .timestamp(DEFAULT_POSE.timestamp)\
        .map_origin(**DEFAULT_POSE.map_origin)\
        .position(*DEFAULT_POSE.position)\
        .orientation(*DEFAULT_POSE.orientation)

class TestPoseBuilder(unittest.TestCase):

    def test_single_pose(self):
        builder = XVIZBuilder()
        setup_pose(builder)

        expected = {
            'update_type': 'SNAPSHOT',
            'updates': [
                {
                    'timestamp': 1.0,
                    'poses': {
                        PRIMARY_POSE_STREAM: DEFAULT_POSE
                    }
                }
            ]
        }

        message = builder.get_message()
        assert json.dumps(message, sort_keys=True) == json.dumps(expected, sort_keys=True)

    def test_multiple_poses(self):
        builder = XVIZBuilder()
        setup_pose(builder)

        builder.pose('/vehicle-pose-2')\
            .timestamp(2.0)\
            .map_origin(4.4, 5.5, 6.6)\
            .position(44., 55., 66.)\
            .orientation(0.44, 0.55, 0.66)

        expected = {
            'update_type': 'SNAPSHOT',
            'updates': [
                {
                    'timestamp': 1.0,
                    'poses': {
                        PRIMARY_POSE_STREAM: DEFAULT_POSE,
                        "/vehicle-pose-2": {
                            'timestamp': 2.0,
                            'map_origin': {'longitude': 4.4, 'latitude': 5.5, 'altitude': 6.6},
                            'position': [44., 55., 66.],
                            'orientation': [0.44, 0.55, 0.66]
                        }
                    }
                }
            ]
        }

        message = builder.get_message()
        assert json.dumps(message, sort_keys=True) == json.dumps(expected, sort_keys=True)

class TestPrimitiveBuilder(unittest.TestCase):

    def test_polygon(self):
        builder = XVIZBuilder()
        setup_pose(builder)

        verts = [[0., 0., 0.], [4., 0., 0.], [4., 3., 0.]]
        builder.primitive('/test/polygon')\
            .polygon(verts)\
            .id('1')\
            .style({
                'fill_color': [255, 0, 0]
            })

        expected = {
            'timestamp': 1.0,
            'poses': {
                PRIMARY_POSE_STREAM: DEFAULT_POSE
            },
            'primitives': {
                '/test/polygon': {
                    'polygons': [
                        {
                            'base': {
                                'style': {
                                    'fill_color': [255, 0, 0],
                                },
                                'object_id': '1'
                            },
                            'vertices': verts
                        }
                    ]
                }
            }
        }

        data = builder.get_data().to_object()
        assert json.dumps(data, sort_keys=True) == json.dumps(expected, sort_keys=True)

class TestUIPrimitiveBuilder:
    def test_null(self):
        builder = XVIZUIPrimitiveBuilder(None, None)
        data = builder.stream('/test').get_data()

        assert data is None

    def test_treetable(self):
        builder = XVIZBuilder()
        setup_pose(builder)

        TEST_COLUMNS = [{'display_text': 'Name', 'type': 'STRING'}] # FIXME: type is in lower case in XVIZ
        builder.ui_primitives('/test').treetable(TEST_COLUMNS)
        data = builder.get_data().to_object()

        expected = {
            '/test': {
                'treetable': {
                    'columns': TEST_COLUMNS,
                    # 'nodes': [] # FIXME: nodes are no serialized
                }
            }
        }
        assert json.dumps(data['ui_primitives'], sort_keys=True) == json.dumps(expected, sort_keys=True)
