# -*- encoding: utf-8 -*-

import hashlib
import threading

from troll.security import db

class Session(object):
    __slots__ = ('user', 'permissions',)

    def __init__(self, dbconn, user=None):
        if user is None:
            user = db.User()
        self.user = user
        self.permissions = {}

        grants = db.Grant.Broker.fetch(
            dbconn.cursor(),
            ('role_id', 'eq', user['role_id'])
        )
        for grant in grants:
            self.permissions[grant['permission_id']] = True

    def can(self, permission):
        return permission in self.permissions

class SessionStore(threading.local):
    def __init__(self):
        threading.local.__init__(self)
        self._sessions = {}
        self.anon = UserSession()

    def get(self, h):
        return self._sessions.get(h)

    def set(self, h, s):
        self._sessions[h] = s
        return s

    def setanon(self, h):
        self._sessions[h] = self.anon
        return self.anon

def generateNewSession(app, user):
    print "generate new session for user %(login)s (%(id)d)" % user
    conn = app.dbconn()
    curs = conn.cursor()
    session_id = user.session_id
    if session_id:
        db.Session.Broker.delete(curs, ('id', 'eq', session_id))
    valid = False
    base = (app.salt % str(datetime.now())) + user.password
    while not valid:
        h = hashlib.md5(base).hexdigest()
        if db.Session.Broker.fetchone(curs, ('hash', 'eq', h)) is None:
            valid = True
        else:
            base += app.salt % str(datetime.now())
    session = Session({'hash': h})
    db.Session.Broker.insert(curs, session)
    print "session", session.id, 'with hash =', session.hash
    user.session_id = session.id
    db.User.Broker.update(conn.cursor(), user)
    conn.commit()
    return session.hash
