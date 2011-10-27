# -*- encoding: utf-8 -*-

import web

from troll.security import db
from troll.security.password import hashPassword

class AuthLocal(object):

    def __init__(self, conf):

        pass

    def authenticate(self, app, **kwargs):
        i = web.input()
        login = kwargs.get('login', i.get('login'))
        password = kwargs.get('password', i.get('password'))
        if login and password:
            password_hash = hashPassword(app.conf['salt'], password)
            with app.virtual_admin_conn as conn:
                user = db.User.Broker.fetchone(conn.cursor(), ('mail', 'eq', login))
                if user is not None:
                    assert user.id is not None
                    auth = db.AuthLocal.Broker.fetchone(conn.cursor(), [
                        ('user_id', 'eq', user.id),
                        ('password', 'eq', password_hash),
                    ])
                    if auth is not None:
                        return {
                            'success': True,
                            'user': user,
                            'auth': auth,
                        }
        return {
            'success': False,
            'error': 'Wrong login / password',
        }

