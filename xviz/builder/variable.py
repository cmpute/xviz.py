from easydict import EasyDict as edict

from xviz.builder.base_builder import XVIZBaseBuilder
from xviz.builder.validator import CATEGORY

class XVIZVariableBuilder(XVIZBaseBuilder):
    def __init__(self, metadata, validator):
        super().__init__(CATEGORY.POSE, metadata, validator)

        # Stores variable data by stream then id
        # They will then be group when constructing final object
        self._data = {}

        # inflight builder data
        self._id = None
        self._values = None

    def id(self, identifier):
        self.validate_prop_set_once('_id')
        self._id = identifier
        return self

    def values(self, values):
        self.validate_prop_set_once('_values')
        if not isinstance(values, [list, tuple]):
            self.validate_error("Input `values` must be array")

        self._values = values
        return self

    def get_data(self):
        self._flush()
        if not self._data:
            return None

        return edict(self._data)

    def _add_variable_entry(self):
        if not self._data_pending():
            return

        field_name = 'doubles'
        value = self._values[0]
        if isinstance(value, str):
            field_name = 'strings'
        elif isinstance(value, bool):
            field_name = 'bools'

        entry = edict(values={field_name: self._values})
        if self._id:
            entry.base = edict(object_id=self._id)

        if self._stream_id in self._data.keys():
            if self._id in self._data[self._stream_id]:
                self.validate_error("Input `values` already set for id %s" % self._id)
            else:
                self._data[self._stream_id][self._id] = entry
        else:
            id_entry = edict()
            id_entry[self._id] = entry
            self._data[self._stream_id] = id_entry

    def _data_pending(self):
        return self._values and self._id

    def _validate(self):
        if self._data_pending():
            super()._validate()
            if self._values is None:
                self.validate_warn("Stream %s values are not provided" % self._stream_id)

    def _flush(self):
        self._validate()
        self._add_variable_entry()
        self._reset()

    def _reset(self):
        self._id = None
        self._values = None
