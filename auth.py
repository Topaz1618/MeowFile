__copyright__ = """ Copyright (c) 2021 HangYan. """
__license__ = 'MIT license'
__version__ = '1.0'
__author__ = 'topaz1668@gmail.com'

import re
import asyncio
import hmac
import hashlib

from base import BaseHandler
from models import conn_db, Users
from code import AuthError, TokenError, BaseError
from config import SECRET, EXTERNAL_HOST, INTRANET_HOST
from mf_enum import UserType, ModifyType, UserLevel
from mf_utils import auth_login_redirect, create_token, admin_login_redirect, remove_token, get_token_user
from backend_extensions import check_is_admin, get_user_id, check_is_intranet


class IndexHandler(BaseHandler):
    def get(self):
        self.render("index.html", user='18310703270')
        return


class LogoutHandler(BaseHandler):
    def get(self):
        try:
            token = self.get_secure_cookie("token")
            if token is None:
                self.render("login.html")
                return

            if isinstance(token, bytes):
                token = token.decode()

            remove_token(token)
            self.clear_cookie("token")
            self.render("login.html")

        # except TokenError as e:
        #     message = {'msg': e.error_msg, 'error_code': e.error_code}
        #     self.write(message)
        #
        # except Exception as e:
        #     message = {'msg': "Logout failed", 'error_code': '1010'}
        #
        #     self.write(message)

        except BaseError as e:
            print(e)
            self.render("login.html")

        except AuthError as e:
            print(e)
            self.render("login.html")

        except TokenError as e:
            print(e)
            self.render("login.html")

        except Exception as e:
            print(e)
            self.render("login.html")

    def post(self):
        try:
            token = self.get_argument("Authorization", None)

            if token is None or len(token) == 0:
                raise TokenError("5000")

            remove_token(token)
            self.clear_cookie("token")
            message = {'msg': "Logout successful. ", 'error_code': '1000'}

        except TokenError as e:
            message = {'msg': e.error_msg, 'error_code': e.error_code}

        except Exception as e:
            message = {'msg': "Logout failed", 'error_code': '1010'}

        self.write(message)


class LoginHandler(BaseHandler):
    def get(self):
        self.render('login.html')

    def post(self):
        try:
            session = conn_db()

            username = self.get_argument("phonenum", "")
            password = self.get_argument("password", "")

            if username is None or len(username) == 0:
                raise AuthError("1003")

            if password is None or len(password) == 0:
                raise AuthError("1003")

            pwd_verify = re.match(r'[A-Za-z0-9@#$%^&+=]{8,16}$', password)
            if pwd_verify is None:
                raise AuthError("1005")

            user_exists = session.query(Users).filter(Users.username == username).first()
            if user_exists is None:
                raise AuthError("1002")

            password = hmac.new(SECRET, password.encode(), hashlib.md5).hexdigest()

            user_status = session.query(Users).filter(
                Users.username == username,
                Users.password == password
            ).first()

            if user_status is None:
                session.close()
                raise AuthError("1004")

            is_intranet = check_is_intranet(username)
            host_name = self.request.host_name
            if is_intranet and host_name == EXTERNAL_HOST:
                raise BaseError("1007")

            if not is_intranet and host_name == INTRANET_HOST:
                is_admin = check_is_admin(username)
                if is_admin != UserLevel.ADMIN.value:
                    raise BaseError("1008")

            remote_ip = self.get_client_ip()
            token = create_token(username, remote_ip)

            user_status.last_remote_ip = remote_ip
            user_status.is_expired = 0

            if user_status.access_times is None:
                user_status.access_times = 0

            user_status.access_times += 1

            session.add(user_status)
            session.commit()
            print("login token >>>>", token, username)
            message = {
                'msg': {'token': token, 'username': username},
                'error_code': '1000'
            }

            session.close()
            self.clear_cookie("token")
            self.clear_cookie("username")
            self.set_secure_cookie("token", token, 3600)
            self.set_cookie("username", username)

        except AuthError as e:
            message = {'msg':  e.error_msg, 'error_code': e.error_code}

        except BaseError as e:
            message = {'msg':  e.error_msg, 'error_code': e.error_code}

        except Exception as e:
            print("!!!!!!!!!!!! ", e)
            message = {'msg': "Unknown Error", 'error_code': '1010'}

        self.write(message)


class CreateUserHandler(BaseHandler):
    @admin_login_redirect
    def get(self):
        cookie_token = self.get_secure_cookie("token")
        token = self.get_argument("Authorization", None)
        username = get_token_user(cookie_token, token)
        is_admin = check_is_admin(username)

        self.render('create_users.html', username=username, is_admin=is_admin)

    @admin_login_redirect
    def post(self):
        try:
            username = self.get_argument('username', None)
            password1 = self.get_argument('password1', None)
            password2 = self.get_argument('password2', None)
            is_admin = self.get_argument('is_admin', None)
            is_intranet = self.get_argument('is_intranet', None)
            is_allowed_download = self.get_argument('is_allowed_download', None)
            is_allowed_upload = self.get_argument('is_allowed_upload', None)

            print(username, password1, password2, is_admin, is_intranet, is_allowed_download, is_allowed_upload)

            if username is None or len(username) == 0:
                raise AuthError("1016")

            if password1 is None or len(password1) == 0:
                raise AuthError("1004")

            if password1 != password2:
                raise AuthError("1015")

            if is_allowed_download is None:
                is_allowed_download = 0

            if is_allowed_upload is None:
                is_allowed_upload = 0

            if not isinstance(is_allowed_download, int):
                is_allowed_download = int(is_allowed_download)

            if not isinstance(is_allowed_upload, int):
                is_allowed_upload = int(is_allowed_upload)

            if is_intranet is None:
                is_intranet = UserType.INTRANET_USER.value

            if not isinstance(is_intranet, int):
                is_intranet = int(is_intranet)

            if is_admin is None:
                is_admin = 0

            if not isinstance(is_admin, int):
                is_admin = int(is_admin)

            if is_admin in UserLevel.REVIEW_GROUP.value:
                is_intranet = UserType.EXTRANET_USER.value
                is_allowed_download = 1
                is_allowed_upload = 1

            session = conn_db()
            user_exists = session.query(Users).filter(Users.username == username).first()
            if user_exists is not None:
                raise AuthError("1001")

            pwd_verify = re.match(r'[A-Za-z0-9@#$%^&+=]{8,16}$', password1)

            if pwd_verify is None:
                raise AuthError("1005")

            password = hmac.new(SECRET, password1.encode(), hashlib.md5).hexdigest()
            user = Users(
                username=username,
                password=password,
                is_admin=is_admin,
                is_allowed_upload=bool(is_allowed_upload),
                is_allowed_download=bool(is_allowed_download),
                is_intranet_user=bool(is_intranet),
                access_times=0)
            session.add(user)
            session.commit()

            message = {
                'msg': {
                    "username": username,
                    "is_admin": is_admin,
                },
                'error_code': '1000'
            }

        except AuthError as e:
            message = {'msg':  e.error_msg, 'error_code': e.error_code}

        except Exception as e:

            message = {'msg': "Unknow Error", 'error_code': '1010'}

        self.write(message)


class RestPasswordView(BaseHandler):
    @auth_login_redirect
    def get(self):
        cookie_token = self.get_secure_cookie("token")
        token = self.get_argument("Authorization", None)
        username = get_token_user(cookie_token, token)
        is_admin = check_is_admin(username)

        self.render('reset_password.html', username=username, is_admin=is_admin)

    @auth_login_redirect
    def post(self):
        try:
            cookie_token = self.get_secure_cookie("token")
            token = self.get_argument("Authorization", None)
            user = get_token_user(cookie_token, token)

            username = self.get_argument('username', '')
            password = self.get_argument('password1', '')
            password2 = self.get_argument('password2', '')

            manager_level = check_is_admin(user)
            user_level = check_is_admin(username)

            session = conn_db()
            print(username, password, password2)

            if username is None or len(username) == 0:
                raise AuthError("1003")

            if password is None or len(password) == 0:
                raise AuthError("1003")

            if password != password2:
                raise AuthError("1003")

            pwd_verify = re.match(r'[A-Za-z0-9@#$%^&+=]{8,16}$', password)
            if pwd_verify is None:
                raise AuthError("1005")

            user_obj = session.query(Users).filter(Users.username == username).first()
            if user_obj is None:
                raise AuthError("1002")

            manager_uid = get_user_id(user)
            print(">>>>>>>>>", manager_uid, user_obj.id)
            if user_obj.id != manager_uid:
                if manager_level != UserLevel.ADMIN.value:
                    raise AuthError("1016")

                if user_level == UserLevel.ADMIN.value:
                    raise AuthError("1017")

            password = hmac.new(SECRET, password.encode(), hashlib.md5).hexdigest()
            user_obj.password = password
            session.commit()
            session.close()
            message = {
                'msg': {
                    "user": username,
                },
                'error_code': '1000',

            }
        except BaseError as e:
            message = {'msg':  e.error_msg, 'error_code': e.error_code}

        except AuthError as e:
            message = {'msg':  e.error_msg, 'error_code': e.error_code}

        except Exception as e:
            print("!!!!!", e)
            message = {'msg': "Unknown Error", 'error_code': '1010'}

        self.write(message)


class UpdatePermissionHandler(BaseHandler):
    @admin_login_redirect
    def get(self):
        try:
            cookie_token = self.get_secure_cookie("token")
            token = self.get_argument("Authorization", None)
            username = get_token_user(cookie_token, token)

            is_admin = check_is_admin(username)

            self.render("modify_permission.html", username=username, is_admin=is_admin)

        except TokenError as e:
            self.render("authority_error.html", error_message=e.error_msg, error_code=e.error_code)

        except Exception as e:
            print(e)
            self.render("error_page.html", error_message="Unknown error")

    @admin_login_redirect
    def post(self):
        try:
            cookie_token = self.get_secure_cookie("token")
            token = self.get_argument("Authorization", None)
            admin_user = get_token_user(cookie_token, token)

            username = self.get_argument("username", None)
            modify_type = self.get_argument("modify_type", None)
            is_admin = self.get_argument("is_admin", None)
            is_intranet = self.get_argument('is_intranet', None)
            is_allowed_download = self.get_argument('is_allowed_download', None)
            is_allowed_upload = self.get_argument('is_allowed_upload', None)

            user_level = check_is_admin(username)
            if user_level == UserLevel.ADMIN.value:
                raise AuthError("1017")

            session = conn_db()

            user_obj = session.query(Users).filter(
                Users.username == username,
            ).first()

            if user_obj is None:
                session.close()
                raise AuthError("1002")

            print("!!!", modify_type, is_admin, is_intranet)

            if modify_type is None:
                raise BaseError("1002")

            if not isinstance(modify_type, int):
                modify_type = int(modify_type)

            if modify_type == ModifyType.IS_ADMIN.value:
                print("!!!", modify_type, )

                if is_admin is None:
                    raise BaseError("1002")

                if not isinstance(is_admin, int):
                    is_admin = int(is_admin)

                current_permission = user_obj.is_admin
                if current_permission == is_admin:
                    session.close()
                    raise AuthError("1014")

                user_obj.is_admin = is_admin

            elif modify_type == ModifyType.IS_INTRANET.value:
                if is_intranet is None:
                    raise BaseError("1002")

                if not isinstance(is_intranet, int):
                    is_intranet = int(is_intranet)

                current_type = user_obj.is_intranet_user
                if current_type == is_intranet:
                    session.close()
                    raise AuthError("1014")

                user_obj.is_intranet_user = bool(is_intranet)

            elif modify_type == ModifyType.IS_ALLOWED_UPLOAD.value:
                if is_allowed_upload is None:
                    raise BaseError("1002")

                if not isinstance(is_allowed_upload, int):
                    is_allowed_upload = int(is_allowed_upload)

                current_type = user_obj.is_allowed_upload
                if current_type == is_allowed_upload:
                    session.close()
                    raise AuthError("1014")

                user_obj.is_allowed_upload = bool(is_allowed_upload)

            elif modify_type == ModifyType.IS_ALLOWED_DOWNLOAD.value:
                if is_allowed_download is None:
                    raise BaseError("1002")

                if not isinstance(is_allowed_download, int):
                    is_allowed_download = int(is_allowed_download)

                current_type = user_obj.is_allowed_download
                if current_type == is_allowed_download:
                    session.close()
                    raise AuthError("1014")

                user_obj.is_allowed_download = bool(is_allowed_download)

            session.commit()
            session.close()

            data = {
                "username": username,
                "permission": is_admin,
                "is_intranet": is_intranet,
            }

            message = {'msg': data, 'error_code': "1000"}
            print(message)

        except BaseError as e:
            print("1005", e)
            message = {'msg': e.error_msg, 'error_code': e.error_code}

        except AuthError as e:
            message = {'msg': e.error_msg, 'error_code': e.error_code}

        except Exception as e:
            print("Error:", e)
            message = {'msg': "Unknown Error", 'error_code': '1010'}

        self.write(message)
