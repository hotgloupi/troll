# -*- encoding: utf-8 -*-

import abc
import inspect
import web

class AbstractView(object):
    __metaclass__ = abc.ABCMeta

    _exposed_methods = None

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


    @abc.abstractproperty
    def app(self):
        """
            This method is defined internally. You can use it in all
            view implementations.
            >>> class MyView(AbstractView):
            >>>     @expose
            >>>     def index(self):
            >>>         return app.session.user['fullname']
            >>>
        """

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
