__copyright__ = """ Copyright (c) 2021 HangYan. """
__license__ = 'MIT license'
__version__ = '1.0'
__author__ = 'topaz1668@gmail.com'


import os.path
import asyncio

import tornado.httpserver
import tornado.web
import tornado.options
from tornado.options import define, options


from auth import CreateUserHandler, LoginHandler, LogoutHandler, RestPasswordView, UpdatePermissionHandler

from base import IndexHandler, PageErrorHandler, TestHandler, FileListHandler, MyFilesHandler, PendingListHandler, CountFileHandler,\
    ReviewFileHandler, DeleteFileHandler, ShowRecordHandler, UserInfoHandler, ManageFilesHandler, UserListHandler, ShowMyRecordHandler


from handle_file import CheckFileExistsHandler, MergeFileHandler, UploadFileHandler, DownloadFileHandler, \
    CheckTranRightHandler


define("port", default=8011, help="run on the given port", type=int)

if __name__ == "__main__":
    tornado.options.parse_command_line()
    settings = {
        "template_path": os.path.join(os.path.dirname(__file__), "templates"),
        "static_path": os.path.join(os.path.dirname(__file__), "static"),
        "cookie_secret": "bZJc2sWbQLKos6GkHn/VB9oXwQt8S0R0kRvJ5/xJ89E=",
        "login_url": "/login",
    }

    application = tornado.web.Application([
        (r'/', IndexHandler),  # 首页

        # 用户系统
        (r'/create_user', CreateUserHandler),
        (r'/login', LoginHandler),
        (r'/logout', LogoutHandler),
        (r'/reset_password', RestPasswordView),
        (r'/update_permission', UpdatePermissionHandler),

        # 用户信息
        (r'/user_info', UserInfoHandler),
        (r'/user_list', UserListHandler),

        # 文件列表
        (r'/file_list', FileListHandler),
        (r'/pending_list', PendingListHandler),
        (r'/my_files', MyFilesHandler),

        # 文件操作
        (r'/review_file', ReviewFileHandler),
        (r'/delete_file', DeleteFileHandler),
        (r'/manage_files', ManageFilesHandler),

        # 文件下载记录
        (r'/download_record', ShowRecordHandler),
        (r'/my_record', ShowMyRecordHandler),
        (r'/file_num', CountFileHandler),

        # 上传 & 下载
        (r'/check_file_exists', CheckFileExistsHandler),
        (r'/check_tran_right', CheckTranRightHandler),

        (r'/download_file', DownloadFileHandler),  # Zip 下载

        (r'/upload_file', UploadFileHandler),  # 断点切片上传
        (r'/merge_file', MergeFileHandler),
        #
        # (r'/test', TestHandler),
        # (r'/t_merge_file', TMergeFileHandler),

        # For test
        (r'/test', TestHandler),

        # 404
        ('.*', PageErrorHandler),


    ], debug=True, **settings)

    # CA_FILE = "encry_files/WoSign-RSA-root.crt"
    # CERT_FILE = "encry_files/4916579_www.topazaws.com.pem"
    # KEY_FILE = "encry_files/4916579_www.topazaws.com.key"
    #
    # context = ssl.create_default_context(ssl.Purpose.CLIENT_AUTH)
    # context.load_cert_chain(certfile=CERT_FILE, keyfile=KEY_FILE)
    # context.load_verify_locations(CA_FILE)    # 根证书

    http_server = tornado.httpserver.HTTPServer(
        application,
        # ssl_options=context,
        max_buffer_size=10485760000)

    server2 = tornado.httpserver.HTTPServer(
        application,
        max_buffer_size=10485760000)

    http_server.listen(options.port)    #
    server2.listen(8010)    # 内网用户访问

    asyncio.get_event_loop().run_forever()
