# -*- encoding: utf-8 -*-

from troll.db.interface import Interface
from troll.db.table import Table
from troll.db.field import String

class IRole(Interface):
    id = String("Role id", 0, min=1)
    description = String("Role name", min=1, max=50)

class Role(Table):
    """
        'role' table contains all user class, from
        'anonymous' to 'administrator'.
    """
    __implements__ = IRole
    __table__ = 'role'
    __primary_keys__ = ('id',)
