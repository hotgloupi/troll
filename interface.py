# -*- encoding: utf-8 -*-

class Interface(object):
    pass

def getInterfaces(obj):
    def rec(node, bases):
        #print "on node", node, isinstance(node, Interface)
        if node == Interface:
            return True
        if any([rec(parent, bases) for parent in node.__bases__]):
            bases.append(node)
            return True
        return False
    bases = []
    if not isinstance(obj, type):
        obj = obj.__class__
    rec(obj, bases)
    return bases

