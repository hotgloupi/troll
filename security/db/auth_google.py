# -*- encoding: utf-8 -*-

from troll.db.interface import Interface
from troll.db.table import makeTable
from troll.db.field import Int, String, Date

from troll.security.db.user import User

class IAuthGoogle(Interface):
    user_id = Int("User", None, min=1)
    token_type = String("Token type", None, min=1)
    expiration_date = Date("Expiration date of the access token")
    access_token = String("Access token", None, min=1)
    refresh_token = String("Refresh token", None, min=1)

AuthGoogle = makeTable(IAuthGoogle, 'auth_google', tuple(), {
    'user_id': User,
})
