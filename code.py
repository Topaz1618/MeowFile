__copyright__ = """ Copyright (c) 2021 HangYan. """
__license__ = 'MIT license'
__version__ = '1.0'
__author__ = 'topaz1668@gmail.com'

class BaseError(Exception):
    def __init__(self, error_code):
        super().__init__(self)
        self.error_dic = {
            '1001': 'Get params failed. ',
            '1002': 'Type of input error. ',
            '1003': 'File does not exists. ',
            '1004': 'File receiving. ',
            '1005': 'Permission error. ',
            '1006': '请选择文件',
            '1007': '当前用户类型为内网账号, 请登录内网服务器',
            '1008': '当前用户类型为外网账号, 请登录外网服务器',
            '1009': 'File already exists',
            '1010': '当前用户无上传权限',
            '1011': '当前用户无下载权限',

        }
        self.error_code = error_code
        if self.error_code in self.error_dic:
            self.error_msg = self.error_dic.get(self.error_code)
        else:
            self.error_msg = self.error_code

    def __str__(self):
        return self.error_msg


class AuthError(Exception):
    def __init__(self, error_code):
        super().__init__(self)
        self.error_dic = {
            '1001': 'user exists',
            '1002': "User does not exists",
            '1003': 'register failed',
            '1004': 'password failed',
            '1005': 'Password format failed',
            '1006': 'verify code does not exists or already expired or already used.',
            '1007': 'The verify code sent failed. ',
            '1008': 'Get phone number failed',
            '1009': 'phone number format failed. ',
            '1010': '已领取会员',
            "1011": '会员已过期 ',
            "1012": "Membership has expired",
            "1013": "创建内部测试用户失败",
            "1014": "已指定相同权限, 请勿重复设置",
            '1015': 'Password match failed',
            '1016': '请检查用户名',
            '1017': 'Admin 用户， 权限禁止修改',
        }
        self.error_code = error_code
        if self.error_code in self.error_dic:
            self.error_msg = self.error_dic.get(self.error_code)
        else:
            self.error_msg = self.error_code

    def __str__(self):
        return self.error_msg


class DBError(Exception):
    def __init__(self, error_code, error_message=None):
        super().__init__(self)
        self.error_dic = {
            '4001': 'Failed to count the number of times. ',
            '4002': 'Add new item failed. ',
            '4003': 'Item has already exists. ',
            '4004': 'Item does not exists. ',
            '4005': 'Get object failed',
            '4006': '当前文件不存在',
            "4007": 'Permission error, no permission to delete file. ',
            "4008": 'Delete file error',

        }
        self.error_code = error_code
        if self.error_code in self.error_dic:
            self.error_msg = self.error_dic.get(self.error_code)
        else:
            self.error_msg = error_message

    def __str__(self):
        return self.error_msg


class TokenError(Exception):
    def __init__(self, error_code, error_message=None):
        super().__init__(self)
        self.error_dic = {
            '5000': 'Get token failed. ',
            '5001': 'Token has already expired. ',
            '5002': 'Illegal Ip. ',
            '5003': 'Token does not exist. ',
            '5005': 'token does not match the user. ',
            "5006": 'Current user is not member. ',
            "5007": 'Member has expired. ',
            "5008": 'Current user is not admin.',
            "5009": 'Token format error.',
            "5010": '当前用户权限不足.',
        }
        self.error_code = error_code
        if self.error_code in self.error_dic:
            self.error_msg = self.error_dic.get(self.error_code)
        else:
            self.error_msg = error_message

    def __str__(self):
        return self.error_msg


class BackstageError(Exception):
    def __init__(self, error_code, error_message=None):
        super().__init__(self)
        self.error_dic = {
            '6000': 'Permission denied. ',
            '6001': 'Token has already expired. ',
            '6002': 'Illegal Ip. ',
            '6003': 'Token does not exist. ',
            '6004': 'token does not match the user',
        }
        self.error_code = error_code
        if self.error_code in self.error_dic:
            self.error_msg = self.error_dic.get(self.error_code)
        else:
            self.error_msg = error_message

    def __str__(self):
        return self.error_msg

