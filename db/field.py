# -*- encoding: utf-8 -*-

class Field(object):
    def __init__(self, descr, default):
        self.name = None
        self.descr = unicode(descr)
        self.default = default

    def validate(self, value):
        return value is not None

class Int(Field):

    def __init__(self, descr, default, min=None, max=None):
        Field.__init__(self, descr, default)
        self.min = min
        self.max = max

    def validate(self, value):
        if not isinstance(value, int):
            return False
        if self.min is not None and value < self.min:
            return False
        if self.max is not None and value > self.max:
            return False
        return True

    def __str__(self):
        return "<field.Int in [%s, %s]>" % (
            self.min is None and "-Inf" or str(self.min),
            self.max is None and "+Inf" or str(self.max)
        )

class String(Field):
    def __init__(self, descr, default="", min=None, max=None):
        Field.__init__(self, descr, default)
        self.min = min
        self.max = max

    def validate(self, value):
        if self.min is not None and len(value) < self.min:
            return False
        if self.max is not None and len(value) > self.max:
            return False
        return True

class Text(String):
    pass

class Mail(Field):
    pass
    # TODO validate

class Date(Field):
    def __init__(self, descr):
        Field.__init__(self, descr, None)

class Bool(Field):
    pass

