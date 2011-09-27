# -*- encoding: utf-8 -*-

import itertools

from interface import getInterfaces

"""
    Let's say we have to convert Data into a PDF
    >>> class Data(object):
    ...     buffer = None
    >>>
    >>> data = Data()
    >>> data.buffer = 'Data to convert'

    We create a marker interface for adapters
    that can build a XML document
    >>> from view import IView
    >>> class XMLView(IView):
    ...     "render XML document"

    We can now create our adaptor
    >>> class DataXMLAdaptor(XMLView):
    ...     __metaclass__ = adapts(Data)
    ...     def __init__(self, data):
    ...         assert isinstance(data, Data)
    ...         self._data = data
    ...
    ...     def render(self):
    ...         return '<data><![CDATA[%s]]></data>' % self._data.buffer
    ...

    Using the metaclass returned from 'adapts' function
    is equivalent to calling manually register(DataXMLAdaptor, (XMLView,), (Data,))

    Since the adaptor is registered, we can use it with the function adapt.
    >>> adapt(data, XMLView).render()
    '<data><![CDATA[Data to convert]]></data>'
"""
_adaptors = {}

def dumpAdaptors():
    for targets, adaptors in _adaptors.iteritems():
        for interfaces, adaptor in adaptors.iteritems():
            print 'adapts (%s,) to (%s,) with %s' % (
                ', '.join(t.__name__ for t in targets),
                ', '.join(i.__name__ for i in interfaces),
                adaptor.__name__
            )

def adapt(objs, *interfaces):
    global _adaptors
    """
        Adapt instance obj to given interfaces
    """
    if not isinstance(objs, tuple):
        objs = (objs,)
    families = []
    for t in (type(o) for o in objs):
        family = [t]
        while len(t.__bases__) == 1 and t.__bases__[0] != object:
            t = t.__bases__[0]
            family.append(t)
        families.append(family)
    def combinations(families):
        if len(families) == 1:
            for e in families[0]: yield (e,)
        elif len(families) > 1:
            for e in families[0]:
                for c in combinations(families[1:]):
                    yield (e,) + c

    adaptors = None
    for types in combinations(families):
        adaptors = _adaptors.get(types)
        if adaptors is not None:
            interfaces = tuple(sorted(interfaces))
            adaptor = adaptors.get(interfaces)
            if adaptor is not None:
                return adaptor(*objs)
    if adaptors is None:
        raise Exception("Cannot adapt %s to %s " % (
            str(objs),
            str(interfaces)
        ))

def adapts(*classes):
    """
        Return a metaclass to prepare the adaptor of given classes.
        Usage:
        >>> class IMutation(object): pass
        ...
        >>> class Data1(object): pass
        ...
        >>> class Data2(object): pass
        ...
        >>> class MyAdaptor(IMutation):
        ...     __metaclass__ = adapts(Data1, Data2)
        ...     def __init__(self, data):
        ...         self._data = data
        >>> adapt(Data1(), IMutation).__class__.__name__
        'MyAdaptor'
        >>> adapt(Data2(), IMutation).__class__.__name__
        'MyAdaptor'
    """
    global _adaptors
    #class MetaClass(type):
    #    def __new__(cls, name, bases, dct):
    #        print "BITE", bases
    #        adaptor = type.__new__(cls, name, bases, dct)
    def makeMetaClass(name, bases, dct):
        metabases = tuple(set(type(b) for b in bases))
        metaclass = type('Meta_' + '_'.join(str(b) for b in bases), metabases, {})
        adaptor = metaclass(name, bases, dct)
        interfaces = tuple(sorted(getInterfaces(adaptor)))
        register(adaptor, interfaces, classes)
        combinations = []
        for n in range(1, len(interfaces)):
            combinations.extend(
                tuple(sorted(c)) for c in itertools.combinations(interfaces, n)
            )
        for c in combinations:
            if  c not in _adaptors:
                register(adaptor, c, classes)
        print 'registered adaptor', name, 'for', interfaces
        return adaptor

    return makeMetaClass

def register(adaptor, interfaces, targets):
    global _adaptors
    assert len(interfaces)
    #families = []
    #for t in targets:
    #    family = [t]
    #    while len(t.__bases__) == 1 and t.__bases__[0] != object:
    #        t = t.__bases__[0]
    #        family.append(t)
    #    families.append(family)
    #def combinations(families):
    #    if len(families) == 1:
    #        for e in families[0]: yield (e,)
    #    elif len(families) > 1:
    #        for e in families[0]:
    #            for c in combinations(families[1:]):
    #                yield (e,) + c

    #for types in combinations(families):
    types = targets
    adaptors = _adaptors.setdefault(types, {})
    interfaces = tuple(sorted(interfaces))
    adaptors[interfaces] = adaptor

if __name__ == "__main__":
    import doctest
    doctest.testmod()
