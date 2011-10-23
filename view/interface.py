# -*- encoding: utf-8 -*-

from troll.interface import Interface

class IView(Interface):
    """
        Base class for all view
    """
    def __init__(self, app):
        self._app = app
        self._session = None
        self._user = None
        self._logger = None

    @property
    def app(self): return self._app

    @property
    def session(self):
        if self._session is None:
            self._session = self._app.session
        return self._session

    @property
    def user(self):
        if self._user is None:
            self._user = self.session.user
        return self._user

    @property
    def logger(self):
        if self._logger is None:
            name = self.__class__.__module__ + '.' + self.__class__.__name__
            self._logger = self._app.getLogger(name)
        return self._logger

class IEditView(IView):
    pass

class IHTMLView(IView):
    pass

class IJsonView(IView):
    pass

class IXMLView(IView):
    pass

class IWidget(IView):
    pass

class IInput(IView):
    pass
