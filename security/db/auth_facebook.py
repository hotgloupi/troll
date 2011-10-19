# -*- encoding: utf-8 -*-

from troll.db.interface import Interface
from troll.db.table import makeTable
from troll.db.field import Int, String, Date

from troll.security.db.user import User

class IAuthFacebook(Interface):
    user_id = Int("User", None, min=1)
    expiration_date = Date("Expiration date of the access token")
    access_token = String("Access token", None, min=1)

AuthFacebook = makeTable(IAuthFacebook, 'auth_facebook', tuple(), {
    'user_id': User,
})
