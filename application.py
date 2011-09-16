# -*- encoding: utf-8 -*-

from troll.security.session import Session, SessionStore
from troll.security import db

class Application(object):
    _objects = None
    _views = None
    _permissions = None
    _roles = None
    _sessions = None

    def __init__(self, dbconnector):
        assert dbconnector is not None
        self.dbconn = dbconnector
        self._sessions = SessionStore()
        self._objects = [
            db.User,
            db.Role,
            db.Permission,
            db.Grant,
            db.Session,
        ]

    def getSession(self, h):
        if h is None:
            return self._sessions.anon
        s = self._sessions.get(h)
        if s is None:
            curs = self.dbconn().cursor()
            session = db.Session.Broker.fetchone(curs, ('hash', 'eq', h))
            if session is None:
                s = self._sessions.setanon(h)
            else:
                user = db.User.Broker.fetchone(curs, ('session_id', 'eq', session['id']))
                if user is None:
                    s = self._sessions.setanon(h)
                else:
                    s = self._sessions.set(h, Session(self.dbconn(), user))
        return s
