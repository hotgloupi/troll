# -*- encoding: utf-8 -*-

class Broker(object):

    # override this
    __type__ = None

    __operators__ = {
        'and': 'AND',
        'or': 'OR',
        'eq': '=',
        'neq': '!=',
        'not': 'NOT',
    }


    """
    criterias = {
        'conditions': [
            ('id', 'eq', '12'),
            'or',
            ('login', 'neq', 'bite'),
        ]
        'sort': [
            ('login', True),    # descending == True
            'id'                # <> ('id', True)
        ]
    }
    """
    @classmethod
    def fetch(cls, curs, criterias={}, columns=None, _type=None):
        if _type is None:
            _type = cls.__type__
        assert _type is not None
        if columns is None:
            columns = tuple(f.name for f in _type.__fields__)
        table_name = _type.__table__
        req = "SELECT %s FROM %s" % (
            ', '.join((table_name + '.' + f) for f in columns),
            table_name
        )

        params = None
        conditions = cls._getConditions(criterias)
        if conditions:
            conditions_string, params = cls._parseConditions(conditions, _type)
            req += conditions_string
        sortstring = lambda f, d: table_name + '.' + f + (d and ' DESC' or ' ASC')
        sort_fields = [sortstring(f, d) for f, d in cls._getSort(criterias)]
        if sort_fields:
            req += ' ORDER BY ' + ', '.join(sort_fields)
        print req, params or []
        if params is not None:
            curs.execute(req, tuple(params))
        else:
            curs.execute(req)
        for row in curs:
            yield _type(dict(zip(columns, row)))

    @classmethod
    def fetchone(cls, curs, criterias, columns=None, _type=None):
        gen = cls.fetch(curs, criterias, columns, _type)
        try:
            res = gen.next()
        except StopIteration:
            res = None
        return res

    @classmethod
    def insert(cls, curs, obj, _type=None):
        if _type is None:
            _type = cls.__type__
        if not isinstance(obj, _type):
            obj = _type(obj)
        req = "INSERT INTO %s (%s) VALUES (%s)" % (
            _type.__table__,
            ', '.join(f.name for f in _type.__fields__),
            ', '.join('?' * len(_type.__fields__))
        )
        values = tuple(obj[f.name] for f in _type.__fields__)
        print req, values
        curs.execute(req, values)
        if len(_type.__primary_keys__) == 1:
            pkey = _type.__primary_keys__[0]
            obj[pkey] = curs.lastrowid

    @classmethod
    def delete(cls, curs, criterias={}, _type=None):
        if _type is None:
            _type = cls.__type__
        req = "DELETE FROM %s " % _type.__table__
        conditions = cls._getConditions(criterias)
        conditions_string, params = cls._parseConditions(conditions, _type)
        req += conditions_string
        print req, params
        curs.execute(req, params)

    @classmethod
    def update(cls, curs, obj, _type=None):
        if _type is None:
            _type = cls.__type__
        assert len(_type.__primary_keys__)
        columns = obj.getDirtyFields()
        if not len(columns):
            return
        req = "UPDATE %s SET %s WHERE %s" % (
            _type.__table__,
            ', '.join(k + ' = ?' for k in columns),
            ' AND '.join(k + ' = ?' for k in _type.__primary_keys__)
        )
        params = tuple(obj[k] for k in columns)
        params += tuple(obj[k] for k in _type.__primary_keys__)
        print req, params
        curs.execute(req, params)

    @classmethod
    def _parseConditions(cls, conditions, _type):
        if not conditions:
            return ('', tuple())
        params = None
        conditions_strings = []
        has_operator = True
        params = []
        for c in conditions:
            if isinstance(c, tuple):
                if not has_operator:
                    conditions_strings.append('AND')
                if '.' not in c[0]:
                    conditions_strings.append(_type.__table__ + '.' + c[0])
                else:
                    # XXX jointures ici c[0].split('.')[0]
                    conditions_strings.append(c[0])
                has_operator = False
                conditions_strings.append(cls.__operators__[c[1]])
                conditions_strings.append('?')
                params.append(c[2])
            elif isinstance(c, basestring):
                conditions_strings.append(cls.__operators__[c])
                has_operator = True
            else:
                raise Exception("Unknown condition type '%s'" % str(c))
        return (" WHERE " + ' '.join(conditions_strings), params)

    @classmethod
    def _getConditions(cls, criterias):
        if criterias is None:
            return None
        if isinstance(criterias, tuple):
            return [criterias]
        elif isinstance(criterias, list):
            return criterias
        else:
            return criterias.get('conditions')

    @classmethod
    def _getSort(cls, criterias):
        if not isinstance(criterias, dict):
            return
        s = criterias.get('sort')
        if isinstance(s, basestring):
            yield (s, False)
        elif isinstance(s, tuple):
            assert len(s) == 2
            yield s
        elif isinstance(s, list):
            for e in s:
                if isinstance(e, basestring):
                    yield (e, False)
                elif isinstance(e, tuple):
                    assert len(e) == 2
                    yield e




def makeBroker(_type):
    class _Broker(Broker):
        __type__ = _type
    return _Broker
