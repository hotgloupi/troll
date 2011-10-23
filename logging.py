# -*- encoding: utf-8 -*-

from troll.tools import ThreadedDict

class LoggerStore(object):

    _loggers = ThreadedDict()

    _format = '[%(name)s][%(levelno)s]'

    @classmethod
    def get(cls, name):
        assert isinstance(name, basestring)
        logger = cls._loggers.get(name)
        if logger is None:
            cls._loggers[name] = logger = cls._buildNew(name)
        return logger

    @classmethod
    def _buildNew(cls, name):
        logger = logging.Logger(name)
        formatter = logging.Formatter(cls._format)
        handler = logging.StreamHandler()
        handler.setFormatter(formatter)
        logger.addHandler(handler)
        return logger


