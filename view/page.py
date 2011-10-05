# -*- encoding: utf-8 -*-

import web
from genshi import HTML

from html_view import HTMLView
from expose import expose

class Page(HTMLView):

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
        res = super(Page, self).render(template, obj)
        if web.ctx.env.get('HTTP_X_REQUESTED_WITH') == 'XMLHttpRequest':
            return res
        else:
            var = {'content': HTML(res)}
            var.update(obj)
            return super(Page, self).render(self.__skeleton__, var)


