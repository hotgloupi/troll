# -*- encoding: utf-8 -*-

import time
import hashlib

from troll.security import db
from troll.tools import ThreadedDict

class _Session(ThreadedDict):
    """
        Internaly created session class.
    """
    __slots__ = ('user', 'permissions', 'hash')

    def __init__(self, hash, user, permissions):
        ThreadedDict.__init__(self)
        self.user = user
        self.hash = hash
        self.permissions = permissions

    def can(self, permission):
        return permission in self.permissions

class SessionStore(object):
    """
        Manage sessions
    """


    def __init__(self, app):
        self._sessions = ThreadedDict()
        self._app = app
        user = db.User()
        self._anon = self._insertSession('anon_token', user)

    def get(self, h):
        assert isinstance(h, basestring)
        s = self._sessions.get(h)
        if s is not None:
            return s
        elif self._app.has_database:
            with self._app.virtual_admin_conn as conn:
                session = db.Session.Broker.fetchone(conn.cursor(), ('hash', 'eq', h))
                if session is not None and session.user_id is not None:
                    user = db.User.Broker.fetchone(
                        conn.cursor(), ('id', 'eq', session.user_id)
                    )
                    if user is not None:
                        return self._insertSession(h, user)

        return self._anon

    def delete(self, h):
        del self._sessions[h]

    def setUserSession(self, session, user):
        assert session.hash in self._sessions
        session.permissions = self._app.getPermissionsFor(user.role_id)
        session.user = user

    def generateVirtualSession(self, user):
        return _Session(None, user, None)

    def generateNewSession(self, salt, user):
        if self._app.has_database:
            h = self._generateNewSessionWithDb(salt, user)
        else:
            h = self._generateNewSession(salt)
        s = self._insertSession(h, user)
        return s

    def _generateNewSession(self, salt):
        base = ''
        while True:
            base = salt % (base + str(time.time()))
            h = hashlib.md5(base).hexdigest()
            if self._sessions.get(h) is None:
                return h

    def _generateNewSessionWithDb(self, salt, user):
        with self._app.virtual_admin_conn as conn:
            while True:
                h = self._generateNewSession(salt)
                if db.Session.Broker.fetchone(conn.cursor(), ('hash', 'eq', h)) is None:
                    break
            db.Session.Broker.insert(conn.cursor(), db.Session({'hash': h, 'user_id': user.id}))
        return h


    def _insertSession(self, h, user):
        self._sessions[h] = s = _Session(h, user, self._app.getPermissionsFor(user.role_id))
        return s
