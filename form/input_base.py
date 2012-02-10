# -*- encoding: utf-8 -*-

import threading
import genshi.template

class InputBase(threading.local):
    __template__ = None
    __attributes__ = ['class_', 'id', 'style']

    def __init__(self, name, **kwargs):
        self._params = kwargs
        self._params['name'] = unicode(name)
        assert self.__class__.__template__ is not None
        tpl = self.__class__.__template__
        if isinstance(tpl, basestring):
            self.__class__.__template__ = genshi.template.MarkupTemplate(tpl)
        else:
            assert hasattr(tpl, 'generate')

        self._attrs = kwargs.pop('attrs', {})
        assert isinstance(self._attrs, dict)
        for attr in self.__attributes__:
            value = kwargs.get(attr)
            if value is not None:
                self._attrs[attr.strip('_')] = value

    @property
    def name(self): return self._params['name']

    @property
    def params(self): return self._params

    def _getParams(self, additional_params={}):
        params = {'attrs': self._attrs}
        params.update(self._params)
        params.update(additional_params)
        return params

    def _render(self, **kwargs):
        return self.__template__.generate(**self._getParams(kwargs))
