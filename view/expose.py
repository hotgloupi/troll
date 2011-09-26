# -*- encoding: utf-8 -*-

import web

from troll.view.abstract_view import AbstractView

def expose(method):
    if not hasattr(method, '_exposed'):
        method._exposed = method
        #view = method.im_class
        #assert issubclass(view, AbstractView)
        #view.exposed_methods[method.__name__] = {
        #    'method': method,
        #}
    return method

def exposeWhen(*permissions):
    _permissions = []
    for p in permissions:
        if hasattr(p, '__iter__'):
            _permissions.extend(p)
        else:
            assert isinstance(p, basestring)
            _permissions.append(p)
    def decorator(method):
        method = expose(method)
        def wrapper(*args, **kwargs):
            self = args[0]
            if all(self.app.session.can(p) for p in _permissions):
                return method(*args, **kwargs)
            else:
                raise web.Forbidden()
        wrapper._exposed = method
        return wrapper
    return decorator

def exposeFor(roles):
    pass

def exposeIf(method):
    pass
