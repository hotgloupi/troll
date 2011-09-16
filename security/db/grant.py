# -*- encoding: utf-8 -*-

from troll.db.interface import Interface
from troll.db.table import Table
from troll.db.field import String

from role import Role
from permission import Permission

class IGrant(Interface):
    role_id = String("Role id to grant", 0, min=1)
    permission_id = String("Permission id for the role", 0, min=1)

class Grant(Table):
    """
        'grant' table is a many to many table to link
        roles to their associated permissions. For
        example, 'manager' role is granted to 'add_user'
        permission.
    """
    __implements__ = IGrant
    __table__ = 'grant'
    __foreign_keys__ = {
        'role_id': Role,
        'permission_id': Permission,
    }
