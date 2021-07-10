__copyright__ = """ Copyright (c) 2021 HangYan. """
__license__ = 'MIT license'
__version__ = '1.0'
__author__ = 'topaz1668@gmail.com'

import os
import argparse

parser = argparse.ArgumentParser(description='')
parser.add_argument('--push_list', dest='push_list', type=list, default=[])
args = parser.parse_args()

# MESSAGE CONFIG
REGION = "cn-123"
ACCESS_KEY_ID = "$$$$$$$$$$$$$$$$"
ACCESS_KEY_SECRET = "$$$$$$$$$$$$$$$$"


# API CONFIG
SECRET = b'$$$$$$$$$$$$$$$$'
SECRET_KEY = '$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$'
TOKEN_KEY = b'$$$$$$$$'
DES_KEY = b'$$$$$$$$'
VERIFYCODE_TIMEOUT = 60 * 5
TOKEN_TIMEOUT = 3600 * 1000 * 24


# DATABASE CONFIG
USERNAME = "root"
PASSWORD = "123456"
HOST = "127.0.0.1"
PORT = "3306"
DATABASE = "ManageFileDB"

REDIS_HOST = "127.0.0.1"
REDIS_PORT = "3306"
REDIS_PASSWD = "123456"

ERROR_CODE = b'0x00'
SUCCESS_CODE = b'0x01'

RECORD_PAGE_LIMIT = 10
PAGE_LIMIT = 5
REGISTER_USER_PAGE_LIMIT = 20
CHUNK_SIZE = 1014 * 1024 * 10
FILE_STORE_TIME = 60 * 60 * 24

INTRANET_PORT = 8010
EXTERNAL_PORT = 8011
PUBLIC_PORT = 8012

access_logfile = "logfiles/nginx_access.log"
SSH_PORT = 22

INTRANET_HOST = "192.168.0.12"
INTRANET_SSH_USERNAME = "topaz"  # ssh 用户名
INTRANET_SSH_PWD = "123"  # 密码

EXTERNAL_HOST = "192.168.0.11"
EXTERNAL_SSH_USERNAME = "topaz"  # ssh 用户名
EXTERNAL_SSH_PWD = "123"  # 密码

