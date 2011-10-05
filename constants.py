# -*- encoding: utf-8 -*-

import os
ROOT_DIR = os.path.abspath(os.path.dirname(__file__))
TEMPLATE_DIR = os.path.join(ROOT_DIR, 'templates')
SALT = "This is a TRoll SALT '%s'"

SESSION_COOKIE_NAME = "SESSION_ID"

ROLES = {
    'anonymous': 'Not logged in user',
    'user': 'Normal web site user',
    'manager': 'Site web manager',
    'administrator': 'Site web administrator',
}

PERMISSIONS = {
    'login': 'Possibility to log in',
    'logout': 'Log out',
    'subscribe': 'Subscribe',
    'unsubscribe': 'Unsubscribe',
    'manage': 'General managment permission',

    'add_role': 'Add role',
    'del_role': 'Delete role',
    'mod_role': 'Modify role',

    'add_permission': 'Add permission',
    'del_permission': 'Delete permission',
    'mod_permission': 'Modify permission',

    'add_grant': 'Add grant',
    'del_grant': 'Delete grant',
    'mod_grant': 'Modify grant',

    'add_user': 'Add user',
    'del_user': 'Delete user',
    'mod_user': 'Modify user',
}

GRANTS = {
    'anonymous': ('login', 'subscribe'),
    'user': ('logout', 'unsubscribe'),
    'manager': (
        'logout', 'unsubscribe', 'manage',
    ),
    'administrator': (
        'logout', 'manage',
        'add_user', 'del_user', 'mod_user',
    ),
}

