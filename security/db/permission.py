# -*- encoding: utf-8 -*-

from troll.db.interface import Interface
from troll.db.table import Table
from troll.db.field import Int, String

class IPermission(Interface):
    id = String("Permission name", min=1)
    description = String("Permission description", max=250)

class Permission(Table):
    """
        'permission' table contains all possible
        action available on the web site, like 'del_user'.
    """
    __implements__ = IPermission
    __table__ = 'permission'
    __primary_keys__ = ('id',)
