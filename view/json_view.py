# -*- encoding: utf-8 -*-

import json
import web

from troll.view.abstract_view import AbstractView

class JsonView(AbstractView):

    def render(self, obj):
        web.header('Content-Type', 'text/plain') #because adblock add some dirty stuff
        #web.header('Content-Type', 'application/json')
        return json.dumps(obj)

