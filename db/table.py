# -*- encoding: utf-8 -*-

from troll.db.smartdict import SmartDict

class Table(SmartDict):
    pass

def makeTable(interface, table, pkeys=('id',), fkeys={}):
    class _BasicSmartDict(SmartDict):
        __implements__ = interface
        __table__ = table
        __primary_keys__ = pkeys
        __foreign_keys__ = fkeys
    return _BasicSmartDict
