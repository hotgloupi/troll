# -*- encoding: utf-8 -*-

from troll import db
from troll.security.db import Role, Permission, Grant, User, AuthLocal
from troll.security.password import hashPassword

fields_create = {
    db.field.Int: "INTEGER",
    db.field.Float: "FLOAT",
    db.field.String: "TEXT",
    db.field.Mail: "TEXT",
    db.field.Date: "TIMESTAMP",
    db.field.Bool: "BOOL",
    db.field.Password: "TEXT",
    db.field.Text: "TEXT",
}

def prepareClass(conn, cls, initial_data):
    is_new = False
    if not conn.hasTable(cls.__table__):
        req = "CREATE TABLE %s (%s)"
        fields = []
        for f in cls.__fields__:
            s = fields_create[f.__class__]
            fields.append(f.name + ' ' + s)
            if f.name in cls.__primary_keys__:
                fields[-1] += ' PRIMARY KEY'
        req = req % (cls.__table__, ', '.join(fields))
        conn.cursor().execute(req)
        is_new = True
    if is_new:
        for data in initial_data:
            cls.Broker.insert(conn.cursor(), data)

def prepareDatabase(conn, classes, salt, initial_data, need_admin):
    for cls in classes:
        prepareClass(conn, cls, initial_data.get(cls, []))

    if not need_admin:
        return
    admin = User.Broker.fetchone(conn.cursor(), ('mail', 'eq', 'admin'))
    if admin is None:
        print "You need to create 'admin' account"
        from getpass import getpass
        wrong = True
        while wrong:
            password = getpass("Enter the new password: ")
            if len(password) < 6:
                print "password too short"
                continue
            confirm = getpass("Repeat the new password: ")
            if confirm != password:
                print "passwords do not match"
                continue
            password = hashPassword(salt, password)
            confirm = None
            wrong = False
        admin = User({
            'fullname': 'Administrator',
            'mail': 'admin',
            'role_id': 'administrator',
        })
        User.Broker.insert(conn.cursor(), admin)
        assert admin.id is not None
        AuthLocal.Broker.insert(conn.cursor(), AuthLocal({
            'user_id': admin.id,
            'password': password,
        }))

    else:
        conn.logger.debug("'admin' account already there")

