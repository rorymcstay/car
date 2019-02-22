import logging as logging
import os
import traceback
from logging.handlers import RotatingFileHandler


class LogGenerator:
    def __init__(self, log, name):
        '''Makes a log handler with format for telegraf/grafana. outputs it to root/out'''
        LOGLEVEL = os.getenv('LOGLEVEL', 'INFO').upper()
        LOG = log.getLogger(name)
        LOG.setLevel(level=LOGLEVEL)
        # create file handler which logs even debug messages

        if not os.path.exists('./out/'):
            os.makedirs('./out/')
        # fh = logging.FileHandler('./out/{}.log'.format(name))
        fh = RotatingFileHandler('./out/{}.log'.format(name), maxBytes=os.getenv("MAX_LOG_BYTES", 500000),
                                 backupCount=os.getenv("LOG_BACKUP", 5))
        LOG.addHandler(fh)
        # fh.setLevel(logging.INFO)
        # create console handler with a higher log level
        ch = logging.StreamHandler()
        ch.setLevel(level=LOGLEVEL)
        # create formatter and add it to the handlers
        formatter = logging.Formatter(' %(name)s - %(asctime)s - %(levelname)s: %(message)s')
        fh.setFormatter(formatter)
        ch.setFormatter(formatter)
        # add the handlers to the logger
        LOG.addHandler(fh)
        LOG.addHandler(ch)
        self.debug = LOG.debug
        self.info = LOG.info
        self.warning = LOG.warning
        self.error = LOG.error

def write_log(log, msg, thread='main', **kwargs):
    try:
        string = '-thread: {} -msg: {}'.format(thread, msg)
        if kwargs is not None:
            for key, value in kwargs.items():
                string = string + ' -{}: {}'.format(key, value)
        log(string)
    except:
        print('logging error')
        traceback.print_exc()
