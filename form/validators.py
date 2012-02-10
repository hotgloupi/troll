# -*- encoding: utf-8 -*-

import re

class Validator:
    def __init__(self, test, msg=None):
        self.test = test
        self.msg = msg

    def __call__(self, value):
        try: return self.test(value)
        except: return False

NotNull = Validator(lambda v: bool(v.strip()), "Required")

class Regexp(Validator):
    def __init__(self, rexp, msg=None):
        self.rexp = re.compile(rexp)
        self.msg = msg

    def __call__(self, value):
        return bool(self.rexp.match(value))

Email = Regexp(r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,5}$', "Not a valid email")
