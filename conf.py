# -*- encoding: utf-8 -*-

from troll import constants

def cleanAuth(user_conf):
    roles = {}
    roles.update(constants.ROLES)
    roles.update(user_conf.get('roles', {}))

    permissions = {}
    permissions.update(constants.PERMISSIONS)
    permissions.update(user_conf.get('permissions', {}))

    grants = {}
    grants.update(constants.GRANTS)
    for role, grant in user_conf.get('grants', {}).iteritems():
        base = set(grants.get(role, tuple()))
        grants[role] = tuple(base.union(grant))

    return roles, permissions, grants

def getConf(user_conf={}):
    conf = {
        'debug': True,
        'database': {
            'connect_string': 'db.sqlite3',
            'logger_name': 'database',
        },
        'salt': constants.SALT,
        'template_dir': 'templates',
        'encoding': 'utf-8',
        'logger_store': {
#            'database': 'database.log', #logger for database
        },
        'session_store': {
#            'file': 'sessions.dat' #session file
        },
        'auth': {
#            'local': {},
#            'google': {
#                'client_id': '',
#                'client_secret': '',
#                'redirect_uri': '',
#            },
#            'facebook': {
#                'client_id': '',
#                'client_secret': '',
#                'redirect_uri': '',
#            },
        },
    }
    conf.update(user_conf)

    roles, permissions, grants = cleanAuth(user_conf)
    conf.update({
        'roles': roles,
        'permissions': permissions,
        'grants': grants,
    })
    return conf
