# -*- encoding: utf-8 -*-

from troll.db.interface import Interface
from troll.db.table import Table
from troll.db.field import Int, String

class ISession(Interface):
    id = Int("Session id", None, min=1)
    hash = String("Session hash", '', min=0, max=50)


class Session(Table):
    __implements__ = ISession
    __table__ = 'session'
    __primary_keys__ = ('id',)
