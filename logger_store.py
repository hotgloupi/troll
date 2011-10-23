# -*- encoding: utf-8 -*-

import logging

from troll.tools import ThreadedDict

class LoggerStore(object):
    """

    """

    _format = '[%(levelname)s][%(name)s] %(user)s(%(user_id)d): %(message)s'

    def __init__(self, conf):
        self._loggers = ThreadedDict()

    def get(cls, name, session):
        assert isinstance(name, basestring)
        logger = cls._loggers.get(name)
        if logger is None:
            cls._loggers[name] = logger = cls._buildNew(name)
        return logging.LoggerAdapter(logger, {
            'user': session.user.mail,
            'user_id': session.user.id or 0,
        })

    def _buildNew(cls, name):
        logger = logging.Logger(name)
        formatter = logging.Formatter(cls._format)
        handler = logging.StreamHandler()
        handler.setFormatter(formatter)
        logger.addHandler(handler)
        return logger

