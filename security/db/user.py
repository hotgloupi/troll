# -*- encoding: utf-8 -*-

import json

from troll.db.interface import Interface
from troll.db.table import Table
from troll.db.field import Int, String, Mail, Password
from troll.db import broker
from troll.security.db.role import Role

class IUser(Interface):
    id = Int("User id", None, min=1)
    mail = Mail("Mail", 'anon')
    fullname = String("Full name", 'Anonymous', min=1, max=250)
    role_id = String("Associated role", 'anonymous', min=1)
    metadata = String("Json metadata", json.dumps({}))

class User(Table):
    __implements__ = IUser
    __table__ = 'user'
    __primary_keys__ = ('id',)
    __foreign_keys__ = {
        'role_id': Role
    }

    def getMetadata(self):
        return json.loads(self['metadata'])

    def addMetadata(self, key, value):
        raw = self['metadata']
        m = self.getMetadata()
        m[key] = value
        self['metadata'] = json.dumps(m)

