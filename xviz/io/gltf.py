"""
This module provides basic io under GLTF format
"""

import logging
import json, array, struct
from typing import Union
from collections import namedtuple
from easydict import EasyDict as edict

import numpy as np

from xviz.io.base import XVIZBaseWriter
from xviz.message import XVIZMessage, XVIZEnvelope, AllDataType, Metadata

# Constants

bufferView_t = namedtuple("bufferViewItem", ("buffer", "byteOffset", "byteLength"))
accessor_t = namedtuple("accessorItem", ("bufferView", "type", "componentType", "count"))
image_t = namedtuple("imageItem", ("bufferView", "mimetype", "width", "height"))

component_type_d = {
  'b' : 5120,
  'B' : 5121,
  'h' : 5122,
  'H' : 5123,
  'I' : 5125,
  'f' : 5126
}
types_d = ['SCALAR', 'VEC2', 'VEC3', 'VEC4']
XVIZ_GLTF_EXTENSION = 'AVS_xviz'

def pad_to_4bytes(length):
    return (length + 3) & ~3

# Wrappers
class ImageWrapper:
    def __init__(self, image: bytes, width: int = None, height: int = None, mime_type: str = None):
        self.data = image
        self.mime_type = mime_type
        self.width = width
        self.height = height

class GLTFBuilder:
    """
    # Reference
    [GLBBuilder](https://github.com/uber-web/loaders.gl/blob/master/modules/gltf/src/lib/deprecated/glb-builder.js)
    and [GLTFBuilder](https://github.com/uber-web/loaders.gl/blob/master/modules/gltf/src/lib/deprecated/gltf-builder.js)
    from [@loaders.gl/gltf](https://github.com/uber-web/loaders.gl/blob/master/modules/gltf/README.md)
    """
    MAGIC_glTF = 0x46546c67 # glTF in ASCII
    MAGIC_JSON = 0x4e4f534a # JSON in ASCII
    MAGIC_BIN = 0x004e4942 # BIN\0 in ASCII

    def __init__(self):
        self._version = 2
        self._byte_length = 0 # keep track of body size
        self._json = edict(
            asset={
                "version": str(self._version)
            },
            buffers=[],
            bufferViews=[],
            accessors=[],
            image=[],
            meshes=[]
        )
        self._source_buffers = []
        self.log = logging.getLogger("gltf")

    ################ Basic glTF adders ##############

    def add_accessor(self, buffer_view_index: int, size: int, component_type: int, count: int):
        '''
        Adds an accessor to a bufferView

        :param buffer_view_index: The index of the buffer view to access
        :param size: XXX
        :param component_type: XXX
        :param count: XXX
        :return: accessor_index: Index of added buffer in "accessors" list
        '''
        self._json.accessors.append(accessor_t(
            bufferView=buffer_view_index,
            type=types_d[size - 1],
            componentType=component_type,
            count=count
        )._asdict())
        return len(self._json.accessors) - 1

    def add_buffer_view(self, buffer: bytes):
        '''
        Add one untyped source buffer, create a matching glTF `bufferView`,
        and return its index

        :param buffer: bytes
        :return: buffer_view_index: The index of inserted bufferView
        '''
        if not isinstance(buffer, bytes):
            raise ValueError("add_buffer_view should be directly used with bytes")

        self._json.bufferViews.append(bufferView_t(
            buffer=0,
            byteOffset=self._byte_length,
            byteLength=len(buffer)
        )._asdict())

        # Pad array
        pad_len = pad_to_4bytes(len(buffer))
        buffer += b'\x00' * (pad_len - len(buffer))
        self._byte_length += pad_len
        self._source_buffers.append(buffer)

        return len(self._json.bufferViews) - 1

    def add_buffer(self, buffer: Union[bytes, array.array], accessor_size: int):
        '''
        Add a binary buffer. Builds glTF "JSON metadata" and saves buffer reference.
        Buffer will be copied into BIN chunk during "pack".
        Currently encodes buffers as glTF accessors, but this could be optimized.

        :param buffer: flattened array
        :param size: XXX
        :param component_type: XXX
        :param count: XXX
        :return: accessor_index: Index of added buffer in "accessors" list
        '''
        buffer_view_index = self.add_buffer_view(buffer)
        return self.add_accessor(buffer_view_index, size=accessor_size,
            component_type=component_type_d[buffer.typecode], count=len(buffer))

    def add_application_data(self, key: str, data):
        '''
        Add an extra application-defined key to the top-level data structure.
        By default packs JSON by extracting binary data and replacing it with JSON pointers

        :param key: Key name of the data
        :param data:
        :param pack_typed_arrays: Pack binaries
        '''
        self._json[key] = data

    def add_extra_data(self, key, data):
        if 'extras' not in self._json.keys():
            self._json.extras = edict()
        self._json.extras[key] = data

    def add_extension(self, ext, data):
        if 'extensions' not in self._json.keys():
            self._json.extensions = edict()
        self._json.extensions[ext] = data
        self.register_used_extension(ext)

    def add_required_extension(self, ext, data, **options):
        self.add_extension(ext, data, **options)
        self.register_required_extension(ext)

    def register_used_extension(self, ext):
        if 'extensionUsed' not in self._json.keys():
            self._json.extensionsUsed = []
        if ext not in self._json.extensionUsed:
            self._json.extensionUsed.append(ext)

    def register_required_extension(self, ext):
        if 'extensionRequired' not in self._json.keys():
            self._json.extensionRequired = []
        if ext not in self._json.extensionRequired:
            self._json.extensionRequired.append(ext)

    ################ Output ############

    def flush(self, file):
        '''
        Encode the full glTF file as a binary GLB file
        
        :param file: file-like object. The stream to write data into.
            It could be a file opened in binary mode or BytesIO object
        '''

        # Prepare data
        self._json.buffers = [{"byteLength": self._byte_length}]
        binary = b''.join(self._source_buffers)
        jsonstr = json.dumps(self._json, separators=(',', ':')).encode('ascii')
        jsonlen = pad_to_4bytes(len(jsonstr))

        assert len(binary) == pad_to_4bytes(len(binary)), "Something wrong in binary padding"
        binlen = len(binary)

        # Write GLB header
        file.write(struct.pack("<I", self.MAGIC_glTF))
        file.write(struct.pack("<I", self._version))
        file.write(struct.pack("<I", 28 + jsonlen + binlen))
        
        # Write Json
        file.write(struct.pack("<I", jsonlen))
        file.write(struct.pack("<I", self.MAGIC_JSON))
        file.write(jsonstr)
        file.write(b"\x00" * (jsonlen - len(jsonstr))) # pad

        # Write Binary
        file.write(struct.pack("<I", binlen))
        file.write(struct.pack("<I", self.MAGIC_BIN))
        file.write(binary)
        file.write(b"\x00" * (binlen - len(binary))) # pad

    ################ glTF Applications ##############

    def pack_binary_json(self, data):
        # Check if string has same syntax as our "JSON pointers", if so "escape it".
        if isinstance(data, str) and data.find("#/") == -1:
            return '#' + data

        # Recursively deal with containers
        if isinstance(data, list):
            return [self.pack_binary_json(obj) for obj in data]
        if isinstance(data, dict):
            return {k:self.pack_binary_json(v) for k, v in data.items()}

        # Pack specific data to binary
        if isinstance(data, ImageWrapper):
            image_index = self.add_image(data.data)
            return "#/images/{}".format(image_index)
        if isinstance(data, array.array):
            buffer_index = self.add_buffer(data)
            return "#/accessors/{}".format(buffer_index)

        # Else return original
        return data

    def add_image(self, obj):
        # TODO: infer image type from binary
        if not isinstance(obj, ImageWrapper):
            raise ValueError("Image should be wrapped with ImageWrapper")

        buffer_view_index = self.add_buffer_view(obj)
        self._json.images.append(image_t(
            bufferView=buffer_view_index,
            mimeType=obj.mime_type,
            width=obj.width,
            height=obj.height
        )._asdict())
        return len(self._json.images) - 1
    
    def add_point_cloud(self, obj):
        raise NotImplementedError()

    def add_mesh(self, indices, mode):
        raise NotImplementedError()

    def add_compressed_mesh(self, atrributes, indices, mode):
        raise NotImplementedError()

    def add_compressed_point_cloud(self, attributes):
        raise NotImplementedError()

class GLBWriter(XVIZBaseWriter):
    def __init__(self, envelope=True, use_xviz_extension=True):
        self._message_timings = edict(messages={})
        self._use_xviz_extension = use_xviz_extension
        self._counter = 1
        self._warp_envelop = envelope

    def _save_timestamp(self, xviz_data: AllDataType, index: int = None):
        if index: # normal data
            if not xviz_data.updates:
                raise ValueError("Cannot find timestamp")

            times = [update.timestamp for update in xviz_data.updates]
            tmin, tmax = min(times), max(times)

            self._message_timings.messages[index] = (tmin, tmax, index, "%d-frame" % index)
        else: # metadata
            if xviz_data.HasField('log_info'):
                self._message_timings.start_time = xviz_data.log_info.start_time
                self._message_timings.end_time = xviz_data.log_info.end_time

    def write_message(self, message: XVIZMessage, index: int = None):
        
        self._check_valid()
        if self._warp_envelop:
            obj = XVIZEnvelope(message).to_object()
        else:
            obj = message.to_object()
        builder = GLTFBuilder()

        # Process necessary information
        if isinstance(message.data, Metadata):
            self._save_timestamp(message)
            fname = "1-frame.glb"
        else:
            if not index:
                index = self._counter
                self._counter += 1

            self._save_timestamp(message, index)
            fname = "%d-frame.glb" % index

            # TODO: wrap image data

        # Encode GLB into file
        packed_data = builder.pack_binary_json(obj)
        if self._use_xviz_extension:
            builder.add_extension(XVIZ_GLTF_EXTENSION, packed_data)
        else:
            builder.add_application_data('xviz', packed_data)

        with self._source.open(fname) as fout:
            builder.flush(fout)

    def close(self):
        if self._source:
            self._write_message_index()

        super().close()