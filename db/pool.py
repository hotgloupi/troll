# -*- encoding: utf-8 -*-

import sqlite3

class Cursor(sqlite3.Cursor):

    def __init__(self, conn, logger):
        sqlite3.Cursor.__init__(self, conn)
        self._logger = logger

    def execute(self, req, params=tuple()):
        msg = req.strip() + ' ' + str(params)
        self._logger.debug(msg)
        return sqlite3.Cursor.execute(self, req, params)

class Connection(sqlite3.Connection):

    def __init__(self, connect_string, logger):
        sqlite3.Connection.__init__(self, connect_string)
        self.logger = logger

    def cursor(self):
        return Cursor(self, self.logger)

    def hasTable(self, table_name):
        curs = self.cursor()
        res = curs.execute(
            "SELECT name FROM sqlite_master" \
            " WHERE type = 'table' AND name = ?",
            (table_name,)
        )
        return res.fetchone() is not None

class Pool(object):

    # XXX TODO
    def __init__(self, conf, logger_store):
        self._connect_string = conf['connect_string']
        self._logger_store = logger_store
        self._logger_name = conf.get('logger_name', 'database')

    def getConnection(self, session):
        logger = self._logger_store.get(self._logger_name, session)
        return Connection(self._connect_string, logger)
