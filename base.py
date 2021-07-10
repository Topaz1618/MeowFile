__copyright__ = """ Copyright (c) 2021 HangYan. """
__license__ = 'MIT license'
__version__ = '1.0'
__author__ = 'topaz1668@gmail.com'

import os
import stat
import asyncio
import jwt
import math
import psutil
import aiofiles
from time import time, sleep
from urllib.parse import quote

from tornado.web import RequestHandler

from backend_extensions import get_file_name, create_upload_record, get_total_counts, generate_data_list, create_download_record, \
    update_review_status, check_is_admin, delete_file, get_total_records, get_record_list, check_is_intranet, get_user_info, \
    delete_resources, get_total_users, get_user_list, check_expired_file
from config import SECRET_KEY, PAGE_LIMIT, RECORD_PAGE_LIMIT, INTRANET_HOST, EXTERNAL_HOST
from code import BaseError, DBError, TokenError, AuthError
from mf_utils import async_auth_login_redirect, auth_login_redirect, get_token_user, subtract_num, add_num, admin_login_redirect, \
    async_admin_login_redirect, reviewer_login_redirect, async_reviewer_login_redirect
from mf_logger import logger as mf_logging
from mf_logger import download_logger, asset_logger
from mf_enum import RequestDataType, UserType, UserLevel
from mf_scp import get_from_remote, put_to_remote, put_to_remote_win


class BaseHandler(RequestHandler):
    def get_current_user(self):
        return self.get_secure_cookie("username")

    def get_client_ip(self):
        x_real_ip = self.request.headers.get("X-Real-IP")
        remote_ip = x_real_ip or self.request.remote_ip
        return remote_ip


class PageErrorHandler(BaseHandler):
    """ 错误页面 """
    def get(self):
        self.set_header("Response-Code", "404")
        self.render("404.html")


class IndexHandler(BaseHandler):
    """ 主页面 """
    def get(self):
        try:
            token = self.get_secure_cookie("token")
            if token is not None:
                if isinstance(token, bytes):
                    token = token.decode()

                token_dic = jwt.decode(token.encode(), SECRET_KEY)
                username = token_dic.get('phonenum')
                user_level = check_is_admin(username)
            else:
                username = None
                user_level = UserLevel.NORMAL.value

            self.render("main.html", username=username, is_admin=user_level)

        except BaseError as e:
            self.render("authority_error.html", error_message=e.error_msg, error_code=e.error_code)

        except TokenError as e:
            self.render("authority_error.html", error_message=e.error_msg, error_code=e.error_code)

        except Exception as e:
            print(e)
            self.render("error_page.html", error_message="Unknown error")


class UserInfoHandler(BaseHandler):
    @auth_login_redirect
    def get(self):
        try:
            cookie_token = self.get_secure_cookie("token")
            token = self.get_argument("Authorization", None)
            username = get_token_user(cookie_token, token)
            is_admin = check_is_admin(username)
            data = get_user_info(username)
            self.render("user_info.html", username=username, is_admin=is_admin, data=data)

        except BaseError as e:
            self.render("error_page.html", error_message=e.error_msg)

        except TokenError as e:
            print("DBError", e, e.error_code)
            self.render("authority_error.html", error_message=e.error_msg)

        except AuthError as e:
            self.render("error_page.html", error_message=e.error_msg)

        except Exception as e:

            self.render("error_page.html", error_message="Unknown error")


class CountFileHandler(BaseHandler):
    @reviewer_login_redirect
    def get(self):
        try:
            cookie_token = self.get_secure_cookie("token")
            token = self.get_argument("Authorization", None)
            username = get_token_user(cookie_token, token)

            type_id = RequestDataType.PENDING_FILES.value
            is_admin = check_is_admin(username)
            total = get_total_counts(type_id, username, is_admin)

            message = {"msg": total, "error_code": "1000"}
            self.write(message)

        except BaseError as e:
            self.render("error_page.html", error_message=e.error_msg)

        except TokenError as e:
            self.render("authority_error.html", error_message=e.error_msg)

        except DBError as e:
            self.render("error_page.html", error_message=e.error_msg)

        except AuthError as e:
            self.render("error_page.html", error_message=e.error_msg)

        except Exception as e:
            self.render("error_page.html", error_message="Unknown error")


class ReviewFileHandler(BaseHandler):
    def get_file(self, file_id, status_id, username, loop):
        asyncio.set_event_loop(loop)
        update_review_status(file_id, status_id, username)

    @async_reviewer_login_redirect
    async def get(self):
        try:
            cookie_token = self.get_secure_cookie("token")
            token = self.get_argument("Authorization", None)
            username = get_token_user(cookie_token, token)

            file_id = self.get_argument("fid", None)
            status_id = self.get_argument("status", None)

            if file_id is None:
                raise BaseError("1002")

            if status_id is None:
                raise BaseError("1002")

            if not isinstance(file_id, int):
                file_id = int(file_id)

            if not isinstance(status_id, int):
                status_id = int(status_id)

            loop = asyncio.get_event_loop()
            loop.run_in_executor(None, self.get_file, file_id, status_id, username, loop)

            self.redirect("/pending_list")

        except BaseError as e:
            self.render("error_page.html", error_message=e.error_msg)

        except DBError as e:
            self.render("error_page.html", error_message=e.error_msg)

        except Exception as e:
            self.render("error_page.html", error_message="Unknown error")

    def post(self):
        try:
            cookie_token = self.get_secure_cookie("token")
            token = self.get_argument("Authorization", None)
            username = get_token_user(cookie_token, token)

            file_id = self.get_argument("fid", None)
            status_id = self.get_argument("status", None)

            if file_id is None:
                raise BaseError("1002")

            if status_id is None:
                raise BaseError("1002")

            if not isinstance(file_id, int):
                file_id = int(file_id)

            if not isinstance(status_id, int):
                status_id = int(status_id)

            update_review_status(file_id, status_id, username)
            message = {"msg": "successful", "error_code": "1000"}

        except BaseError as e:
            print("1005", e)
            message = {'msg': e.error_msg, 'error_code': e.error_code}

        except DBError as e:
            print("DBError", e, e.error_code)
            message = {'msg': e.error_msg, 'error_code': e.error_code}

        except AuthError as e:
            message = {'msg': e.error_msg, 'error_code': e.error_code}

        except Exception as e:
            print("Error:", e)
            message = {'msg': "Unknown Error", 'error_code': '1010'}

        self.write(message)


class DeleteFileHandler(BaseHandler):
    @auth_login_redirect
    def post(self):
        try:
            cookie_token = self.get_secure_cookie("token")
            token = self.get_argument("Authorization", None)
            username = get_token_user(cookie_token, token)
            is_admin = check_is_admin(username)
            file_id = self.get_argument("file_id", None)
            if file_id is None:
                raise BaseError("1002")

            delete_file(username, file_id, is_admin)

            message = {"msg": "successful", "error_code": "1000"}

        except BaseError as e:
            print("1005", e)
            message = {'msg': e.error_msg, 'error_code': e.error_code}

        except DBError as e:
            print("DBError", e, e.error_code)
            message = {'msg': e.error_msg, 'error_code': e.error_code}

        except AuthError as e:
            message = {'msg': e.error_msg, 'error_code': e.error_code}

        except Exception as e:
            print("Error:", e)
            message = {'msg': "Unknown Error", 'error_code': '1010'}

        self.write(message)


class ManageFilesHandler(BaseHandler):
    @reviewer_login_redirect
    def post(self):
        try:
            cookie_token = self.get_secure_cookie("token")
            token = self.get_argument("Authorization", None)
            username = get_token_user(cookie_token, token)

            file_list = self.get_argument("resource_list", None)
            if file_list is None:
                raise BaseError("1006")

            delete_resources(username, file_list)
            message = {"msg": "successful", "error_code": "1000"}

        except BaseError as e:
            print("1005", e)
            message = {'msg': e.error_msg, 'error_code': e.error_code}

        except DBError as e:
            print("DBError", e, e.error_code)
            message = {'msg': e.error_msg, 'error_code': e.error_code}

        except AuthError as e:
            message = {'msg': e.error_msg, 'error_code': e.error_code}

        except Exception as e:
            print("Error:", e)
            message = {'msg': "Unknown Error", 'error_code': '1010'}

        self.write(message)

    @reviewer_login_redirect
    def get(self):
        try:
            cookie_token = self.get_secure_cookie("token")
            token = self.get_argument("Authorization", None)
            username = get_token_user(cookie_token, token)
            is_admin = check_is_admin(username)

            type_id = self.get_argument("select", None)
            page_num = self.get_argument("page", None)

            page_num = page_num if page_num is not None else 1

            if type_id is None:
                if is_admin in UserLevel.REVIEW_GROUP.value:
                    type_id = RequestDataType.ALL_FILES.value if is_admin else RequestDataType.APPROVED_FILES.value

            if not isinstance(type_id, int):
                type_id = int(type_id)

            if not isinstance(page_num, int):
                page_num = int(page_num)

            total = get_total_counts(type_id, username, is_admin)
            total_page = math.ceil(total / PAGE_LIMIT)
            start = (page_num - 1) * PAGE_LIMIT
            end = total if PAGE_LIMIT * page_num > total else PAGE_LIMIT * page_num

            data = generate_data_list(username, start, end, type_id, is_admin)

            page_info = {
                "start": start,
                "end": end,
                "total_data": total,
                "current_page": page_num,
                "total_page": total_page,
                "is_select": type_id,
                "is_admin": is_admin,
            }

            self.render("manage_files.html", username=username, is_admin=is_admin, page_info=page_info, data=data, subtract=subtract_num, add=add_num)

        except BaseError as e:
            self.render("error_page.html", error_message=e.error_msg)

        except AuthError as e:
            self.render("error_page.html", error_message=e.error_msg)

        except DBError as e:
            self.render("error_page.html", error_message=e.error_msg)

        except Exception as e:
            self.render("error_page.html", error_message="Unknown error")


class UserListHandler(BaseHandler):
    @admin_login_redirect
    def get(self):
        # try:
            cookie_token = self.get_secure_cookie("token")
            token = self.get_argument("Authorization", None)
            username = get_token_user(cookie_token, token)
            is_admin = check_is_admin(username)

            user_type = self.get_argument("select", None)
            page_num = self.get_argument("page", None)

            if user_type is None:
                user_type = UserType.ALL_USER.value

            if not isinstance(user_type, int):
                user_type = int(user_type)

            page_num = page_num if page_num is not None else 1

            if not isinstance(page_num, int):
                page_num = int(page_num)

            total = get_total_users(user_type)
            total_page = math.ceil(total / PAGE_LIMIT)
            start = (page_num - 1) * PAGE_LIMIT
            end = total if PAGE_LIMIT * page_num > total else PAGE_LIMIT * page_num

            page_info = {
                "start": start,
                "end": end,
                "total_data": total,
                "current_page": page_num,
                "total_page": total_page,
                "is_select": user_type,
                "is_admin": is_admin,
            }

            data = get_user_list(start, end, user_type)
            self.render("user_list.html", username=username, is_admin=is_admin, page_info=page_info, data=data, subtract=subtract_num, add=add_num)

        # except BaseError as e:
        #     self.render("error_page.html", error_message=e.error_msg)
        #
        # except AuthError as e:
        #     self.render("error_page.html", error_message=e.error_msg)
        #
        # except DBError as e:
        #     self.render("error_page.html", error_message=e.error_msg)
        #
        # except Exception as e:
        #     print(e)
        #     self.render("error_page.html", error_message="Unknown error")


class FileListHandler(BaseHandler):
    @auth_login_redirect
    def get(self):
        try:
            cookie_token = self.get_secure_cookie("token")
            token = self.get_argument("Authorization", None)
            username = get_token_user(cookie_token, token)
            is_admin = check_is_admin(username)

            type_id = self.get_argument("select", None)
            page_num = self.get_argument("page", None)
            page_num = page_num if page_num is not None else 1

            if type_id is None:
                if is_admin in UserLevel.REVIEW_GROUP.value:
                    type_id = RequestDataType.ALL_FILES.value
                else:
                    type_id = RequestDataType.APPROVED_FILES.value

            if not isinstance(type_id, int):
                type_id = int(type_id)

            if not isinstance(page_num, int):
                page_num = int(page_num)

            check_expired_file()

            total = get_total_counts(type_id, username, is_admin)
            total_page = math.ceil(total / PAGE_LIMIT)
            start = (page_num - 1) * PAGE_LIMIT
            end = total if PAGE_LIMIT * page_num > total else PAGE_LIMIT * page_num

            data = generate_data_list(username, start, end, type_id, is_admin)

            page_info = {
                "start": start,
                "end": end,
                "total_data": total,
                "current_page": page_num,
                "total_page": total_page,
                "is_select": type_id,
                "is_admin": is_admin,
            }
            is_admin = check_is_admin(username)

            self.render("file_list.html", username=username, is_admin=is_admin, page_info=page_info, data=data, subtract=subtract_num, add=add_num)

        except BaseError as e:
            self.render("error_page.html", error_message=e.error_msg)

        except AuthError as e:
            self.render("error_page.html", error_message=e.error_msg)

        except DBError as e:
            self.render("error_page.html", error_message=e.error_msg)

        except Exception as e:
            self.render("error_page.html", error_message="Unknown error")


class PendingListHandler(BaseHandler):
    @reviewer_login_redirect
    def get(self):
        try:
            cookie_token = self.get_secure_cookie("token")
            token = self.get_argument("Authorization", None)
            username = get_token_user(cookie_token, token)
            is_admin = check_is_admin(username)
            page_num = self.get_argument("page", None)
            page_num = page_num if page_num is not None else 1
            if not isinstance(page_num, int):
                page_num = int(page_num)

            type_id = RequestDataType.PENDING_FILES.value
            total = get_total_counts(type_id, username, is_admin)
            total_page = math.ceil(total / PAGE_LIMIT)
            start = (page_num - 1) * PAGE_LIMIT
            end = total if PAGE_LIMIT * page_num > total else PAGE_LIMIT * page_num

            is_admin = check_is_admin(username)

            data = generate_data_list(username, start, end, type_id, is_admin)

            page_info = {
                "start": start,
                "end": end,
                "total_data": total,
                "current_page": page_num,
                "total_page": total_page,
                "is_select": type_id,
            }
            self.render("pending_list.html", username=username, is_admin=is_admin, page_info=page_info, data=data, subtract=subtract_num, add=add_num)

        except BaseError as e:
            self.render("error_page.html", error_message=e.error_msg)

        except AuthError as e:
            self.render("error_page.html", error_message=e.error_msg)

        except DBError as e:
            self.render("error_page.html", error_message=e.error_msg)

        except Exception as e:
            self.render("error_page.html", error_message="Unknown error")


class ShowRecordHandler(BaseHandler):
    @reviewer_login_redirect
    def get(self):
        try:
            cookie_token = self.get_secure_cookie("token")
            token = self.get_argument("Authorization", None)
            username = get_token_user(cookie_token, token)
            page_num = self.get_argument("page", None)
            page_num = page_num if page_num is not None else 1
            if not isinstance(page_num, int):
                page_num = int(page_num)

            is_admin = check_is_admin(username)
            total = get_total_records(username, is_admin, is_personal_only=False)
            total_page = math.ceil(total / RECORD_PAGE_LIMIT)
            start = (page_num - 1) * RECORD_PAGE_LIMIT
            end = total if RECORD_PAGE_LIMIT * page_num > total else RECORD_PAGE_LIMIT * page_num

            print(total, total_page, start, end)

            data = get_record_list(username, start, end, is_admin, is_personal_only=False)

            page_info = {
                "start": start,
                "end": end,
                "total_data": total,
                "current_page": page_num,
                "total_page": total_page,
            }

            self.render("download_record.html", username=username, is_admin=is_admin, page_info=page_info, data=data, subtract=subtract_num, add=add_num)

        except BaseError as e:
            self.render("error_page.html", error_message=e.error_msg)

        except AuthError as e:
            self.render("error_page.html", error_message=e.error_msg)

        except DBError as e:
            self.render("error_page.html", error_message=e.error_msg)

        except Exception as e:
            self.render("error_page.html", error_message="Unknown error")


class ShowMyRecordHandler(BaseHandler):
    @auth_login_redirect
    def get(self):
        try:
            cookie_token = self.get_secure_cookie("token")
            token = self.get_argument("Authorization", None)
            username = get_token_user(cookie_token, token)

            page_num = self.get_argument("page", None)
            page_num = page_num if page_num is not None else 1
            if not isinstance(page_num, int):
                page_num = int(page_num)

            is_admin = check_is_admin(username)
            total = get_total_records(username, is_admin, is_personal_only=True)
            total_page = math.ceil(total / RECORD_PAGE_LIMIT)
            start = (page_num - 1) * RECORD_PAGE_LIMIT
            end = total if RECORD_PAGE_LIMIT * page_num > total else RECORD_PAGE_LIMIT * page_num

            print(total, total_page, start, end)

            data = get_record_list(username, start, end, is_admin, is_personal_only=True)

            page_info = {
                "start": start,
                "end": end,
                "total_data": total,
                "current_page": page_num,
                "total_page": total_page,
            }

            self.render("download_record.html", username=username, is_admin=is_admin, page_info=page_info, data=data, subtract=subtract_num, add=add_num)

        except BaseError as e:
            self.render("error_page.html", error_message=e.error_msg)

        except AuthError as e:
            self.render("error_page.html", error_message=e.error_msg)

        except DBError as e:
            self.render("error_page.html", error_message=e.error_msg)

        except Exception as e:
            self.render("error_page.html", error_message="Unknown error")


class MyFilesHandler(BaseHandler):
    @auth_login_redirect
    def get(self):
        try:
            cookie_token = self.get_secure_cookie("token")
            token = self.get_argument("Authorization", None)
            username = get_token_user(cookie_token, token)
            is_admin = check_is_admin(username)

            page_num = self.get_argument("page", None)

            page_num = page_num if page_num is not None else 1
            if not isinstance(page_num, int):
                page_num = int(page_num)

            type_id = self.get_argument("select", None)

            if type_id is None:
                type_id = RequestDataType.ALL_FILES.value

            if not isinstance(type_id, int):
                type_id = int(type_id)

            print("type id", type_id)

            total = get_total_counts(type_id, username, is_admin, is_personal_only=True)
            total_page = math.ceil(total / PAGE_LIMIT)
            start = (page_num - 1) * PAGE_LIMIT
            end = total if PAGE_LIMIT * page_num > total else PAGE_LIMIT * page_num

            data = generate_data_list(username, start, end, type_id, is_admin, is_personal_only=True)

            page_info = {
                "start": start,
                "end": end,
                "total_data": total,
                "current_page": page_num,
                "total_page": total_page,
                "is_select": type_id,
                "is_admin": is_admin,
            }

            self.render("my_files.html", username=username, is_admin=is_admin, page_info=page_info, data=data, subtract=subtract_num, add=add_num)

        except BaseError as e:
            self.render("error_page.html", error_message=e.error_msg)

        except AuthError as e:
            self.render("error_page.html", error_message=e.error_msg)

        except DBError as e:
            self.render("error_page.html", error_message=e.error_msg)

        except Exception as e:
            self.render("error_page.html", error_message="Unknown error")


class TestHandler(BaseHandler):
    # def get(self):
    #     # message = {'msg': "GOOD", 'error_code': "1000"}
    #     message = b"1dsdcdcdscsd"
    #     # sleep(1)
    #     self.set_header("File-Size", 163)
    #
    #     print("Secure token: ", self.get_secure_cookie("token"))
    #     # self.set_secure_cookie("a", "123456tcookie")
    #
    #     self.write(message)
    # #
    # def post(self):
    #     print("Test api post")
    #     # self.set_header("Content-Length", 163)
    #
    #     token = self.get_cookie("token", None)
    #     print("Token:", token)
    #
    #     print("Secure Cookie", self.get_secure_cookie("a"))
    #     self.set_secure_cookie("a", "123456tcookie")
    #
    #     self.write("!23")
    #

    @async_auth_login_redirect
    async def get(self):
        cookie_token = self.get_secure_cookie("token")
        token = self.get_argument("Authorization", None)
        username = get_token_user(cookie_token, token)
        # username = "15600803270"
        is_admin = check_is_admin(username)

        self.render("test.html", username=username, is_admin=is_admin)

    def save_chunk(self, save_path, loop):
        asyncio.set_event_loop(loop)
        file_metas = self.request.files['file']
        for meta in file_metas:
            with open(save_path, 'wb') as up:
                up.write(meta['body'])

    @async_auth_login_redirect
    async def post(self):
        try:
            host_name = self.request.host_name
            remote_ip = self.request.remote_ip

            cookie_token = self.get_secure_cookie("token")
            token = self.get_argument("Authorization", None)
            username = get_token_user(cookie_token, token)

            count = self.get_argument("count", None)
            filename = self.get_argument("filename", None)
            total_chunk = self.get_argument("total_chunk", None)
            file_md5 = self.get_argument("md5", None)
            file_uuid = self.get_argument("uuid", None)
            file_uuid = file_uuid.strip(" ")

            is_intranet = check_is_intranet(username)

            if is_intranet and host_name == EXTERNAL_HOST:
                raise BaseError("1005")

            if filename is None:
                raise BaseError("1001")

            if filename.endswith("jpg") or filename.endswith("png") or int(total_chunk) <= 1:
                save_path = os.path.join("download", filename)
                file_metas = self.request.files['file']
                for meta in file_metas:
                    with open(save_path, 'wb') as up:
                        up.write(meta['body'])
                await self.flush()

                create_upload_record(username, filename, file_md5, remote_ip, is_intranet)

                self.write('success')

            else:
                # uuid_path = f"{filename.split('.')[0]}_{file_uuid}_{username}"
                uuid_path = f"{file_md5}_{username}"
                chunk_path = os.path.join("download", "tmp", uuid_path)

                if not os.path.exists(chunk_path):
                    os.mkdir(chunk_path)

                print(f"File upload API  file name: {filename} chunk count: {count}, 内存占用率: {psutil.virtual_memory().percent} | CPU 使用率: {psutil.cpu_percent(0)}")

                save_path = os.path.join(chunk_path, "%05d" % int(count))
                loop = asyncio.get_event_loop()
                loop.run_in_executor(None, self.save_chunk, save_path, loop)
                await self.flush()

                if len(os.listdir(chunk_path)) != int(total_chunk):
                    self.write("uploading")
                else:
                    download_logger.warning(f"\"UPLOAD FILE CHUNK\" [User: {username}] [File: {filename}]")
                    self.write('success')

        except TokenError as e:
            mf_logging.warning(f"Download [{filename}] error: {e.error_msg}.")
            message = {'msg': e.error_msg, 'error_code': e.error_code}
            self.write(message)

        except BaseError as e:
            mf_logging.warning(f"Download [{filename}] error: {e.error_msg}.")
            message = {'msg': e.error_msg, 'error_code': e.error_code}
            self.write(message)

        except Exception as e:
            print("e")
            message = {'msg': "Unknown Error", 'error_code': '1010'}
            self.write(message)
