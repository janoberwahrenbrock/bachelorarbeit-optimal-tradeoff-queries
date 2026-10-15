"""Picklable read-only mappings preserving insertion order and exact values."""
from collections.abc import Mapping
from types import MappingProxyType


class FrozenMapping(Mapping):
    __slots__ = ("_data",)

    def __init__(self, values=()):
        # The input mapping remains owned by its builder; taking one boundary
        # snapshot prevents a retained builder reference from changing a state.
        object.__setattr__(self, "_data", MappingProxyType(dict(values)))

    def __setattr__(self, name, value):
        raise AttributeError("frozen mapping")

    @classmethod
    def _from_owned(cls, values):
        """Internal builder handoff; the caller must retain no mutable alias."""
        instance = object.__new__(cls)
        object.__setattr__(instance, "_data", MappingProxyType(values))
        return instance

    def __getitem__(self, key):
        return self._data[key]

    def __iter__(self):
        return iter(self._data)

    def __len__(self):
        return len(self._data)

    def keys(self):
        return self._data.keys()

    def values(self):
        return self._data.values()

    def items(self):
        return self._data.items()

    def get(self, key, default=None):
        return self._data.get(key, default)

    def __reduce__(self):
        return type(self), (tuple(self._data.items()),)

    def __repr__(self):
        return f"FrozenMapping({self._data!r})"
