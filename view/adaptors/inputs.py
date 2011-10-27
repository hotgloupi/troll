# -*- encoding: utf-8 -*-

from troll.adaptor import adapts
from troll.application import BaseApplication
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
from genshi.template import MarkupTemplate

class Input(IInput):

    _input = u"""
<html xmlns="http://www.w3.org/1999/xhtml" xmlns:py="http://genshi.edgewall.org/" py:strip="">
<label for="${table}.${name}" class="${label_class}">${label}</label>
<input type="${input_type}" name="${table}.${name}" class="${input_class}" value="${value}" py:attrs="input_attrs" />
<span py:if="error" class="error">${error}</span>
</html>"""

    _textarea = u"""
<html xmlns="http://www.w3.org/1999/xhtml" xmlns:py="http://genshi.edgewall.org/" py:strip="">
<label for="${table}.${name}" class="${label_class}">${label}</label>
<textarea name="${table}.${name}" class="${input_class}" py:attrs="input_attrs">${value}</textarea>
<span py:if="error" class="error">${error}</span>
</html>"""

    def __init__(self, field, obj, app):
        self.field = field
        self.obj = obj
        self.error = None
        IInput.__init__(self, app)

    def params(self, kwargs):
        params = {
            'name': self.field.name,
            'label':  self.field.descr,
            'table': self.obj.__table__,
            'value': unicode(self.obj[self.field.name]),
            'input_class': '',
            'label_class': '',
            'input_attrs': '',
            'error': self.error,
        }
        params.update(kwargs)
        return params

    def generate(self, string, **kwargs):
        return MarkupTemplate(string).generate(**self.params(kwargs))

    def _renderBool(self, **kwargs):
        attrs = kwargs.get('input_attrs', {})
        if self.obj[self.field.name]:
            attrs[u'checked'] = u'checked'
        return self.generate(self._input, input_type="checkbox", input_attrs=attrs, **kwargs)

    def _renderString(self, **kwargs):
        return self.generate(self._input, input_type='text', **kwargs)

    def _renderPassword(self, **kwargs):
        return self.generate(self._input, input_type='password', **kwargs)

    def _renderText(self, **kwargs):
        return self.generate(self._textarea, **kwargs)


def createInput(field_type, render_method):
    class _Input(Input):
        __metaclass__ = adapts(field_type, Table, BaseApplication)
        render = render_method
    return _Input

createInput(Bool, Input._renderBool)
createInput(Date, lambda _: 'date')
createInput(Int, lambda _: 'int')

createInput(Mail, Input._renderString)
createInput(String, Input._renderString)
createInput(Password, Input._renderPassword)
createInput(Text, Input._renderText)
