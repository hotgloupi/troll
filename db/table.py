# -*- encoding: utf-8 -*-

from troll.db.smartdict import SmartDict

class Table(SmartDict):
    def validate(self, *fields):
        if not fields:
            fields = self.__fields__
        else:
            fields = (self.__fields_by_name__[f] for f in fields)
        errors = {}
        for f in fields:
            err = f.validate(self._values[f.name])
            if err:
                errors[self.__table__ + '.' + f.name] = err
        return errors

    def insert(self, conn):
        with conn:
            self.Broker.insert(conn.cursor(), self)

    def save(self, conn):
        with conn:
            self.Broker.update(conn.cursor(), self)

def makeTable(interface, table, pkeys=('id',), fkeys={}):
    class _BasicSmartDict(Table):
        __implements__ = interface
        __table__ = table
        __primary_keys__ = pkeys
        __foreign_keys__ = fkeys
    return _BasicSmartDict
