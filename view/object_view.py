# -*- encoding: utf-8 -*-

from troll.view.base_view import BaseView
from troll.view import expose

class ObjectView(BaseView):
    # TODO

    @expose
    def index(self, id=None):
        print id
        return self.app.session.user.fullname


    @expose
    def new(self):
        return 'new'
