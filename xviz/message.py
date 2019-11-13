import base64

from xviz.v2.core_pb2 import StreamSet
from google.protobuf.json_format import MessageToDict

class XVIZData:
    '''
    This class is basically a wrapper around protobuf message `StreamSet`. It represent a frame of update.
    '''
    def __init__(self, data=None):
        if data and not isinstance(data, StreamSet):
            raise ValueError("The data input must be structured (using StreamSet class)")
        self._data = data

    def _unravel_list(self, list_: list, width: int):
        if len(list_) % width != 0:
            raise ValueError("The shape of the list is incorrect!")

        new_list = []
        for i in range(len(list_) // width):
            new_list.append(list_[i*width:(i+1)*width])
        return new_list

    def _unravel_style_object(self, style: dict):
        if 'fill_color' in style:
            print(base64.b64decode(style['fill_color']))
            style['fill_color'] = list(base64.b64decode(style['fill_color']))
        if 'stroke_color' in style:
            style['stroke_color'] = list(base64.b64decode(style['stroke_color']))

    def to_object(self):
        '''
        Serialize this data to primitive objects (with dict and list). Flattened arrays will
        be restored in this process.
        '''
        dataobj = MessageToDict(self._data, preserving_proto_field_name=True)

        print(dataobj)
        if 'primitives' in dataobj:
            for pdata in dataobj['primitives'].values():
                # process vertices
                if 'polygons' in pdata:
                    for pldata in pdata['polygons']:
                        if 'vertices' in pldata:
                            pldata['vertices'] = self._unravel_list(pldata['vertices'], 3)
                if 'polylines' in pdata:
                    for pldata in pdata['polylines']:
                        if 'vertices' in pldata:
                            pldata['vertices'] = self._unravel_list(pldata['vertices'], 3)
                        if 'colors' in pldata:
                            # TODO: identify size from vertices
                            pldata['colors'] = self._unravel_list(pldata['colors'], 4)
                if 'points' in pdata:
                    for pldata in pdata['points']:
                        if 'points' in pldata:
                            pldata['points'] = self._unravel_list(pldata['points'], 3)
                        if 'colors' in pldata:
                            # TODO: identify size from points
                            pldata['colors'] = self._unravel_list(pldata['colors'], 4)

                # process styles
                for pcats in pdata.values():
                    for pldata in pcats:
                        if 'base' in pldata and 'style' in pldata['base']:
                            self._unravel_style_object(pldata['base']['style'])
                    
        return dataobj
        