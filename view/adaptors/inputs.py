# -*- encoding: utf-8 -*-

from troll.adaptor import adapts
from troll.application import Application
from troll.db.field import Bool
from troll.db.field import Date
from troll.db.field import Int
from troll.db.field import String
from troll.db.field import Text
from troll.db.table import Table
from troll.view.interface import IInput

from genshi import HTML

class Input(IInput):
    def __init__(self, field, obj, app):
        self.field = field
        self.obj = obj
        IInput.__init__(self, app)

    def params(self, **kwargs):
        params = {
            'name': self.field.name,
            'label':  self.field.descr,
            'table': self.obj.__table__,
            'value': unicode(self.obj[self.field.name]),
        }
        params.update(kwargs)
        return params

    def _renderBool(self):
        vars =  {
            'table': self.obj.__table__,
            'name': self.field.name,
            'label': unicode(self.field.descr),
            'type': 'checkbox',
            'checked': self.obj[self.field.name] and u'checked="checked"' or u'',
        }
        html = u"""
            <label for="%(table)s.%(name)s">%(label)s</label>
            <input type="%(type)s" name="%(table)s.%(name)s" %(checked)s />
        """ % vars
        return HTML(html)


    def _renderString(self):
        html = u"""
            <label for="%(table)s.%(name)s">%(label)s</label>
            <input type="%(type)s" name="%(table)s.%(name)s" value="%(value)s" />
        """ % self.params(type='text')
        return HTML(html)

def createInput(field_type, render_method):
    class _Input(Input):
        __metaclass__ = adapts(field_type, Table, Application)
        render = render_method
    return _Input

def renderInput(_type, field, obj):
    return HTML("""
        <label for="%(table)s.%(name)s">%(label)s</label>
    """ % {
        'table': obj.__table__,
        'name': field.name,
        'label': field.descr,
        'type': _type,
        'value': str(obj[field.name]),
    })

createInput(Bool, Input._renderBool)
createInput(Date, lambda _: 'date')
createInput(Int, lambda _: 'int')

createInput(String, Input._renderString)
createInput(Text,
    lambda self: HTML(u"""
        <label for="%(table)s.%(name)s">%(label)s</label>
        <textarea name="%(table)s.%(name)s">%(value)s</textarea>
    """ % {
        'table': self.obj.__table__,
        'name': self.field.name,
        'label': self.field.descr,
        'type': 'text',
        'value': self.obj[self.field.name].decode('utf-8'),
    })
)
