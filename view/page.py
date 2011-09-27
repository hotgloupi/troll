# -*- encoding: utf-8 -*-

import web
from genshi import HTML

from base_view import BaseView
from interface import IHTMLView
from expose import expose

class Page(BaseView, IHTMLView):

    __skeleton__ = None
    __template__ = None

    @expose
    def index(self):
        return self.render()

    def render(self, template=None, obj=None):
        if template is None:
            template = self.__template__
        if obj is None:
            obj = {}
        res = BaseView.render(self, template, obj)
        if web.ctx.env.get('HTTP_X_REQUESTED_WITH') == 'XMLHttpRequest':
            return res
        else:
            var = {'content': res, 'HTML': HTML}
            var.update(obj)
            return BaseView.render(self, self.__skeleton__, var)


