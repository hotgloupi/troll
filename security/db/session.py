# -*- encoding: utf-8 -*-

from troll.db.interface import Interface
from troll.db.table import Table
from troll.db.field import Int, String

from troll.security.db.user import User

class ISession(Interface):
    user_id = Int("Session id", None, min=1)
    hash = String("Session hash", '', min=0, max=50)


class Session(Table):
    __implements__ = ISession
    __table__ = 'session'
    __primary_keys__ = ()
    __foreign_keys__ = {
        'user_id': User
    }
