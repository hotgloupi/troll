# -*- encoding: utf-8 -*-

import json

from troll.db.interface import Interface
from troll.db.table import Table
from troll.db.field import Int, String, Date
from troll.security.db.user import User

class IAuthGoogle(Interface):
    user_id = Int("User", None, min=1)
    token_type = String("Token type", None, min=1)
    expiration_date = Date("Expiration date of the access token")
    access_token = String("Access token", None, min=1)
    refresh_token = String("Refresh token", None, min=1)
    metadata = String("User meta data", json.dumps("{}"))

class AuthGoogle(Table):
    __implements__ = IAuthGoogle
    __table__ = 'auth_google'
    __primary_keys__ = tuple()
    __foreign_keys__ = {
        'user_id': User
    }

    @property
    def metadata(self):
        return json.loads(self['metadata'])
