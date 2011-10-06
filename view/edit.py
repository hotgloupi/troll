# -*- encoding: utf-8 -*-

from troll.adaptor import adapt
from troll.db.table import Table
from troll.view.html_view import HTMLView
from troll.view.interface import IEditView
from troll.view.interface import IInput

class Edit(HTMLView, IEditView):

    def __init__(self, obj, app, fields=None):
        self._obj = obj
        self._table = type(obj)
        assert issubclass(self._table, Table)
        self._fields = (fields is None and [self._table.__fields__] or [fields])[0]
        HTMLView.__init__(self, app)

    @property
    def obj(self): return self._obj

    def getWidgets(self):
        assert isinstance(self._obj, self._table)
        w = {}
        for f in self._fields:
            w[self._table.__table__ + '.' + f.name] = adapt((f, self._obj, self.app), IInput)
        return w

