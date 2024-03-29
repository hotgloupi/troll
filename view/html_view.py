# -*- encoding: utf-8 -*-

from genshi import template
import threading
import web

from troll.view.abstract_view import AbstractView

class Viewer(object):
    def __init__(self, loader):
        self.loader = loader
        self.pages = {}

    def render(self, page, obj={}):
        tmpl = self.loader.load(page, encoding="utf-8")
        tmpl = tmpl.generate(**obj)
        return tmpl.render('html', doctype='html5')

class ViewerStore(threading.local):
    def __init__(self):
        self._viewers = {}

    def get(self, template_dir, auto_reload, encoding):
        viewer = self._viewers.get(template_dir)
        if viewer is None:
            self._viewers[template_dir] = viewer = Viewer(
                template.TemplateLoader(
                    template_dir,
                    auto_reload=auto_reload,
                    default_encoding=encoding
                )
            )
        return viewer


class HTMLView(AbstractView):
    """
        Base class for an HTML view
        >>> class MyView(troll.view.HTMLView):
        >>>     __template__ = 'index.html'
        >>>     __template_dir__ = 'templates' # this is default value, overridable also with app conf
        >>>
        >>>     @troll.view.expose
        >>>     def index(self):
        >>>         return self.render()
        >>>
        >>>     @troll.view.expose
        >>>     def login(self):
        >>>         return self.render('login.html')
    """
    __viewers__ = ViewerStore()
    __template__ = None
    __template_dir__ = None

    def __init__(self, app):
        self._viewer = None
        if self.__template_dir__ is None:
            self.__template_dir__ = app.conf['template_dir']
        AbstractView.__init__(self, app)

    @property
    def viewer(self):
        if self._viewer is None:
            self._viewer = self.__viewers__.get(
                self.__template_dir__,
                self.app.conf['debug'],
                self.app.conf['encoding']
            )
        return self._viewer

    def render(self, template=None, obj=None):
        if template is None:
            template = self.__template__
        assert template is not None
        if obj is None:
            obj = {}

        if 'session' not in obj:
            obj['session'] = self.session

        if 'user' not in obj:
            obj['user'] = self.user

        if 'path' not in obj:
            obj['path'] = web.ctx.path
        web.header('Content-Type', 'text/html')
        return self.viewer.render(template, obj)
