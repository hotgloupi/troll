# -*- encoding: utf-8 -*-

import time
import hashlib

from troll.security import db
from troll.tools import ThreadedDict

class Session(ThreadedDict):
    __slots__ = ('user', 'permissions', 'hash')

    def __init__(self, dbconn, user, hash):
        ThreadedDict.__init__(self)
        self.user = user
        self.hash = hash
        self.permissions = {}

        if dbconn is not None:
            grants = db.Grant.Broker.fetch(
                dbconn.cursor(),
                ('role_id', 'eq', user['role_id'])
            )
            for grant in grants:
                self.permissions[grant['permission_id']] = True

    def can(self, permission):
        return permission in self.permissions

    def clone(self):
        return self.__class__(None, self.user, self.hash)

class SessionStore(object):
    def __init__(self, app):
        self._sessions = ThreadedDict()
        with app.virtual_admin_conn as conn:
            self._anon = Session(conn, db.User(), None)

    def get(self, h):
        return self._sessions.get(h)

    def set(self, h, s):
        self._sessions[h] = s
        return s

    def setanon(self, h):
        s = self._anon.clone()
        s.hash = h
        self._sessions[h] = s
        return s

def generateNewSession(conn, salt, user):
    with conn:
        base = ''
        while True:
            base = salt % (base + str(time.time()))
            h = hashlib.md5(base).hexdigest()
            if db.Session.Broker.fetchone(conn.cursor(), ('hash', 'eq', h)) is None:
                break
        session = db.Session({'hash': h, 'user_id': user.id})
        db.Session.Broker.insert(conn.cursor(), session)
    return session.hash
