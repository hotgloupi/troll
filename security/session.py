# -*- encoding: utf-8 -*-

import os
import pickle
import time
import hashlib
import threading
import web

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
    def __str__(self):
        return "<Session %s for %s: %s>" % (
            self.hash, self.user.mail, ThreadedDict.__str__(self)
        )

class SessionStore(object):
    """
        Manage sessions
    """


    def __init__(self, app):
        self._conf = app.conf.get('session_store', {})
        self._sessions_file = self._conf.get('file')
        self._sessions = ThreadedDict()
        self._app = app
        if self._sessions_file is not None:
            if os.path.exists(self._sessions_file):
                try:
                    with open(self._sessions_file, 'r') as f:
                        res = pickle.load(f)
                    for h, data in res.iteritems():
                        self._reloadSession(h, db.User(data[0]), data[1], data[2])
                except:
                    pass

        self._anon = self._reloadSession(
            'anon_token', db.User(),
            self._app.getPermissionsFor('anonymous')
        )
        self._last_save = None

    def save(self):
        self._saveSession()

    def _saveSession(self):
        if self._sessions_file is None:
            return
        if self._last_save is None or \
           self._last_save - time.time() > 1:
            def getFields(s):
                is_ok = lambda v: any(isinstance(v, t) for t in [basestring, int, float])
                return filter(lambda i: is_ok(i[0]) and is_ok(i[1]), s.iteritems())
            sessions = dict(
                (h, (dict(s.user), s.permissions, getFields(s)))
                for h, s in self._sessions.iteritems()
            )
            with open(self._sessions_file, 'wb') as f:
                res = pickle.dump(sessions, f)

    def _reloadSession(self, h, user, permissions, fields={}):
        s = self._sessions[h] = _Session(h, user, permissions)
        s.update(fields)
        return s

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
        self._saveSession()

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
        self._saveSession()
        return s
