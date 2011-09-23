# -*- encoding: utf-8 -*-

from troll import security
from troll import db
from troll.preparedb import prepareDatabase

class Application(object):
    _objects = None
    _views = None
    _permissions = None
    _roles = None
    _sessions = None
    _pool = None
    _conf = None

    def __init__(self, conf):
        self._conf = conf
        self._pool = db.Pool(conf['database']['connect_string'])
        self._objects = [
            security.db.User,
            security.db.Role,
            security.db.Permission,
            security.db.Grant,
            security.db.Session,
        ]
        self._views = {}
        with self._pool.conn() as conn:
            prepareDatabase(
                conn,
                self._objects,
                conf['roles'],
                conf['permissions'],
                conf['grants'],
                conf['salt']
            )
        with self._pool.conn() as conn:
            self._sessions = security.SessionStore(conn)

    def getSession(self, h):
        if h is None:
            return self._sessions.anon
        s = self._sessions.get(h)
        if s is None:
            with self._pool.conn() as conn:
                curs = conn.cursor()
                session = security.db.Session.Broker.fetchone(curs, ('hash', 'eq', h))
                if session is None:
                    s = self._sessions.setanon(h)
                else:
                    user = security.db.User.Broker.fetchone(curs, ('session_id', 'eq', session['id']))
                    if user is None:
                        s = self._sessions.setanon(h)
                    else:
                        s = self._sessions.set(h, Session(conn, user))
        return s

    def registerView(self, view, id, patterns=None):
        assert issubclass(view, IView)
        assert isinstance(id, basestring)
        assert '/' not in id
        assert id not in self._views
        if patterns is None:
            patterns = ('/' + id + '/?',)
        elif isinstance(patterns, basestring):
            patterns = (patterns,)
        elif not isinstance(patterns, tuple):
            patterns = tuple(patterns)
        self._views[id] = {
            'view': view,
            'patterns': patterns
        }

    def run(self):
        pass
