__copyright__ = """ Copyright (c) 2021 HangYan. """
__license__ = 'MIT license'
__version__ = '1.0'
__author__ = 'topaz1668@gmail.com'

from enum import Enum


class CreateType(Enum):
    CREATE_SECONDARY_MENU = 0
    ZIP = 1
    FEATURE = 2
    GOODS = 3
    VIDEO = 4


class DeleteType(Enum):
    SECONDARY_MENU = 0
    ZIP = 1
    FEATURE = 2
    GOODS = 3
    VIEW_VIDEO = 4


class GetType(Enum):
    DEFAULT = 0
    MAIN_MENU = 1
    RESOURCES = 2


class GoodsType(Enum):
    ZIP = 0
    FEATURE = 1


class ZipType(Enum):
    ACTOR = 1
    SCENE = 2
    ACTION = 3
    SHOT = 4


class CreateAuthority(Enum):
    SCENE = False
    SHOT = False
    ACTOR = True
    ACTION = True


class PayChannel(Enum):
    WXPAY = 0
    ALIPAY = 1
    Free = 2


class RechargeStatus(Enum):
    SUCCESS = 0
    FAIL = 1


class OrderStatus(Enum):
    SUCCESS = 0
    NOTPAY = 1
    PAYERROR = 2
    REVOKED = 3
    CLOSED = 4
    USERPAYING = 5


class OwnerEnum(Enum):
    PAID = 0
    AllUSER = 1
    MEMBER = 2


class MemberLevel(Enum):
    NON_MEMBER = 0  # 非会员
    JUNIOR_MEMBER = 1
    SENIOR_MEMBER = 2


class AuthorityLevel(Enum):
    CUSTOM = 0  # 非会员
    VIP = 2


class PayStatus(Enum):
    SUCCESS = "Success"  # 非会员
    Fail = "Fail"


class RequestDataType(Enum):
    PENDING_FILES = 0
    APPROVED_FILES = 1
    FAILED_FILES = 2
    ALL_FILES = 3


class ApprovalStatus(Enum):
    PENDING_FILES = 0
    APPROVED_FILES = 1
    FAILED_FILES = 2
    ALL_FILES = 3


class UserType(Enum):
    EXTRANET_USER = 0
    INTRANET_USER = 1
    ALL_USER = 2


class ModifyType(Enum):
    IS_ADMIN = 1
    IS_INTRANET = 2
    IS_ALLOWED_UPLOAD = 3
    IS_ALLOWED_DOWNLOAD = 4


class UserLevel(Enum):
    NORMAL = 0  # 普通用户
    ADMIN = 1   # Admin
    REVIEWER = 2    # 审核人员
    REVIEW_GROUP = [1, 2]  # 审核组 1: Admin 2: 审核人员


