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

    conf = {}
    conf.update(base_conf)
    conf.update({
        'debug': base_conf.get('debug', True),
        'database': base_conf.get('database', {'connect_string': 'db.sqlite3'}),
        'salt': base_conf.get('salt', constants.SALT),
        'roles': roles,
        'permissions': permissions,
        'grants': grants,
        'template_dir': base_conf.get('template_dir', 'templates'),
        'encoding': base_conf.get('encoding', 'utf-8'),
    })
    return conf
