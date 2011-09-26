# -*- encoding: utf-8 -*-

from troll.interface import Interface

class IView(Interface):
    """
        Base class for all view
    """

class IEditView(IView):
    pass

class IHTMLView(IView):
    pass

class IJsonView(IView):
    pass

class IXMLView(IView):
    pass
