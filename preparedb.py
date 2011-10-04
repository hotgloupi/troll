# -*- encoding: utf-8 -*-

from troll import db
from troll.security.db import Role, Permission, Grant, User
from troll.security.password import hashPassword

fields_create = (
    (db.field.Int, "INTEGER"),
    (db.field.String, "TEXT"),
    (db.field.Mail, "TEXT"),
    (db.field.Date, "TIMESTAMP"),
    (db.field.Bool, "BOOL"),
)

def prepareClass(conn, cls):
    curs = conn.cursor()
    req = "CREATE TABLE %s (%s)"
    fields = []
    for f in cls.__fields__:
        for t, s in fields_create:
            if isinstance(f, t):
                fields.append(f.name + ' ' + s)
                if f.name in cls.__primary_keys__:
                    fields[-1] += ' PRIMARY KEY'
                break
    try:
        req = req % (cls.__table__, ', '.join(fields))
        #print "Create table '%s' with '%s'" % (cls.__table__, req)
        curs.execute(req)
    except Exception, e:
        print "  => Cannot create table '%s': %s" % (cls.__table__, e)
    else:
        print "  => Created"

def prepareDatabase(conn, classes, roles, permissions, grants, salt):
    for cls in classes:
        prepareClass(conn, cls)
    conn.commit()

    curs = conn.cursor()
    for id, description in roles.iteritems():
        curs.execute("SELECT 1 FROM role WHERE id = ?", (id,))
        if not curs.fetchone():
            role = Role({'id':id, 'description': description})
            Role.Broker.insert(curs, role)
            print "  => Role '%s' inserted" % id

    for id, description in permissions.iteritems():
        curs.execute("SELECT 1 FROM permission WHERE id = ?", (id,))
        if not curs.fetchone():
            permission = Permission({'id': id, 'description': description})
            Permission.Broker.insert(curs, permission)
            print "  => Permission '%s' inserted" % id

    for role, role_permissions in grants.iteritems():
        assert isinstance(role_permissions, tuple)
        curs.execute("SELECT 1 FROM role WHERE id = ?", (role,))
        if curs.fetchone() is None:
            raise Exception("Unknown role '%s'" % str(role))
        for permission in role_permissions:
            curs.execute("SELECT 1 FROM permission WHERE id = ?", (permission,))
            if curs.fetchone() is None:
                raise Exception("Unkown permission '%s'" % str(permission))
            curs.execute("""
                SELECT 1 FROM grant WHERE role_id = ? AND permission_id = ?
            """, (role, permission))
            if curs.fetchone() is None:
                print " => '%s can %s'" % (role, permission)
                grant = Grant({'role_id': role, 'permission_id': permission})
                Grant.Broker.insert(curs, grant)

    admin = User.Broker.fetchone(curs, {'conditions':[('mail', 'eq', 'admin')]}, columns=['id'])
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
            'password': password,
            'role_id': 'administrator',
        })
        User.Broker.insert(conn.cursor(), admin)
    else:
        print "  => 'admin' account already there"

    conn.commit()


