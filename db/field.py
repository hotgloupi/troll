# -*- encoding: utf-8 -*-

class Field(object):
    def __init__(self, descr, default):
        self.name = None
        self.descr = unicode(descr)
        self.default = default

    def validate(self, value):
        return ''

class Int(Field):

    def __init__(self, descr, default, min=None, max=None):
        Field.__init__(self, descr, default)
        self.min = min
        self.max = max

    def validate(self, value):
        if not isinstance(value, int):
            return 'Value %s is not an instance of int' % str(value)
        if self.min is not None and value < self.min:
            return 'Number %d is greater than %d' % (value, self.min)
        if self.max is not None and value > self.max:
            return 'Number %d is lower than %d' % (value, self.min)
        return ''

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
        if not isinstance(value, basestring):
            return "Value %s is not an instance of string" % str(value)
        if self.min is not None and len(value) < self.min:
            return 'String too short'
        if self.max is not None and len(value) > self.max:
            return 'String too long'
        return ''

class Password(String):
    pass

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

