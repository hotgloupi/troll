# -*- encoding: utf-8 -*-

from troll import constants

def getConf(base_conf={}):
    roles = {}
    roles.update(constants.ROLES)
    roles.update(base_conf.get('roles', {}))

    permissions = {}
    permissions.update(constants.PERMISSIONS)
    permissions.update(base_conf.get('permissions', {}))

    grants = {}
    grants.update(constants.GRANTS)
    for role, grant in base_conf.get('grants', {}).iteritems():
        base = set(grants.get(role, tuple()))
        grants[role] = tuple(base.union(grant))

    conf = {
        'debug': True,
        'database': {
            'connect_string': 'db.sqlite3',
            'logger_name': 'database',
        },
        'salt': constants.SALT,
        'template_dir': 'templates',
        'encoding': 'utf-8',
    }
    conf.update(base_conf)
    conf.update({
        'roles': roles,
        'permissions': permissions,
        'grants': grants,
    })
    return conf
