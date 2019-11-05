import math
import time
import json

DEG_1_AS_RAD = math.pi / 180;
DEG_90_AS_RAD = 90 * DEG_1_AS_RAD;

circle_metadata = {
    'type': 'xviz/metadata',
    'data': {
        'version': '2.0.0',
        'streams': {
            '/vehicle_pose': {},
            '/circle': {
                'coordinate': 'IDENTITY',
                'stream_style': {
                    'fill_color': [200, 0, 70, 128]
                }
            },
            '/ground_grid_h': {
                'coordinate': 'IDENTITY',
                'stream_style': {
                    'stroked': True,
                    'stroke_width': 0.2,
                    'stroke_color': [0, 255, 0, 128]
                }
            },
            '/ground_grid_v': {
                'coordinate': 'IDENTITY',
                'stream_style': {
                    'stroked': True,
                    'stroke_width': 0.2,
                    'stroke_color': [0, 255, 0, 128]
                }
            }
        }
    }
}

class CircleScenario:
    def __init__(self, live=True, radius=30, duration=10, speed=10):
        self._timestamp = time.time()
        self._radius = radius
        self._duration = duration
        self._speed = speed
        self._live = live
        self._grid = self._draw_grid()

    def get_metadata(self):
        metadata = json.loads(json.dumps(circle_metadata)) # copy

        if not self._live:
            log_start_time = self._timestamp
            metadata['data']['log_info'] = {
                "log_start_time": log_start_time,
                "log_end_time": log_start_time + self._duration
            }

        return metadata

    def get_message(self, time_offset):
        timestamp = self._timestamp + time_offset

        return {
            'type': 'xviz/state_update',
            'data': {
                'update_type': 'snapshot',
                'updates': [
                    {
                        'timestamp': timestamp,
                        'poses': self._draw_pose(timestamp),
                        'primitives': self._grid
                    }
                ]
            }
        }

    def _draw_pose(self, timestamp):
        circumference = math.pi * self._radius * 2
        degrees_persec = 360 / (circumference / self._speed)
        current_degrees = timestamp * degrees_persec
        angle = current_degrees * DEG_1_AS_RAD
        return {
            '/vehicle_pose': {
                'timestamp': timestamp,
                # Make the car orient the the proper direction on the circle
                'orientation': [0, 0, DEG_90_AS_RAD + current_degrees * DEG_1_AS_RAD],
                'position': [self._radius * math.cos(angle), self._radius * math.sin(angle), 0]
            }
        }

    def _calculate_grid(self, size):
        grid = [0]
        for i in range(10, size, 10):
            grid = [-i] + grid + [i]
        return grid

    def _draw_grid(self):
        # Have grid extend beyond car path
        grid_size = self._radius + 10
        grid = self._calculate_grid(grid_size)

        gridxviz_h = [{"vertices": [x, -grid_size, 0, x, grid_size, 0]} for x in grid]
        gridxviz_v = [{"vertices": [-grid_size, y, 0, grid_size, y, 0]} for y in grid]

        return {
            '/ground_grid_h': {
                'polylines': gridxviz_h
            },
            '/ground_grid_v': {
                'polylines': gridxviz_v
            },
            '/circle': {
                'circles': [
                    {
                        'center': [0.0, 0.0, 0.0],
                        'radius': self._radius
                    },
                    {
                        'center': [self._radius, 0.0, 0.1],
                        'radius': 1,
                        'base': {
                            'style': {
                                'fill_color': [0, 0, 255]
                            }
                        }
                    }
                ]
            }
        }
