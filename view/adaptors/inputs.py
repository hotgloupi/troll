# -*- encoding: utf-8 -*-

from troll.adaptor import adapts
from troll.application import Application
from troll.db.field import Bool
from troll.db.field import Date
from troll.db.field import Int
from troll.db.field import Mail
from troll.db.field import Password
from troll.db.field import String
from troll.db.field import Text
from troll.db.table import Table
from troll.view.interface import IInput

from genshi import HTML

class Input(IInput):
    def __init__(self, field, obj, app):
        self.field = field
        self.obj = obj
        self.error = None
        IInput.__init__(self, app)

    def params(self, **kwargs):
        params = {
            'name': self.field.name,
            'label':  self.field.descr,
            'table': self.obj.__table__,
            'value': unicode(self.obj[self.field.name]),
            'input_class': '',
            'label_class': '',
            'input_attrs': '',
            'error': '',
        }
        params.update(kwargs)
        if self.error is not None:
            params['error'] = """<span class="error">%s</span>""" % self.error
        return params

    def _renderInput(self, **kwargs):
        html = u"""
            <label for="%(table)s.%(name)s" class="%(label_class)s">%(label)s</label>
            <input type="%(type)s" name="%(table)s.%(name)s" class="%(input_class)s" value="%(value)s" %(input_attrs)s />
            %(error)s
        """ % self.params(**kwargs)
        return HTML(html)

    def _renderBool(self, **kwargs):
        checked = self.obj[self.field.name] and u'checked="checked"' or u''
        return self._renderInput(type="checkbox", input_attrs=checked, **kwargs)

    def _renderString(self, **kwargs):
        return self._renderInput(type='text', **kwargs)

    def _renderPassword(self, **kwargs):
        return self._renderInput(type='password', **kwargs)

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

createInput(Mail, Input._renderString)
createInput(String, Input._renderString)
createInput(Password, Input._renderPassword)
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
