# -*- encoding: utf-8 -*-

from datetime import datetime
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
    def __init__(self, app):
        print "Init SessionStore"
        threading.local.__init__(self)
        self._sessions = {}
        with app.pool.conn() as conn:
            self.anon = Session(conn)

    def get(self, h):
        return self._sessions.get(h)

    def set(self, h, s):
        self._sessions[h] = s
        return s

    def setanon(self, h):
        self._sessions[h] = self.anon
        return self.anon

def generateNewSession(app, user):
    print "generate new session for user %(mail)s (%(id)d)" % user
    with app.pool.conn() as conn:
        curs = conn.cursor()
        valid = False
        salt = app.conf['salt']
        base = (salt % str(datetime.now())) + user.password
        while not valid:
            h = hashlib.md5(base).hexdigest()
            if db.Session.Broker.fetchone(curs, ('hash', 'eq', h)) is None:
                valid = True
            else:
                base += salt % str(datetime.now())
            session = db.Session({'hash': h, 'user_id': user.id})
        db.Session.Broker.insert(curs, session)
        conn.commit()
    return session.hash
