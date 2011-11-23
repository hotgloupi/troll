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
        'startswith': lambda val: ('LIKE', val + u'%'),
        'endswith': lambda val: ('LIKE', u'%' + val),
        'contains': lambda val: ('LIKE', u'%' + val + u'%'),
        'istartswith': lambda val: ('ILIKE', val + u'%'),
        'iendswith': lambda val: ('ILIKE', u'%' + val),
        'icontains': lambda val: ('ILIKE', u'%' + val + u'%'),
        'in': lambda values: ('IN', tuple(values)),
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
            'id'                # <> ('id', False)
        ],
        'limit': 12,
        'offset': 15,
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

        limit = cls._getLimit(criterias)
        if limit:
            req += ' LIMIT %d' % int(limit)
        offset = cls._getOffset(criterias)
        if offset:
            req += ' OFFSET %d' % int(offset)
        print 'REQ', req
        if params is not None:
            curs.execute(req, tuple(params))
        else:
            curs.execute(req)
        for row in curs:
            yield _type(dict(zip(columns, row)))

    @classmethod
    def count(cls, curs, criterias={}, _type=None):
        if _type is None:
            _type = cls.__type__
        assert _type is not None
        req = "SELECT COUNT(*) FROM %s" % _type.__table__
        conditions = cls._getConditions(criterias)
        params = None
        if conditions:
            cond_string, params = cls._parseConditions(conditions, _type)
            req += cond_string
        if params is not None:
            curs.execute(req, tuple(params))
        else:
            curs.execute(req)
        return curs.fetchone()[0]

    @classmethod
    def fetchone(cls, curs, criterias={}, columns=None, _type=None):
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
                    if c[0] not in _type.__fields_by_name__:
                        raise Exception("Unknown field '%s' for table '%s'" % (str(c[0]), _type.__table__))
                    conditions_strings.append(_type.__table__ + '.' + c[0])
                else:
                    raise NotImplemented()
                    # XXX jointures ici c[0].split('.')[0]
                    conditions_strings.append(c[0])
                has_operator = False
                op = cls.__operators__[c[1]]
                if isinstance(op, basestring):
                    conditions_strings.extend([op, '?'])
                    params.append(c[2])
                else:
                    op, param = op(c[2])
                    if isinstance(param, tuple):
                        params.extend(param)
                        conditions_strings.extend([op, '(' + ','.join('?'*len(param)) + ')'])
                    else:
                        params.append(param)
                        conditions_strings.extend([op, '?'])
            elif isinstance(c, basestring):
                conditions_strings.append(cls.__operators__[c])
                has_operator = True
            else:
                raise Exception("Unknown condition type '%s'" % str(c))
        return (" WHERE " + ' '.join(conditions_strings), params)

    @classmethod
    def _getLimit(cls, criterias):
        if isinstance(criterias, dict):
            return criterias.get('limit')
        return None

    @classmethod
    def _getOffset(cls, criterias):
        if isinstance(criterias, dict):
            return criterias.get('offset')
        return None

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
                elif isinstance(e, (list, tuple)):
                    assert len(e) == 2
                    yield e




def makeBroker(_type):
    class _Broker(Broker):
        __type__ = _type
    return _Broker
