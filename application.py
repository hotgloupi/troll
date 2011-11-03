# -*- encoding: utf-8 -*-

import traceback
import web

from troll.conf import getConf
from troll import constants
from troll import db
from troll import security
from troll.view import IView
from troll.preparedb import prepareDatabase
from troll.logger_store import LoggerStore

def makeBoundedViewType(app, ViewType):
    assert issubclass(ViewType, IView)
    class BoundedView(ViewType):
        def __init__(self):
            super(BoundedView, self).__init__(app)
    BoundedView.__name__ = ViewType.__name__
    BoundedView.__module__ = ViewType.__module__
    return BoundedView

class BaseApplication(object):
    _views = None
    _sessions = None
    _conf = None
    _auth_plugins = None
    _logger_store = None
    _is_running = False
    _session_store = None


    @property
    def has_database(self): return False

    @property
    def session_hash(self): return web.cookies().get(constants.SESSION_COOKIE_NAME)

    @session_hash.setter
    def session_hash(self, h): return web.setcookie(constants.SESSION_COOKIE_NAME, h, 999999)

    @property
    def session(self): return self._getSession(self.session_hash)

    @property
    def session_store(self):
        if self._session_store is None:
            self._session_store = security.SessionStore(self)
        return self._session_store

    @property
    def virtual_admin_session(self):
        return self.session_store.generateVirtualSession(
            security.db.User({'mail':'virtual_admin'})
        )

    @property
    def conf(self): return self._conf

    @property
    def logger(self): return self.getLogger('app')

    def getLogger(self, name):
        if self._is_running:
            return self._logger_store.get(name, self.session)
        return self._logger_store.get(name, self.virtual_admin_session)



    def __init__(self, views, objects=tuple(), conf={}):
        self._conf = getConf(conf)
        self._logger_store = LoggerStore(self._conf['logger_store'])
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
        self._auth_plugins = {}
        if 'auth' in self._conf:
            for plugin_name, plugin_conf in self._conf['auth'].iteritems():
                plugin_table, plugin = self.available_auth_plugins[plugin_name]
                self.logger.debug("Register auth plugin: %s" % plugin_name)
                self._objects.append(plugin_table)
                self._auth_plugins[plugin_name] = plugin(plugin_conf)

        for id, view in views.iteritems():
            if not hasattr(view, '__template_dir__') or \
               view.__template_dir__ is None:
                view.__template_dir__ = self._conf['template_dir']
            self._registerView(view, id)



    def _getSession(self, h):
        if h is None:
            s = self.session_store.generateNewSession(
                self._conf['salt'],
                security.db.User()
            )
            self.session_hash = s.hash
        else:
            s = self.session_store.get(h)
        return s

    def getPermissionsFor(self, role='anonymous'):
        return self._conf['grants'][role]


    def _registerView(self, view, id):
        assert isinstance(id, basestring)
        assert id not in self._views
        assert issubclass(view, IView)

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
        urls = []
        views = {}
        for id, view in self._views.iteritems():
            for pattern in view['patterns']:
                urls.extend([pattern, id])
            views[id] = makeBoundedViewType(self, view['view'])

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
        self._is_running = True


        app.run()



class DBApplication(BaseApplication):
    _pool = None

    available_auth_plugins = {
        'local': (security.db.AuthLocal, security.plugins.AuthLocal),
        'google': (security.db.AuthGoogle, security.plugins.AuthGoogle),
        'facebook': (security.db.AuthFacebook, security.plugins.AuthFacebook),
    }

    @property
    def has_database(self): return True

    @property
    def conn(self): return self._pool.getConnection(self.session)

    @property
    def virtual_admin_conn(self):
        return self._pool.getConnection(self.virtual_admin_session)

    def __init__(self, views, objects=tuple(), conf={}, initial_data=[]):
        BaseApplication.__init__(self, views, objects, conf)


        self._initial_data = {
            security.db.Role: [],
            security.db.Permission: [],
            security.db.Grant: [],
        }

        for role_id, description in self._conf['roles'].iteritems():
            self._initial_data[security.db.Role].append(
                security.db.Role({'id': role_id, 'description': description})
            )

        for permission_id, description in self._conf['permissions'].iteritems():
            self._initial_data[security.db.Permission].append(
                security.db.Permission({'id': permission_id, 'description': description})
            )

        for role_id, role_permissions in self._conf['grants'].iteritems():
            assert any(k == role_id for k in self._conf['roles'].iterkeys())
            for permission_id in role_permissions:
                self._initial_data[security.db.Grant].append(
                    security.db.Grant({'role_id': role_id, 'permission_id': permission_id})
                )

        for data in initial_data:
            assert isinstance(data, db.Table)
            assert not isinstance(data, (security.db.Role, security.db.Permission, security.db.Grant))
            slot = self._initial_data.get(data.__class__)
            if slot is None:
                self._initial_data[data.__class__] = slot = []
            slot.append(data)


        db_conf = self._conf['database']
        assert db_conf is not None
        self._pool = db.Pool(db_conf, self._logger_store)

    def authenticate(self, mail, password):
        return self.authenticateWith('local', login=mail, password=password)

    def authenticateWith(self, auth_plugin, *args, **kwargs):
        plugin = self._auth_plugins.get(auth_plugin)
        if plugin is None:
            raise Exception("Authentication plugin '%s' not found" % str(auth_plugin))
        try:
            res = plugin.authenticate(self, *args, **kwargs)
            if res is None: raise Exception("Wrong plugin response")
        except Exception, e:
            traceback.print_exc()
            return {
                'success': False,
                'error': "Plugin '%s' error: %s" % (str(auth_plugin), str(e)),
            }
        if res['success'] is False:
            return res

        auth, user = res['auth'], res['user']
        with self.conn as conn:
            existing_user = user.Broker.fetchone(
                conn.cursor(),
                ('mail', 'eq', user.mail)
            )
            if existing_user is not None:
                user = existing_user
                user.addMetadata(auth_plugin, auth.metadata)
                user.Broker.update(conn.cursor(), user)
            else:
                user.addMetadata(auth_plugin, auth.metadata)
                user.Broker.insert(conn.cursor(), user)

            assert user.id is not None
            auth.user_id = user.id
            auth.Broker.insert(conn.cursor(), auth)

        s = self.session_store.generateNewSession(self._conf['salt'], user)
        res['session'] = s
        self.session_hash = res['hash'] = s.hash
        return res

    def logout(self):
        h = self.session_hash
        if h and self.session.user.id:
            with self.conn as conn:
                security.db.Session.Broker.delete(
                    conn.cursor(),
                    ('hash', 'eq', h)
                )
            web.setcookie(constants.SESSION_COOKIE_NAME, '', 3600)

    def run(self):
        with self.virtual_admin_conn as conn:
            prepareDatabase(
                conn,
                self._objects,
                self._conf['salt'],
                self._initial_data,
                True
            )
        BaseApplication.run(self)


def Application(views, objects=[], conf={}, initial_data=[]):
    conf = getConf(conf)
    if conf.get('database') is None:
        return BaseApplication(views, objects=objects, conf=conf)
    else:
        return DBApplication(views, objects=objects, conf=conf, initial_data=initial_data)
