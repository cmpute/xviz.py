# xviz.py

Python implementation of XVIZ protocol. Note that this repository only comply with the protocol standard, the some of the implemented structure and modules definition are not the same. 

# Requirements

Python3, `websockets`, [`gltflib`](https://github.com/sergkr/gltflib), `protobuf`, `numpy`

# Get started

You can try running the scenario server by `python examples/serve_scenarios.py`. Then you can run `cd examples/get-started && yarn start-live` under your `streetscape.gl` repository to see the example scenarios.

Refer to documentation (to be created), examples and tests to learn how to use the library.

# Reference
- [glTF](https://github.com/KhronosGroup/glTF/blob/master/specification/2.0/README.md)
    - C++ header glTF library: https://github.com/syoyo/tinygltf
    - XViz implementation: https://github.com/uber-web/loaders.gl/blob/master/modules/gltf/scripts/glbdump.js
    - pygltflib: https://gitlab.com/dodgyville/pygltflib
    - gltflib: https://github.com/sergkr/gltflib
- Websocket
    - websocket on Python3: https://websockets.readthedocs.io/en/2.7/index.html
    - single websocket on Python2/3: https://github.com/Pithikos/python-websocket-server