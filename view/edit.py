# -*- encoding: utf-8 -*-

from troll.view.base_view import BaseView
from troll.view.interface import IEditView

class Edit(BaseView, IEditView):
    def __init__(self, fields):
        self._fields = fields
