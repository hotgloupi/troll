# -*- encoding: utf-8 -*-

from troll.view.interface import IInput
from troll.adaptor import adapt

def getInputWidgets(app, obj, fields=None, errors={}):
    table = type(obj)
    if fields is None:
        fields = table.__fields__
    widgets = {}
    for f in fields:
        k = table.__table__ + '.' + f.name
        widgets[k] = adapt((f, obj, app), IInput)
        widgets[k].error = errors.get(k)
    return widgets



