"""
This module provides basic io under GLTF format
"""

import sys
PY3 = sys.version_info.major > 2

import logging
from collections import namedtuple
from easydict import EasyDict as edict

import json
import struct
import numpy as np

bufferView_t = namedtuple("bufferViewItem", ("buffer", "byteOffset", "byteLength"))
accessor_t = namedtuple("accessorItem", ("bufferView", "type", "componentType", "count"))
image_t = namedtuple("imageItem", ("bufferView", "mimetype", "width", "height"))

componentType_d = {
  np.int8   : 5120,
  np.uint8  : 5121,
  np.int16  : 5122,
  np.uint16 : 5123,
  np.uint32 : 5125,
  np.float32: 5126
}
types_d = ['SCALAR', 'VEC2', 'VEC3', 'VEC4'];

def padTo4Bytes(length):
    return (length + 3) & ~3

def getComponentTypeFromArray(ndarray):
    return componentType_d[ndarray.dtype]

def getAccessorTypeFromSize(size):
    return types_d[size - 1]

class ImageWrapper:
    def __init__(self, image, width=None, height=None, mimeType=None):
        self.data = image
        self.mimeType = mimeType
        self.width = None
        self.height = None

class GLTF:
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
        self.version = 2
        self.byteLength = 0 # keep track of body size
        self.json = edict(
            asset={
                "version": str(self.version)
            },
            buffers=[],
            bufferViews=[],
            accessors=[],
            image=[],
            meshes=[]
        )
        self.sourceBuffers = []
        self.log = logging.getLogger(GLTF) # if log is None else log

    ################ Basic glTF adders ##############

    def addAccessor(self, bufferViewIndex, **accessorArgs):
        '''
        Adds an accessor to a bufferView

        Parameters
        ----------
        bufferViewIndex: int
            The index of the buffer view to access
        size: int
            FIXME Unknown?
        componentType: int
            FIXME Unknown
        count: int
            FIXME Unknown

        Returns
        -------
        accessorIndex: int
            Index of added buffer in "accessors" list
        '''
        self.json.accessors.append(accessor_t(
            bufferView=bufferViewIndex,
            type=getAccessorTypeFromSize(accessorArgs["size"]),
            componentType=accessorArgs["componentType"],
            count=accessorArgs["count"]
        )._asdict())
        return len(self.json.accessors) - 1

    def addBufferView(self, buffer):
        '''
        Add one untyped source buffer, create a matching glTF `bufferView`,
        and return its index

        Parameters
        ----------
        buffer: bytes
            The binary data to add

        Returns
        -------
        bufferViewIndex: int
            The index of inserted bufferView
        '''
        if not isinstance(buffer, bytes):
            raise ValueError("addBufferView should be directly used with bytes")

        self.json.bufferViews.append(bufferView_t(
            buffer=0,
            byteOffset=self.byteLength,
            byteLength=len(buffer)
        )._asdict())
        self.byteLength += padTo4Bytes(len(buffer))
        self.sourceBuffers.append(buffer)
        return len(self.json.bufferViews) - 1

    def addBuffer(self, buffer, **accessorArgs):
        '''
        Add a binary buffer. Builds glTF "JSON metadata" and saves buffer reference.
        Buffer will be copied into BIN chunk during "pack".
        Currently encodes buffers as glTF accessors, but this could be optimized.

        Parameters
        ----------
        buffer: bytes
            Binary data to add
        size: int
            FIXME Unknown?
        componentType: int
            FIXME Unknown
        count: int
            FIXME Unknown

        Returns
        -------
        accessorIndex: int
            Index of added buffer in "accessors" list
        '''
        bufferViewIndex = self.addBufferView(buffer)
        accessorDefauls = {
            "size": accessorArgs['size'],
            "componentType": getComponentTypeFromArray(buffer),
            "count": len(buffer) // accessorArgs['size']
        }
        accessorDefauls.update(accessorArgs)
        return self.addAccessor(bufferViewIndex, **accessorArgs)

    def addApplicationData(self, key, data, **options):
        '''
        Add an extra application-defined key to the top-level data structure.
        By default packs JSON by extracting binary data and replacing it with JSON pointers

        Parameters
        ----------
        key: str
            Key name of the data
        data: complex object
            Stored data
        packTypedArrays: bool
            Pack binaries
        '''
        packTypedArrays = options.pop("packTypedArrays", True)
        self.json[key] = self.packBinaryJson(data, **options) \
            if packTypedArrays else data

    def packBinaryJson(self, data, **options):
        # Check if string has same syntax as our "JSON pointers", if so "escape it".
        if isinstance(data, str) and data.find("#/") == -1:
            return '#' + data

        # Recursively deal with containers
        if isinstance(data, list):
            return [self.packBinaryJson(obj, **options) for obj in data]
        if isinstance(data, dict):
            return {k:self.packBinaryJson(v, **options) for k, v in data.items()}

        # Pack specific data to binary
        if isinstance(data, ImageWrapper):
            imageIndex = self.addImage(data.data)
            return "#/images/{}".format(imageIndex)
        if isinstance(data, np.ndarray):
            bufferIndex = self.addBuffer(data)
            return "#/accessors/{}".format(bufferIndex)

        # Else return original
        return data

    ################ Output ############

    def encodeAsGLB(self, file):
        '''
        Encode the full glTF file as a binary GLB file
        
        Parameters
        ----------
        file: file-like object
            The stream to write data into. It could be a file opened in binary mode or BytesIO object
        '''

        # Prepare data
        self.json.buffer = [{"byteLength": self.byteLength}]
        binary = b''.join(self.sourceBuffers)
        jsonstr = json.dumps(self.json, separators=(',',':'))
        if PY3:
            jsonstr = jsonstr.encode('ascii')
        jsonlen = padTo4Bytes(len(jsonstr))
        binlen = padTo4Bytes(len(binary))

        # Write GLB header
        file.write(struct.pack("<I", self.MAGIC_glTF))
        file.write(struct.pack("<I", self.version))
        file.write(struct.pack("<I", 28 + jsonlen + binlen))
        
        # Write Json
        file.write(struct.pack("<I", jsonlen))
        file.write(struct.pack("<I", self.MAGIC_JSON))
        file.write(jsonstr)
        file.write(b"\x00" * (jsonlen - len(jsonstr)))

        # Write Binary
        file.write(struct.pack("<I", binlen))
        file.write(struct.pack("<I", self.MAGIC_BIN))
        file.write(binary)
        file.write(b"\x00" * (binlen - len(binary)))

    ################ glTF Extension ##############

    def addExtraData(self, key, data, **options):
        packTypedArrays = options.pop("packTypedArrays", True)
        if 'extras' not in self.json.keys():
            self.json.extras = edict()
        self.json.extras[key] = self.packBinaryJson(data, **options) \
            if packTypedArrays else data

    def addExtension(self, ext, data, **options):
        packTypedArrays = options.pop("packTypedArrays", True)
        if 'extensions' not in self.json.keys():
            self.json.extensions = edict()
        self.json.extensions[ext] = self.packBinaryJson(data, **options) \
            if packTypedArrays else data
        self.registerUsedExtension(ext)

    def addRequiredExtension(self, ext, data, **options):
        self.addExtension(ext, data, **options)
        self.registerRequiredExtension(ext)

    def registerUsedExtension(self, ext):
        if 'extensionUsed' not in self.json.keys():
            self.json.extensionsUsed = []
        if ext not in self.json.extensionUsed:
            self.json.extensionUsed.append(ext)

    def registerRequiredExtension(self, ext):
        if 'extensionRequired' not in self.json.keys():
            self.json.extensionRequired = []
        if ext not in self.json.extensionRequired:
            self.json.extensionRequired.append(ext)

    ################ glTF Applications ##############

    def addImage(self, obj):
        if not isinstance(obj, ImageWrapper):
            raise ValueError("Image should be wrapped with ImageWrapper")

        bufferViewIndex = self.addBufferView(obj)
        self.json.images.append(image_t(
            bufferView=bufferViewIndex,
            mimeType=obj.mimeType,
            width=obj.width,
            height=obj.height
        )._asdict())
        return len(self.json.images) - 1
    
    def addPointCloud(self, obj):
        raise NotImplementedError()

    def addMesh(self, indices, mode):
        raise NotImplementedError()

    def addCompressedMesh(self, atrributes, indices, mode):
        raise NotImplementedError()

    def addCompressedPointCloud(self, attributes):
        raise NotImplementedError()