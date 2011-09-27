# -*- encoding: utf-8 -*-

from troll.interface import Interface

class IView(Interface):
    """
        Base class for all view
    """
    def __init__(self, app):
        self._app = app

    @property
    def app(self): return self._app

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
