# -*- encoding: utf-8 -*-

import hashlib

def hashPassword(salt, password):
    return hashlib.md5(salt % password).hexdigest()
