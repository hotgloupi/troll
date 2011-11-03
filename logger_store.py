# -*- encoding: utf-8 -*-

import logging

from troll.tools import ThreadedDict

class LoggerStore(object):
    """

    """

    _format = '[%(levelname)s][%(name)s] %(user)s(%(user_id)d): %(message)s'

    def __init__(self, conf):
        self._loggers = ThreadedDict()
        self._conf = conf
        print 'logger store conf', conf

    def get(self, name, session):
        assert isinstance(name, basestring)
        logger = self._loggers.get(name)
        if logger is None:
            self._loggers[name] = logger = self._buildNew(name)
        return logging.LoggerAdapter(logger, {
            'user': session.user.mail,
            'user_id': session.user.id or 0,
        })

    def _buildNew(self, name):
        conf = self._conf.get(name)
        logger = logging.Logger(name)
        formatter = logging.Formatter(self._format)
        if isinstance(conf, basestring):
            print 'LOGGER',name,'log to', conf
            handler = logging.FileHandler(conf)
        else:
            handler = logging.StreamHandler()
        handler.setFormatter(formatter)
        logger.addHandler(handler)
        return logger

