__copyright__ = """ Copyright (c) 2021 HangYan. """
__license__ = 'MIT license'
__version__ = '1.0'
__author__ = 'topaz1668@gmail.com'

import hmac
import hashlib
from sqlalchemy import create_engine, Column, Integer, String,  DateTime, Boolean, ForeignKey
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm.session import sessionmaker
import datetime

from config import USERNAME, PASSWORD, HOST, PORT, DATABASE, SECRET

DB_URI = "mysql+pymysql://{}:{}@{}:{}/{}?charset=utf8".format(USERNAME, PASSWORD, HOST, PORT, DATABASE)
engine = create_engine(DB_URI)
Base = declarative_base(engine)


class Users(Base):
    __tablename__ = "mf_users"
    id = Column(Integer, primary_key=True, nullable=False)
    username = Column(String(32), nullable=False)
    password = Column(String(64), nullable=False)

    last_access_time = Column(String(64))
    last_remote_ip = Column(String(64))
    access_times = Column(Integer, default=0)

    is_intranet_user = Column(Boolean, default=True)        # 0: 外部用户   1: 内部用户
    is_admin = Column(Integer, default=0)               # 0: 普通用户 1: 管理员 2: 审核用户

    is_allowed_download = Column(Boolean, default=False)    # 用户是否允许上传
    is_allowed_upload = Column(Boolean, default=False)      # 用户是否允许下载

    is_delete = Column(Boolean, default=False)
    is_expired = Column(Boolean, default=False)
    register_time = Column(DateTime, default=datetime.datetime.now)

    def __repr__(self):
        return "<User name:%s>" % self.username


class UploadFiles(Base):
    __tablename__ = "mf_upload_files"
    id = Column(Integer, primary_key=True, nullable=False)
    uid = Column(Integer, ForeignKey("mf_users.id"))
    filename = Column(String(64), nullable=False)
    file_status = Column(Integer, default=0)    # 0: 未审核 (普通用户上传文件默认 0) 1: 审核成功 (管理员上传文件默认 1)  2: 审核失败
    remote_ip = Column(String(64))
    file_md5 = Column(String(64))
    upload_time = Column(DateTime, default=datetime.datetime.now)
    is_intranet = Column(Boolean, default=True)
    is_expired = Column(Boolean, default=False)
    is_delete = Column(Boolean, default=False)


class DownloadFilesRecord(Base):
    __tablename__ = "mf_download_files"
    id = Column(Integer, primary_key=True, nullable=False)
    uid = Column(Integer, ForeignKey("mf_users.id"))
    file_id = Column(Integer, ForeignKey("mf_upload_files.id"))
    remote_ip = Column(String(64))
    download_time = Column(DateTime, default=datetime.datetime.now)
    is_delete = Column(Boolean, default=False)


# class FileHashRecord(Base):
#     __tablename__ = "mf_download_files"
#     id = Column(Integer, primary_key=True, nullable=False)
#     file_md5 = Column(String(64))


def conn_db():
    DB_URI = "mysql+pymysql://{}:{}@{}:{}/{}?charset=utf8".format(USERNAME, PASSWORD, HOST, PORT, DATABASE)
    engine = create_engine(DB_URI)
    session = sessionmaker(engine)()
    return session


def create_admin():
    session = conn_db()
    password = hmac.new(SECRET, "12345678".encode(), hashlib.md5).hexdigest()
    user_exists = session.query(Users).filter(Users.username == "admin").first()
    if user_exists is None:
        user = Users(
            username="admin",
            password=password,
            is_admin=1,
            is_allowed_upload=True,
            is_allowed_download=True,
            is_intranet_user=False,
            access_times=0)
        session.add(user)
        session.commit()
    session.close()

if __name__ == "__main__":
    Base.metadata.create_all()  # create table
    create_admin()

