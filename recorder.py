# -*- coding:utf-8 -*-
import os
import logging
from logging.handlers import TimedRotatingFileHandler
from logging.handlers import RotatingFileHandler


class get_log():
    def __init__(self):
        self.loglevel = logging.INFO
        self.logleve2 = logging.WARNING
        self.logleve3 = logging.ERROR
        self.logleve4 = logging.CRITICAL
        self.logleve5 = logging.DEBUG
        self.logleve6 = logging.NOTSET

    def config_log(self, filename=None):
        logger = logging.getLogger(__name__)
        if not bool(filename):
            return self.config_stream_log(logger)
        else:
            return self.config_file_log(logger, filename)

    def config_file_log(self, logger, filename):
        formatter = logging.Formatter(
            ('%(asctime)s  %(pathname)s %(levelname)s 第%(lineno)d行'
             ' %(message)s'))
        logger.setLevel(self.loglevel)
        ch = logging.StreamHandler()
        ch.setLevel(self.logleve3)
        ch.setFormatter(formatter)
        logger.addHandler(ch)
        '''定义文件流'''
        # fh = TimedRotatingFileHandler(filename=filename, when='s', interval=1)
        fh = RotatingFileHandler(filename=filename, maxBytes=512*1024*1024,backupCount=20)
        fh.setLevel(self.loglevel)
        fh.setFormatter(formatter)
        # fh.suffix = '.log'
        # fh.suffix = '%Y%m%d-%H%M.log'
        # fh.suffix = '%Y-%m-%d %H-%M-%S.log'
        logger.addHandler(fh)
        return logger

    def config_stream_log(self, logger):
        handler = logging.StreamHandler()
        formatter = logging.Formatter('%(pathname)s--第%(lineno)d行--%(levelname)s--%(message)s')
        handler.setFormatter(formatter)
        logger.addHandler(handler)
        logger.setLevel(self.loglevel)
        return logger

    def get_filesize(path: 'str'):
        '''获取文件的大小字节'''
        file_size = os.stat(path)
        return file_size.st_size