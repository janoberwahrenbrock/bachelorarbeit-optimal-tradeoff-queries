"""Equality elimination with immutable, stride-preserving cache entries."""
from dataclasses import dataclass

import numpy as np
from scipy.linalg import null_space

from otqa.numerics.cache import BoundedCache


def immutable_array(array):
    extent = sum((dimension - 1) * abs(stride)
                 for dimension, stride in zip(array.shape, array.strides) if dimension > 0)
    size = extent + array.dtype.itemsize if array.size else 0
    offset = sum((dimension - 1) * -stride for dimension, stride in
                 zip(array.shape, array.strides) if dimension > 0 and stride < 0)
    storage = bytearray(size)
    writable = np.ndarray(array.shape, dtype=array.dtype, buffer=storage,
                          offset=offset, strides=array.strides)
    writable[...] = array
    return np.ndarray(array.shape, dtype=array.dtype, buffer=bytes(storage),
                      offset=offset, strides=array.strides)


@dataclass(frozen=True)
class AffineDecomposition:
    particular_point: np.ndarray
    basis: np.ndarray
    equality_residual: float


class AffineCache:
    def __init__(self):
        self.cache = BoundedCache(4096, 8_388_608, self._entry_bytes)

    @staticmethod
    def _entry_bytes(key, value):
        return len(key[2] or b"") + len(key[4] or b"") + len(value.particular_point.base) + len(value.basis.base)

    def get(self, count, matrix, rhs):
        key = (count, None, None, None, None) if matrix is None else (
            count, (matrix.shape, matrix.dtype.str), matrix.tobytes(),
            (rhs.shape, rhs.dtype.str), rhs.tobytes())
        cached = self.cache.get(key)
        if cached is not None:
            return cached
        if matrix is None:
            point, basis, residual = np.zeros(count, dtype=float), np.eye(count, dtype=float), 0.0
        else:
            point, *_ = np.linalg.lstsq(matrix, rhs, rcond=None)
            residual = float(np.max(np.abs(matrix @ point - rhs), initial=0.0))
            basis = null_space(matrix)
        value = AffineDecomposition(immutable_array(point), immutable_array(basis), residual)
        self.cache.put(key, value)
        return value
