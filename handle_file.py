__copyright__ = """ Copyright (c) 2021 HangYan. """
__license__ = 'MIT license'
__version__ = '1.0'
__author__ = 'topaz1668@gmail.com'

import os
import stat
import asyncio
import psutil
from time import time, sleep
from urllib.parse import quote

from tornado.web import RequestHandler

from backend_extensions import get_file_name, create_upload_record, create_download_record, check_is_admin, check_is_intranet, \
    check_if_file_exists, check_if_allowed_upload, check_if_allowed_download, check_upload_record
from config import INTRANET_HOST, EXTERNAL_HOST
from code import BaseError, DBError, TokenError, AuthError
from mf_utils import async_auth_login_redirect, get_token_user, auth_login_redirect
from mf_logger import logger as mf_logging
from mf_logger import download_logger
from mf_enum import RequestDataType, UserType
from mf_scp import put_to_remote
from md5_demo import generate_file_md5
from base import BaseHandler


class OldMergeFileHandler(BaseHandler):
    """ 上传切片合并 API """

    def merge_file(self, chunk_path, filename, file_path, username):
        files = sorted(os.listdir(chunk_path))
        with open(file_path, "wb+") as fd:
            for file in files:
                with open(os.path.join(chunk_path, file), "rb") as f:
                    data = f.read()
                    fd.write(data)
                    fd.flush()
                print( f"File merge API file name: {chunk_path}  Current count: {file}, 内存占用率: {psutil.virtual_memory().percent} | CPU 使用率: {psutil.cpu_percent(0)}")

        is_intranet = check_is_intranet(username)
        remote_ip = self.request.remote_ip

        file_md5 = generate_file_md5(filename)
        create_upload_record(username, filename, file_md5, remote_ip, is_intranet)

        # if is_intranet:
        #     put_to_remote(file_path, EXTERNAL_HOST)
        # else:
        #     put_to_remote(file_path, INTRANET_HOST)
        #     print("Done !!!!!!!!!!! ")

        download_logger.warning(f"\"MERGE FILE\" [User: {username}] [File: {file_path}]")

    @async_auth_login_redirect
    async def post(self):
        try:
            filename = self.get_argument("filename", None)
            total_chunk = self.get_argument("total_chunk", None)
            file_uuid = self.get_argument("uuid", None)
            cookie_token = self.get_secure_cookie("token")
            token = self.get_argument("Authorization", None)
            username = get_token_user(cookie_token, token)

            uuid_path = f"{filename.split('.')[0]}_{file_uuid}_{username}"
            chunk_path = os.path.join("download", "tmp", uuid_path)
            file_path = os.path.join("download", filename)
            if os.path.exists(file_path):
                print(f"File {filename} already exist, ready to delete it. ")
                os.remove(file_path)

            if not os.path.exists(chunk_path):
                self.write("false")
                return

            if len(os.listdir(chunk_path)) != int(total_chunk):
                self.write("false")
                return

            loop = asyncio.get_event_loop()
            loop.run_in_executor(None, self.merge_file, chunk_path, filename, file_path, username)
            self.write("true")

        except Exception as e:
            message = {'msg': "Unknown Error", 'error_code': '1010'}
            self.write(message)


class DownloadFileHandler(BaseHandler):
    def get_content_size(self, file_path):
        stat_result = os.stat(file_path)
        content_size = stat_result[stat.ST_SIZE]
        return content_size

    @async_auth_login_redirect
    async def get(self):
        try:
            host_name = self.request.host_name

            current_pos = self.get_argument("current_pos", None)
            file_id = self.get_argument("fid", None)

            cookie_token = self.get_secure_cookie("token")
            token = self.get_argument("Authorization", None)
            username = get_token_user(cookie_token, token)

            is_intranet = check_is_intranet(username)
            if is_intranet and host_name == EXTERNAL_HOST:
                raise BaseError("1005")

            is_allowed_download = check_if_allowed_download(username)
            if not is_allowed_download:
                raise BaseError("1011")

            if not isinstance(file_id, int):
                file_id = int(file_id)

            filename = get_file_name(username, file_id)
            remote_ip = self.request.remote_ip

            CHUNK_SIZE = 1024 *1024 * 100

            path = os.path.dirname(os.path.abspath(__file__))
            local_file = os.path.join(path, 'download', filename)
            file_exists = os.path.exists(local_file)

            if not file_exists:
                print("Does not exist ")
                raise BaseError("1003")

            file_size = self.get_content_size(local_file)

            self.set_header('Content-Type', 'application/octet-stream')
            self.set_header("Content-Disposition", "attachment; filename=%s" % quote(filename))  # 中文支持
            self.set_header("File-Size", file_size)
            count = 0

            create_download_record(file_id, username, remote_ip)

            with open(local_file, 'rb', buffering=100000) as f:
                if current_pos is not None:
                    current_pos = int(current_pos) if not isinstance(current_pos, int) else current_pos
                    f.seek(current_pos)

                while True:
                    count += 1
                    print(f"Download api: {count}, 内存占用率: {psutil.virtual_memory().percent} | CPU 使用率: {psutil.cpu_percent(0)}")
                    chunk = f.read(CHUNK_SIZE)
                    print(len(chunk))
                    f.flush()
                    if not chunk:
                        break

                    self.write(chunk)
                    await self.flush()

                    # break for test ↓
                    # break

            download_logger.warning(f"\"DOWNLOAD FILE\" [Username: {username}] [Filename: {filename}] ")
            self.finish()
            mf_logging.warning(f"Download [{filename}] completed.")

        except TokenError as e:
            # mf_logging.warning(f"Download [{filename}] error: {e.error_msg}.")
            # message = {'msg': e.error_msg, 'error_code': e.error_code}
            # self.write(message)
            self.render("error_page.html", error_message=e.error_msg)

        except BaseError as e:
            # mf_logging.warning(f"Download [{filename}] error: {e.error_msg}.")
            # message = {'msg': e.error_msg, 'error_code': e.error_code}
            # self.write(message)
            self.render("error_page.html", error_message=e.error_msg)

        except DBError as e:
            # mf_logging.warning(f"Download [{filename}] error: {e.error_msg}.")
            # message = {'msg': e.error_msg, 'error_code': e.error_code}
            # self.write(message)
            self.render("error_page.html", error_message=e.error_msg)

        except Exception as e:
            print("E", e)
            # self.write({'msg': "Unknown Error", 'error_code': '1010'})
            # self.finish()
            self.render("error_page.html", error_message="Unknown error")


class CheckFileExistsHandler(BaseHandler):
    async def post(self):
        remote_ip = self.request.remote_ip
        cookie_token = self.get_secure_cookie("token")
        token = self.get_argument("Authorization", None)
        username = get_token_user(cookie_token, token)

        filename = self.get_argument("filename", None)
        is_intranet = check_is_intranet(username)

        md5_sum = self.get_argument("md5_sum", None)
        blocksize = self.get_argument("blocksize", None)


        if blocksize is None:
            blocksize = 50

        if not isinstance(blocksize, int):
            blocksize = int(blocksize)

        is_exists = check_if_file_exists(md5_sum)
        if is_exists:
            create_upload_record(username, filename, md5_sum, remote_ip, is_intranet)
            message = {"msg": "File already exists.", "error_code": "0"}

        else:
            data = check_upload_record(md5_sum, blocksize, username)
            print("!!!!! ", data)

            message = {"msg": data, "error_code": "1"}

            if data["current_pos"] == 0:
                message = {"msg": data, "error_code": "2"}

        self.write(message)


class CheckTranRightHandler(BaseHandler):
    @auth_login_redirect
    def get(self):
        try:
            cookie_token = self.get_secure_cookie("token")
            token = self.get_argument("Authorization", None)
            username = get_token_user(cookie_token, token)
            check_type = self.get_argument("check_type", None)

            if not isinstance(check_type, int):
                check_type = int(check_type)

            if check_type == 0:
                res = check_if_allowed_upload(username)
                if not res:
                    raise BaseError("1010")

            elif check_type == 1:
                res = check_if_allowed_upload(username)
                if not res:
                    raise BaseError("1011")

            else:
                raise BaseError("1002")

        except TokenError as e:
            self.render("error_page.html", error_message=e.error_msg)

        except BaseError as e:
            self.render("error_page.html", error_message=e.error_msg)

        except Exception as e:
            print("e", e)
            self.render("error_page.html", error_message="Unknown error")

    @auth_login_redirect
    def post(self):
        try:
            cookie_token = self.get_secure_cookie("token")
            token = self.get_argument("Authorization", None)
            username = get_token_user(cookie_token, token)
            check_type = self.get_argument("check_type", None)

            if not isinstance(check_type, int):
                check_type = int(check_type)

            if check_type == 0:
                res = check_if_allowed_upload(username)
                if not res:
                    raise BaseError("1010")

            elif check_type == 1:
                res = check_if_allowed_upload(username)
                if not res:
                    raise BaseError("1011")

            else:
                raise BaseError("1002")

            message = {'msg': res, 'error_code': "1000"}

        except TokenError as e:
            message = {'msg': e.error_msg, 'error_code': e.error_code}

        except BaseError as e:
            message = {'msg': e.error_msg, 'error_code': e.error_code}

        except Exception as e:
            print("e", e)
            message = {'msg': "Unknown Error", 'error_code': '1010'}

        self.write(message)


class MergeFileHandler(BaseHandler):
    """ 上传切片合并 API """

    def merge_file(self, chunk_path, filename, file_path, username):
        files = sorted(os.listdir(chunk_path))
        print("!!!!!!", file_path)
        with open(file_path, "wb+") as fd:
            for file in files:
                with open(os.path.join(chunk_path, file), "rb") as f:
                    data = f.read()
                    fd.write(data)
                    fd.flush()
                print( f"File merge API file name: {chunk_path}  Current count: {file}, 内存占用率: {psutil.virtual_memory().percent} | CPU 使用率: {psutil.cpu_percent(0)}")

        is_intranet = check_is_intranet(username)
        remote_ip = self.request.remote_ip

        file_md5 = generate_file_md5(file_path)
        create_upload_record(username, filename, file_md5, remote_ip, is_intranet)

        # if is_intranet:
        #     put_to_remote(file_path, EXTERNAL_HOST)
        # else:
        #     put_to_remote(file_path, INTRANET_HOST)
        #     print("Done !!!!!!!!!!! ")

        download_logger.warning(f"\"MERGE FILE\" [User: {username}] [File: {file_path}]")

    @async_auth_login_redirect
    async def post(self):
        try:
            filename = self.get_argument("filename", None)
            total_chunk = self.get_argument("total_chunk", None)
            file_uuid = self.get_argument("uuid", None)
            cookie_token = self.get_secure_cookie("token")
            token = self.get_argument("Authorization", None)
            username = get_token_user(cookie_token, token)
            file_md5 = self.get_argument("md5", None)

            uuid_path = f"{file_md5}_{username}"
            print(uuid_path)
            chunk_path = os.path.join("download", "tmp", uuid_path)
            file_path = os.path.join("download", filename)
            if os.path.exists(file_path):
                print(f"File {filename} already exist, ready to delete it. ")
                os.remove(file_path)

            if not os.path.exists(chunk_path):
                self.write("false")
                return

            if len(os.listdir(chunk_path)) != int(total_chunk):

                self.write("false")
                return

            loop = asyncio.get_event_loop()
            loop.run_in_executor(None, self.merge_file, chunk_path, filename, file_path, username)
            self.write("true")

        except Exception as e:
            message = {'msg': "Unknown Error", 'error_code': '1010'}
            self.write(message)


class OldUploadFileHandler(BaseHandler):
    """ zip 上传接口 (权限限制)  """

    @async_auth_login_redirect
    async def get(self):
        cookie_token = self.get_secure_cookie("token")
        token = self.get_argument("Authorization", None)
        username = get_token_user(cookie_token, token)
        # username = "15600803270"
        is_admin = check_is_admin(username)

        self.render("upload_file.html", username=username, is_admin=is_admin)

    def save_chunk(self, save_path, loop):
        asyncio.set_event_loop(loop)
        file_metas = self.request.files['file']
        for meta in file_metas:
            with open(save_path, 'wb') as up:
                up.write(meta['body'])

    def put_file(self, save_path, is_intranet, loop):
        asyncio.set_event_loop(loop)

        if is_intranet:
            put_to_remote(save_path, EXTERNAL_HOST)
        else:
            put_to_remote(save_path, INTRANET_HOST)

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
            file_uuid = self.get_argument("uuid", None)
            file_uuid = file_uuid.strip(" ")

            is_intranet = check_is_intranet(username)
            is_allowed_upload = check_if_allowed_upload(username)

            if is_intranet and host_name == EXTERNAL_HOST:
                raise BaseError("1005")

            if not is_allowed_upload:
                raise BaseError("1010")

            if filename is None:
                raise BaseError("1001")

            if filename.endswith("jpg") or filename.endswith("png") or int(total_chunk) <= 1:
                save_path = os.path.join("download", filename)
                file_metas = self.request.files['file']
                for meta in file_metas:
                    with open(save_path, 'wb') as up:
                        up.write(meta['body'])
                await self.flush()

                file_md5 = generate_file_md5(filename)
                create_upload_record(username, filename, file_md5, remote_ip, is_intranet)

                loop = asyncio.get_event_loop()
                loop.run_in_executor(None, self.put_file, save_path, is_intranet, loop)

                self.write('success')

            else:
                uuid_path = f"{filename.split('.')[0]}_{file_uuid}_{username}"
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
                    # create_upload_record(username, filename, remote_ip, is_intranet)
                    download_logger.warning(f"\"UPLOAD FILE CHUNK\" [User: {username}] [File: {filename}]")
                    self.write('success')

        except TokenError as e:
            mf_logging.warning(f"Download [{filename}] error: {e.error_msg}.")
            message = {'msg': e.error_msg, 'error_code': e.error_code}
            self.write(message)
            # self.render("error_page.html", error_message=e.error_msg)

        except BaseError as e:
            mf_logging.warning(f"Download [{filename}] error: {e.error_msg}.")
            message = {'msg': e.error_msg, 'error_code': e.error_code}
            self.write(message)
            # self.render("error_page.html", error_message=e.error_msg)

        except Exception as e:
            print("e")
            message = {'msg': "Unknown Error", 'error_code': '1010'}
            self.write(message)
            # self.render("error_page.html", error_message="Unknown error")


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


class UploadFileHandler(BaseHandler):

    @async_auth_login_redirect
    async def get(self):
        cookie_token = self.get_secure_cookie("token")
        token = self.get_argument("Authorization", None)
        username = get_token_user(cookie_token, token)
        # username = "15600803270"
        is_admin = check_is_admin(username)

        self.render("upload_file.html", username=username, is_admin=is_admin)

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

                # if is_intranet:
                #     put_to_remote(save_path, EXTERNAL_HOST)
                # else:
                #     put_to_remote(save_path, INTRANET_HOST)

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
