# -*- encoding: utf-8 -*-

from troll.db.interface import Interface
from troll.db.table import Table
from troll.db.field import Int, String, Mail, Password
from troll.db import broker

from troll.security.db.role import Role

class IUser(Interface):
    id = Int("User id", None, min=1)
    mail = Mail("Mail", 'anon')
    password = Password("Password", '', min=6)
    fullname = String("Full name", 'Anonymous', min=1, max=250)
    role_id = String("Associated role", 'anonymous', min=1)

class User(Table):
    __implements__ = IUser
    __table__ = 'user'
    __primary_keys__ = ('id',)
    __foreign_keys__ = {
        'role_id': Role
    }

    class Broker(broker.Broker):

        @classmethod
        def authenticate(cls, curs, mail, password_hash):
            if not mail or not password_hash:
                return None
            criterias = {
                'conditions': [
                    ('mail', 'eq', mail),
                    ('password', 'eq', password_hash)
                ]
            }
            return cls.fetchone(curs, criterias)

