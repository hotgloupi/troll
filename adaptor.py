# -*- encoding: utf-8 -*-

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

def adapt(obj, *interfaces):
    global _adaptors
    """
        Adapt instance obj to given interfaces
    """
    interfaces = tuple(sorted(interfaces))
    adaptors = _adaptors.get(interfaces)

    if adaptors is not None:
        adaptor = adaptors.get(obj.__class__)
        if adaptor is not None:
            return adaptor(obj)
        else:
            raise Exception("Cannot adapt %s to %s " % (
                str(obj.__class__),
                str(interfaces)
            ))
    else:
        raise Exception("No adapters found for %s " %
            str(interfaces)
        )

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
    class MetaClass(type):
        def __new__(cls, name, bases, dct):
            adaptor = type.__new__(cls, name, bases, dct)
            interfaces = getInterfaces(adaptor)
            register(adaptor, interfaces, classes)
            combinations = []
            for n in range(1, len(interfaces)):
                combinations.extend(
                    tuple(sorted(c)) for c in itertools.combinations(interfaces, n)
                )
            for c in combinations:
                if  c not in _adaptors:
                    register(adaptor, c, classes)
    return MetaClass

def register(adaptor, interfaces, targets):
    global _adaptors
    assert len(interfaces)
    interfaces = tuple(sorted(interfaces))
    adaptors = _adaptors.setdefault(interfaces, {})
    for target in targets:
        adaptors[target] = adaptor

if __name__ == "__main__":
    import doctest
    doctest.testmod()
