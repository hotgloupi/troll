# -*- encoding: utf-8 -*-

import sqlite3

class Pool(object):

    # XXX TODO
    def __init__(self, connect_string):
        self._connect_string = connect_string

    def conn(self):
        return sqlite3.connect(self._connect_string)
