# -*- encoding: utf-8 -*-

import hashlib

def hashPassword(app, password):
    return hashlib.md5(app.salt % password).hexdigest()
