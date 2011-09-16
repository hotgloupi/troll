# -*- encoding: utf-8 -*-

from troll.db.interface import Interface
from troll.db.field import Field
from troll.db.broker import makeBroker

class SmartDictMeta(type):
    def __new__(cls, name, bases, dct):
        if '__implements__' in dct:
            if dct['__implements__'].__class__ != tuple:
                dct['__implements__'] = (dct['__implements__'],)
            fields = []
            for interface in dct['__implements__']:
                if issubclass(interface, Interface):
                    cls._prepareInterface(fields, interface)
            dct['__fields__'] = tuple(fields)
            d = {}
            for f in fields:
                assert f.name is not None
                assert f.name not in d
                d[f.name] = f
            dct['__fields_by_name__'] = d
            dct['__slots__'] = tuple()
            if '__primary_keys__' not in dct:
                dct['__primary_keys__'] = tuple()
            if 'Broker' not in dct:
                dct['Broker'] = makeBroker(cls)
            dct['Broker'].__type__ = cls
        return type.__new__(cls, name, bases, dct)

    @classmethod
    def _prepareInterface(cls, fields, interface):
        for name, field in interface.__dict__.iteritems():
            if isinstance(field, Field):
                field.name = name
                fields.append(field)

class SmartDict(object):
    __metaclass__ = SmartDictMeta
    __slots__ = ('_values', '_dirty_fields')

    def __init__(self, values={}):
        self._values = {}
        self._dirty_fields = set()
        for f in self.__fields__:
            self._values[f.name] = values.get(f.name, f.default)
        # XXX check for wrong keys from values ?

    def validate(self):
        for f in self.__fields__:
            if not f.validate():
                return False
        return True

    def __contains__(self, key):
        return key in self.__fields_by_name__

    def __getitem__(self, key):
        f = self.__fields_by_name__.get(key)
        if f is None:
            raise KeyError(str(key))
        return self._values[key]

    def __getattr__(self, key):
        f = self.__fields_by_name__.get(key)
        if f is None:
            return object.__getattribute__(self, key)
        return self._values[key]

    def __setattr__(self, key, val):
        f = self.__fields_by_name__.get(key)
        if f is None:
            return object.__setattr__(self, key, val)
        if self._values[key] == val:
            return
        if not f.validate(val):
            raise ValueError("The value '%s' is not allowed for field '%s'" % (str(val), str(f)))
        self._values[key] = val
        self._dirty_fields.add(key)

    def __setitem__(self, key, val):
        f = self.__fields_by_name__.get(key)
        if f is None:
            raise KeyError(str(key))
        if self._values[key] == val:
            return
        self._values[key] = val
        self._dirty_fields.add(key)

    def keys(self): return self._values.keys()
    def values(self): return self._values.values()
    def items(self): return self._values.items()
    def iterkeys(self): return self._values.iterkeys()
    def itervalues(self): return self._values.itervalues()
    def iteritems(self): return self._values.iteritems()

    def isDirty(self): return len(self._dirty_fields) > 0
    def getDirtyFields(self): return self._dirty_fields
    #def setDirtyFields(self, fields=None):
    #    """
    #        Set dirty fields with the iterable fields.
    #        if fields is None, all fields are dirty
    #    """
    #    if fields is None:
    #        fields = self.__fields__
    #    for f in fields:
    #        self._dirty_fields.add(f)

