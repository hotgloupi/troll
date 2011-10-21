# -*- encoding: utf-8 -*-

import threading

class ThreadedDict(object):
    __slots__ = ('_d', '_lock')

    def __init__(self):
        self._d = {}
        self._lock = threading.Lock()

    def __setitem__(self, key, value):
        with self._lock:
            self._d[key] = value

    def __getitem__(self, key):
        with self._lock:
            return self._d[key]

    def get(self, key, default=None):
        with self._lock:
            return self._d.get(key, default)



