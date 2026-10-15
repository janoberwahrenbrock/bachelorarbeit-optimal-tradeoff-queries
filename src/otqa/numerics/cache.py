"""Bounded LRU storage owned by one numerical session.

An oversized entry is computed normally and is simply not retained. Cache
capacity never changes a mathematical input or result.
"""
from collections import OrderedDict
from dataclasses import dataclass
from threading import RLock
from typing import Callable, Generic, TypeVar

K = TypeVar("K")
V = TypeVar("V")


@dataclass(frozen=True)
class CacheInfo:
    hits: int
    misses: int
    entries: int
    bytes: int
    max_entries: int
    max_bytes: int | None


class BoundedCache(Generic[K, V]):
    def __init__(self, max_entries: int, max_bytes: int | None = None,
                 size: Callable[[K, V], int] | None = None):
        self.max_entries, self.max_bytes = max_entries, max_bytes
        self._size = size or (lambda key, value: 0)
        self._entries: OrderedDict[K, tuple[V, int]] = OrderedDict()
        self._bytes = self.hits = self.misses = 0
        self._lock = RLock()

    def get(self, key: K) -> V | None:
        with self._lock:
            item = self._entries.get(key)
            if item is None:
                self.misses += 1
                return None
            self.hits += 1
            self._entries.move_to_end(key)
            return item[0]

    def put(self, key: K, value: V) -> None:
        size = self._size(key, value)
        if self.max_bytes is not None and size > self.max_bytes:
            return
        with self._lock:
            previous = self._entries.pop(key, None)
            if previous is not None:
                self._bytes -= previous[1]
            self._entries[key] = value, size
            self._bytes += size
            while (len(self._entries) > self.max_entries or
                   (self.max_bytes is not None and self._bytes > self.max_bytes)):
                _, (_, removed_size) = self._entries.popitem(last=False)
                self._bytes -= removed_size

    def clear(self) -> None:
        with self._lock:
            self._entries.clear()
            self._bytes = 0

    def info(self) -> CacheInfo:
        with self._lock:
            return CacheInfo(self.hits, self.misses, len(self._entries), self._bytes,
                             self.max_entries, self.max_bytes)
