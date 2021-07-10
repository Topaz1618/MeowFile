__copyright__ = """ Copyright (c) 2021 HangYan. """
__license__ = 'MIT license'
__version__ = '1.0'
__author__ = 'topaz1668@gmail.com'

import sys
import re
import logging.handlers
import time
import os


class MyTimedRotatingFileHandler(logging.handlers.TimedRotatingFileHandler):
    """ 自定制日志方法: 每天更新, 到达一定数量自动清除 """
    def __init__(self):
        formatter = logging.Formatter(fmt='[%(levelname)s] [%(asctime)s] %(message)s', datefmt='%Y_%m_%d %H:%M:%S')
        self.setFormatter(formatter)
        self.dir_log = "logfiles/"
        filename = self.dir_log + time.strftime("%Y_%m_%d") + ".log"
        logging.handlers.TimedRotatingFileHandler.__init__(self, filename, when='D', interval=1, backupCount=180)

    def doRollover(self):
        self.stream.close()
        self.baseFilename = self.dir_log + time.strftime("%Y_%m_%d") + ".log"
        self.stream = open(self.baseFilename, 'w')
        self.rolloverAt = self.rolloverAt + self.interval
        if self.backupCount > 0:
            for s in self.getFilesToDelete():
                os.remove(s)

    def getFilesToDelete(self):
        dirName, baseName = os.path.split(self.baseFilename)
        fileNames = os.listdir(dirName)
        result = []
        prefix, suffix = baseName.split(".")
        for fileName in fileNames:
            if self.extMatch.match(prefix):
                result.append(os.path.join(dirName, fileName))
        if self.backupCount == 0:
            result = []

        if len(result) < self.backupCount:
            result = []
        else:
            result.sort()
            result = result[:len(result) - self.backupCount]
        return result


log_path = "logfiles"
formatter = logging.Formatter(fmt='[%(levelname)s] [%(asctime)s] %(message)s', datefmt='%Y_%m_%d %H:%M:%S')

# Common log
logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)
common_handler = logging.handlers.TimedRotatingFileHandler(f"{log_path}/{time.strftime('%Y_%m_%d')}.log",  when='D', interval=1, backupCount=30)
common_handler.setFormatter(formatter)
logger.addHandler(common_handler)

# Download log
download_logger = logging.getLogger("download")
download_handler = logging.handlers.RotatingFileHandler(f"{log_path}/download.log", maxBytes=10000, backupCount=3)
download_handler.setFormatter(formatter)
download_logger.addHandler(download_handler)

# User asset change log
asset_logger = logging.getLogger("asset")
asset_handler = logging.handlers.RotatingFileHandler(f"{log_path}/user_asset.log", maxBytes=10000, backupCount=3)
asset_handler.setFormatter(formatter)
asset_logger.addHandler(asset_handler)


# Admin asset change log
admin_logger = logging.getLogger("admin")
admin_handler = logging.handlers.RotatingFileHandler(f"{log_path}/amdin_asset.log", maxBytes=10000, backupCount=3)
admin_handler.setFormatter(formatter)
admin_logger.addHandler(admin_handler)


# logger.warning("logger")
# download_logger.warning("download_logger")
# asset_logger.warning("asset ")
# access_logger.warning("access")
#
