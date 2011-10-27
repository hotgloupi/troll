# -*- encoding: utf-8 -*-

from troll.db.interface import Interface
from troll.db.table import makeTable
from troll.db.field import Int, String
from troll.security.db.user import User

class IAuthLocal(Interface):
    user_id = Int("User", None, min=1)
    password = String("password", None, min=1)

AuthLocal = makeTable(IAuthLocal, 'auth_local', tuple(), {
    'user_id': User,
})
