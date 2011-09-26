# -*- encoding: utf-8 -*-

import web

from troll import constants
from troll import db
from troll import security
from troll.view import BaseView, ObjectView
from troll.preparedb import prepareDatabase

class Application(object):
    _views = None
    _sessions = None
    _pool = None
    _conf = None

    @property
    def pool(self): return self._pool

    @property
    def session_hash(self):
        return web.cookies().get(constants.SESSION_COOKIE_NAME)
    @session_hash.setter
    def session_hash(self, h):
        web.setcookie(constants.SESSION_COOKIE_NAME, h, 3600)

    @property
    def session(self): return self._getSession(self.session_hash)

    @property
    def conf(self): return self._conf

    def __init__(self, conf, views, objects):
        self._conf = conf
        self._pool = db.Pool(conf['database']['connect_string'])
        self._objects = [
            security.db.User,
            security.db.Role,
            security.db.Permission,
            security.db.Grant,
            security.db.Session,
        ]
        assert hasattr(objects, '__iter__')
        self._objects.extend(objects)
        self._views = {}

        for id, view in views.iteritems():
            if view.__template_dir__ is None:
                view.__template_dir__ = self._conf['template_dir']
            self._registerView(view, id)

    def authenticate(self, mail, password):
        password_hash = security.password.hashPassword(self._conf['salt'], password)
        with self._pool.conn() as conn:
            user = security.db.User.Broker.fetchone(conn.cursor(), ('mail', 'eq', mail))
            if not user:
                return False
            success = security.db.User.Broker.authenticate(conn.cursor(), mail, password_hash)
        if success:
            h = security.session.generateNewSession(self, user)
            session = self._getSession(h)
            self.session_hash = h
            print "set", constants.SESSION_COOKIE_NAME, "to", h
        return success

    def logout(self):
        h = self.session_hash
        if h and self.session.user.id:
            with self._pool.conn() as conn:
                security.db.Session.Broker.delete(
                    conn.cursor(),
                    ('hash', 'eq', h)
                )
            web.setcookie(constants.SESSION_COOKIE_NAME, '', 3600)

    def _getSession(self, h):
        print "get session for", h
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
                    user = security.db.User.Broker.fetchone(
                        curs, ('id', 'eq', session.user_id)
                    )
                    if user is None:
                        s = self._sessions.setanon(h)
                    else:
                        s = self._sessions.set(h, security.session.Session(conn, user))
        print "got", s
        return s


    def _registerView(self, view, id):
        assert isinstance(id, basestring)
        assert id not in self._views

        exposed_methods = view.getExposedMethods()
        patterns = set([])
        for name, descr in exposed_methods.iteritems():
            if id:
                base = '/' + id
            else:
                base = ''
            if name != 'index':
                base += '/(' + name + ')'
            nb_fixed = len(descr['args']) - len(descr['defaults']) - 1
            assert nb_fixed >= 0
            base += '/([^/]+)' * nb_fixed
            patterns.add(base + '/?')
            for n in range(len(descr['defaults'])):
                patterns.add(base + '/([^/]+)' * (n + 1) + '/?')

        self._views[id] = {
            'view': view,
            'patterns': tuple(patterns)
        }

    def run(self):
        with self._pool.conn() as conn:
            prepareDatabase(
                conn,
                self._objects,
                self._conf['roles'],
                self._conf['permissions'],
                self._conf['grants'],
                self._conf['salt']
            )
        self._sessions = security.SessionStore(self)
        urls = []
        views = {}
        for id, view in self._views.iteritems():
            for pattern in view['patterns']:
                urls.extend([pattern, id])

            assert issubclass(view['view'], BaseView)
            assert hasattr(view['view'], '__template_dir__')

            class View(view['view']):
                _app = self
                @property
                def app(self): return self._app


            views[id] = View

        web.config.debug = self._conf['debug']
        if not urls:
            raise Exception("No Url registered")
        elif not views:
            raise Exception("No views registered")
        it = iter(urls)
        print "Published urls:"
        for url in it:
            print "    - '%s'" % url
            it.next()
        app = web.application(urls, views)
        if self._conf['debug']:
            app.internalerror = web.debugerror

        # enable fastcgi
        #web.wsgi.runwsgi = lambda func, addr=None: web.wsgi.runfcgi(func, addr)
        print
        app.run()

