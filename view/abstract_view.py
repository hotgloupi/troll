# -*- encoding: utf-8 -*-

import inspect
import web

from troll.view.interface import IView

class AbstractView(IView):

    _exposed_methods = None

    def __init__(self, app):
        IView.__init__(self, app)

    @classmethod
    def getExposedMethods(cls):
        if cls._exposed_methods is None:
            members = inspect.getmembers(cls)
            cls._exposed_methods = {}
            for name, member in members:
                if hasattr(member, '__func__'):
                    func = getattr(member.__func__, '_exposed', None)
                    if func:
                        infos = inspect.getargspec(func)
                        cls._exposed_methods[func.__name__] = {
                            'method': member,
                            'args': infos.args,
                            'varargs': infos.varargs,
                            'keywords': infos.keywords,
                            'defaults': infos.defaults or (),
                        }

        return cls._exposed_methods

    def GET(self, *args):
        method = None
        if args:
            method = self._exposed_methods.get(args[0])
            if method:
                args = args[1:]
        if method is None:
            method = self._exposed_methods.get('index')
        if not method:
            raise web.notfound()
        return method['method'](self, *args)

    def POST(self, *args):
        method = None
        if args:
            method = self._exposed_methods.get(args[0])
            if method:
                args = args[1:]
        if method is None:
            method = self._exposed_methods.get('index')
        if not method:
            raise web.notfound()
        return method['method'](self, *args)
