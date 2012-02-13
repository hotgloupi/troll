# -*- encoding: utf-8 -*-

import threading

class ThreadedDict(object):
    __slots__ = ('_d', '_lock')

    def __init__(self):
        self._d = {}
        self._lock = threading.RLock()

    def __setitem__(self, key, value):
        with self._lock:
            self._d[key] = value

    def __getitem__(self, key):
        with self._lock:
            return self._d[key]

    def __delitem__(self, key):
        with self._lock:
            del self._d[key]

    def __contains__(self, key):
        with self._lock:
            return key in self._d

    def get(self, key, default=None):
        with self._lock:
            return self._d.get(key, default)

    def iteritems(self):
        with self._lock:
            return self._d.iteritems()

    def __iter__(self):
        with self._lock:
            return self._d.iteritems()

    def __len__(self):
        with self._lock:
            return len(self._d)
    def __str__(self):
        with self._lock:
            return str(self._d)

    def update(self, d):
        with self._lock:
            return self._d.update(d)

    def setdefault(self, k, v):
        with self._lock:
            return self._d.setdefault(k, v)
