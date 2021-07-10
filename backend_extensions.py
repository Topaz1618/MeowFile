__copyright__ = """ Copyright (c) 2021 HangYan. """
__license__ = 'MIT license'
__version__ = '1.0'
__author__ = 'topaz1668@gmail.com'

import random
import string
import jwt
import hmac
import hashlib
import os
from time import time, sleep
from datetime import datetime, date, timedelta
from sqlalchemy import distinct, func, or_, and_

from models import conn_db, Users, UploadFiles, DownloadFilesRecord
from base_extensions import get_user_id
from config import SECRET, INTRANET_PORT, EXTERNAL_HOST

from mf_logger import asset_logger
from mf_enum import RequestDataType, UserType, UserLevel
from code import AuthError, DBError
from mf_scp import get_from_remote, put_to_remote
from md5_demo import generate_file_md5


def check_if_user_exists(username):
    session = conn_db()
    user_exists = session.query(Users).filter(Users.username == username).first()
    if user_exists is not None:
        session.close()
        raise AuthError("1001")
    session.close()
    return True


def check_is_admin(username):
    session = conn_db()
    user_obj = session.query(Users).filter(Users.username == username).first()

    if user_obj is None:
        session.close()
        raise AuthError("1002")

    is_admin = user_obj.is_admin
    session.close()
    return is_admin


def check_is_intranet(username):
    session = conn_db()
    user_obj = session.query(Users).filter(Users.username == username).first()
    if user_obj is None:
        session.close()
        raise AuthError("1002")
    is_intranet = user_obj.is_intranet_user
    session.close()
    return is_intranet


def check_if_allowed_upload(username):
    session = conn_db()
    user_obj = session.query(Users).filter(Users.username == username).first()
    if user_obj is None:
        session.close()
        raise AuthError("1002")

    is_allowed_upload = user_obj.is_allowed_upload
    session.close()
    return is_allowed_upload


def check_if_allowed_download(username):
    session = conn_db()
    user_obj = session.query(Users).filter(Users.username == username).first()
    if user_obj is None:
        session.close()
        raise AuthError("1002")

    is_allowed_download = user_obj.is_allowed_download
    session.close()
    return is_allowed_download



def create_internal_user(username, password, is_admin):
    session = conn_db()
    try:
        password = hmac.new(SECRET, password.encode(), hashlib.md5).hexdigest()
        user = Users(username=username, password=password, is_admin=is_admin)
        session.add(user)
        session.commit()
        session.close()
    except:
        session.close()
        raise AuthError("1013")


def get_user_list():
    session = conn_db()
    user_obj_list = session.query(Users).all()
    data = []
    for user_obj in user_obj_list:
        data.append([user_obj.id, user_obj.phonenum])

    return data


def create_download_record(file_id, username, remote_ip):
    uid = get_user_id(username)

    session = conn_db()

    try:
        new_record = DownloadFilesRecord(
            uid=uid,
            file_id=file_id,
            remote_ip=remote_ip,
        )
        session.add(new_record)
        session.commit()
        session.close()

    except Exception as e:
        session.close()
        raise DBError("4002")


def get_file_list(username):
    uid = get_user_id(username)
    session = conn_db()

    try:
        data = list()

        file_obj_list = session.query(UploadFiles).filter(
            UploadFiles.is_delete == 0
        ).all()

        for file_obj in file_obj_list:
            user_obj = session.query(Users).filter(
                Users.id == file_obj.uid,
            ).first()

            if user_obj is None:
                raise AuthError("1001")

            single_file = {
                "id": file_obj.id,
                "file_name": file_obj.name,
                "uploader": user_obj.id,
                "upload_time": file_obj.upload_time,
                "file_status": file_obj.file_status,
            }

            data.append(single_file)

        session.close()
        return data

    except Exception as e:
        session.close()
        raise DBError("4005")


def get_file_name(username, file_id):
    uid = get_user_id(username)
    session = conn_db()

    try:
        file_obj = session.query(UploadFiles).filter(
            UploadFiles.id == file_id,
            UploadFiles.is_delete == 0
        ).first()

        if file_obj is None:
            raise Exception

        file_name = file_obj.filename
        session.close()
        return file_name

    except Exception as e:
        session.close()
        raise DBError("4005")


def create_upload_record(username, filename, file_md5, remote_ip, is_intranet):
    uid = get_user_id(username)

    is_admin = check_is_admin(username)

    session = conn_db()
    try:
        file_status = 0
        if is_admin or not is_intranet:
            file_status = 1

        new_record = UploadFiles(
            uid=uid,
            filename=filename,
            file_md5=file_md5,
            remote_ip=remote_ip,
            file_status=file_status,
            is_intranet=is_intranet,
        )
        session.add(new_record)
        session.commit()
        session.close()

    except Exception as e:
        session.close()
        raise DBError("4005")


def get_total_counts(type_id, username, is_admin=UserLevel.NORMAL.value, is_personal_only=False):
    uid = get_user_id(username)

    try:
        session = conn_db()
        if type_id == RequestDataType.ALL_FILES.value:
            if is_admin in UserLevel.REVIEW_GROUP.value and not is_personal_only:
                total = session.query(func.count(distinct(UploadFiles.id))).filter(
                    UploadFiles.is_delete == False,
                ).scalar()
            else:
                total = session.query(func.count(distinct(UploadFiles.id))).filter(
                    UploadFiles.is_delete == False,
                    UploadFiles.uid == uid,
                ).scalar()

        elif type_id == RequestDataType.PENDING_FILES.value:
            if is_admin in UserLevel.REVIEW_GROUP.value and not is_personal_only:
                total = session.query(func.count(distinct(UploadFiles.id))).filter(
                    UploadFiles.is_delete == False,
                    UploadFiles.file_status == RequestDataType.PENDING_FILES.value,
                ).scalar()
            else:
                total = session.query(func.count(distinct(UploadFiles.id))).filter(
                    UploadFiles.is_delete == False,
                    UploadFiles.uid == uid,
                    UploadFiles.file_status == RequestDataType.PENDING_FILES.value,
                ).scalar()

        elif type_id == RequestDataType.APPROVED_FILES.value:
            if is_personal_only:
                total = session.query(func.count(distinct(UploadFiles.id))).filter(
                    UploadFiles.is_delete == False,
                    UploadFiles.uid == uid,
                    UploadFiles.file_status == RequestDataType.APPROVED_FILES.value,
                ).scalar()
            else:
                total = session.query(func.count(distinct(UploadFiles.id))).filter(
                    UploadFiles.is_delete == False,

                    UploadFiles.file_status == RequestDataType.APPROVED_FILES.value,
                ).scalar()

        elif type_id == RequestDataType.FAILED_FILES.value:
            if is_admin in UserLevel.REVIEW_GROUP.value and not is_personal_only:
                total = session.query(func.count(distinct(UploadFiles.id))).filter(
                    UploadFiles.is_delete == False,
                    UploadFiles.file_status == RequestDataType.FAILED_FILES.value,
                ).scalar()

            else:
                total = session.query(func.count(distinct(UploadFiles.id))).filter(
                    UploadFiles.is_delete == False,
                    # UploadFiles.uid == uid,
                    UploadFiles.file_status == RequestDataType.FAILED_FILES.value,
                ).scalar()

        print(f"After: {time()} {total}")
        session.close()
        return total

    except Exception as e:
        raise DBError("4001")


def generate_data_list(username, start, end, request_type, is_admin, is_personal_only=False):
    """
    :param start: 分页数据起始位置
    :param end: 分页数据结束位置
    :param request_type: 请求类型 0: 未审核 １: 审核成功 2: 审核失败 3: 所有状态文件(仅 admin)
    :param is_personal_only: True: 仅显示自己上传文件
    :return:
    """
    uid = get_user_id(username)
    try:
        session = conn_db()
        if request_type == RequestDataType.ALL_FILES.value:
            if is_admin in UserLevel.REVIEW_GROUP.value and not is_personal_only:
                file_obj_list = session.query(UploadFiles).filter(
                    UploadFiles.is_delete == False,
                ).order_by(UploadFiles.id.desc())[start:end]
            else:
                file_obj_list = session.query(UploadFiles).filter(
                    UploadFiles.is_delete == False,
                    UploadFiles.uid == uid,
                ).order_by(UploadFiles.id.desc())[start:end]

        elif request_type == RequestDataType.APPROVED_FILES.value:
            if is_personal_only:
                file_obj_list = session.query(UploadFiles).filter(
                    UploadFiles.uid == uid,
                    UploadFiles.file_status == request_type,
                    UploadFiles.is_delete == False,
                ).order_by(UploadFiles.id.desc())[start:end]
            else:
                file_obj_list = session.query(UploadFiles).filter(
                    UploadFiles.file_status == request_type,
                    UploadFiles.is_delete == False,
                ).order_by(UploadFiles.id.desc())[start:end]

        else:
            if is_admin in UserLevel.REVIEW_GROUP.value and not is_personal_only:
                file_obj_list = session.query(UploadFiles).filter(
                    UploadFiles.is_delete == False,
                    UploadFiles.file_status == request_type,
                ).order_by(UploadFiles.id.desc())[start:end]

            else:
                file_obj_list = session.query(UploadFiles).filter(
                    UploadFiles.is_delete == False,
                    UploadFiles.file_status == request_type,
                    UploadFiles.uid == uid,
                ).order_by(UploadFiles.id.desc())[start:end]

        data = list()
        for file_obj in file_obj_list:
            owner_id = file_obj.uid
            user_obj = session.query(Users).filter(
                Users.id == owner_id,
            ).first()
            if user_obj is None:
                raise AuthError("1002")

            owner = user_obj.username
            download_counts = session.query(func.count(distinct(DownloadFilesRecord.id))).filter(
                DownloadFilesRecord.file_id == file_obj.id,
            ).scalar()

            data.append(
                {"id": file_obj.id,
                 "name": file_obj.filename,
                 "user": owner,
                 "date": file_obj.upload_time,
                 "status": file_obj.file_status,
                 "download_count": download_counts,
                 },
            )

        session.close()
        return data
    except Exception as e:
        raise DBError("4005")


def update_review_status(file_id, status_id, username):
    session = conn_db()

    file_obj = session.query(UploadFiles).filter(
        UploadFiles.id == file_id,
        UploadFiles.is_delete == False,
    ).first()

    if file_obj is None:
        session.close()
        raise DBError("4006")

    file_obj.file_status = status_id
    session.commit()
    # if status_id == 1:
    #     filename = f"download/{file_obj.filename}"
    #     get_from_remote(filename)

    session.close()


def delete_file(username, file_id, is_admin):
    session = conn_db()

    file_obj = session.query(UploadFiles).filter(
        UploadFiles.id == file_id,
    ).first()
    if file_obj is None:
        session.close()
        raise DBError("4006")

    if is_admin != UserLevel.ADMIN.value:
        uid = get_user_id(username)
        if file_obj.uid != uid:
            session.close()
            raise DBError("4007")

    asset_logger.warning(f"\"DOWNLOAD FILE\" [Username: {username}] [Filename: {file_obj.filename}] ")

    file_obj.is_delete = True
    session.commit()
    session.close()


def get_total_records(username, is_admin, is_personal_only):
    uid = get_user_id(username)
    session = conn_db()
    if is_admin in UserLevel.REVIEW_GROUP.value:
        if is_personal_only:
            download_counts = session.query(func.count(distinct(DownloadFilesRecord.id))).filter(
                DownloadFilesRecord.uid == uid,
            ).scalar()
        else:
            download_counts = session.query(func.count(distinct(DownloadFilesRecord.id))).scalar()

    else:
        download_counts = session.query(func.count(distinct(DownloadFilesRecord.id))).filter(
            DownloadFilesRecord.uid == uid,
        ).scalar()

    session.close()
    return download_counts


def get_record_list(username, start, end, is_admin, is_personal_only=False):
    uid = get_user_id(username)
    try:
        session = conn_db()
        if is_admin in UserLevel.REVIEW_GROUP.value:
            if is_personal_only:
                record_obj_list = session.query(DownloadFilesRecord).filter(
                    DownloadFilesRecord.uid == uid,
                ).order_by(DownloadFilesRecord.id.desc())[start:end]
            else:
                record_obj_list = session.query(DownloadFilesRecord).order_by(DownloadFilesRecord.id.desc())[start:end]
        else:
            record_obj_list = session.query(DownloadFilesRecord).filter(
                DownloadFilesRecord.uid == uid,
            ).order_by(DownloadFilesRecord.id.desc())[start:end]


        data = list()

        session = conn_db()

        for record_obj in record_obj_list:

            file_obj = session.query(UploadFiles).filter(
                UploadFiles.id == record_obj.file_id,
            ).first()

            download_user_obj = session.query(Users).filter(
                Users.id == record_obj.uid,
            ).first()

            if download_user_obj is not None:
                download_user = download_user_obj.username
            else:
                download_user = "用户不存在"

            data.append({
                "id": record_obj.id,
                "uid": uid,
                "username": username,
                "download_user": download_user,
                "fid": record_obj.file_id,
                "file_name": file_obj.filename,
                "date": record_obj.download_time,
                "remote_ip": record_obj.remote_ip,
                "is_file_deleted": file_obj.is_delete,
            },
            )

        session.close()
        return data
    except Exception as e:
        raise DBError("4005")


def get_user_info(username):
    session = conn_db()
    user_obj = session.query(Users).filter(
        Users.username == username,
    ).first()

    if user_obj is None:
        raise AuthError("1002")     # 用户不存在

    uid = user_obj.id
    download_count = session.query(func.count(distinct(DownloadFilesRecord.id))).filter(
        DownloadFilesRecord.uid == uid,
    ).scalar()

    upload_count = session.query(func.count(distinct(UploadFiles.id))).filter(
        UploadFiles.uid == uid,
    ).scalar()

    data = {
        "uid": user_obj.id,
        "username": username,
        "create_time": user_obj.register_time,
        "upload_count": upload_count,
        "download_count": download_count,
        "is_admin": user_obj.is_admin,
        "user_type": user_obj.is_intranet_user,
        "is_allowed_upload": user_obj.is_allowed_upload,
        "is_allowed_download": user_obj.is_allowed_download,

    }
    session.close()
    return data


def delete_resources(username, resource_list):
    try:
        file_list = resource_list.split(",")
        session = conn_db()
        for file_id in file_list:
            if not isinstance(file_id, int):
                file_id = int(file_id)

            file_obj = session.query(UploadFiles).filter(
                UploadFiles.id == file_id,
            ).first()

            if file_obj is not None:
                asset_logger.warning(f"\"Delete FILE\" [Admin: {username}] [Filename: {file_obj.filename}] ")
                file_obj.is_delete = 1
                session.commit()


        session.close()
    except Exception as e:
        raise DBError("4008")


def get_total_users(user_type):
    session = conn_db()
    if user_type == UserType.ALL_USER.value:
        user_count = session.query(func.count(distinct(Users.id))).scalar()

    elif user_type == UserType.INTRANET_USER.value:
        user_count = session.query(func.count(distinct(Users.id))).filter(
            Users.is_intranet_user == True,
        ).scalar()

    elif user_type == UserType.EXTRANET_USER.value:
        user_count = session.query(func.count(distinct(Users.id))).filter(
            Users.is_intranet_user == False,
        ).scalar()

    session.close()
    return user_count


def get_user_list(start, end, user_type):
    session = conn_db()
    if user_type == UserType.ALL_USER.value:
        user_obj_list = session.query(Users).order_by(Users.id.desc())[start:end]

    elif user_type == UserType.INTRANET_USER.value:
        user_obj_list = session.query(Users).filter(
            Users.is_intranet_user == True,
        ).order_by(Users.id.desc())[start:end]

    elif user_type == UserType.EXTRANET_USER.value:
        user_obj_list = session.query(Users).filter(
            Users.is_intranet_user == False,
        ).order_by(Users.id.desc())[start:end]

    data = list()
    for user_obj in user_obj_list:
        username = user_obj.username
        single_user = get_user_info(username)
        data.append(single_user)

    session.close()
    return data


def check_expired_file():
    session = conn_db()
    file_obj_list = session.query(UploadFiles).filter(
        UploadFiles.is_intranet == True,
        UploadFiles.is_delete == False,
        UploadFiles.is_expired == False,
        UploadFiles.file_status == 1,
    ).all()

    utc_time = datetime.utcnow()

    for file_obj in file_obj_list:

        if utc_time - file_obj.upload_time > timedelta(days=1):
            print(f"file name: {file_obj.filename} Time: {file_obj.upload_time}")
            file_obj.is_delete = True
            file_obj.is_expired = True
            session.commit()

    session.close()


def check_if_file_exists(md5_sum):
    session = conn_db()

    file_obj = session.query(UploadFiles).filter(
        UploadFiles.file_md5 == md5_sum,
        UploadFiles.is_delete == False,
    ).first()

    if file_obj is None:
        session.close()
        return False

    filename = file_obj.filename
    file_path = f'download/{filename}'
    print(file_path)
    if not os.path.exists(file_path):
        return False

    if md5_sum != generate_file_md5(file_path):
        print(md5_sum, generate_file_md5(file_path))
        session.close()
        return False

    session.close()
    print("hey there ")
    return True


def check_upload_record(md5_sum, blocksize, username):
    slice_list = list()

    total_size = 0
    pre_path = "download/tmp/"
    file_path = os.path.join(pre_path, f"{md5_sum}_{username}");
    if os.path.exists(file_path):
        file_list = os.listdir(file_path)
        for file in file_list:
            file_size = os.path.getsize(os.path.join(file_path, file))
            if file_size == blocksize:
                slice_list.append(int(file))

            total_size += file_size

    data = {
        "current_pos": total_size,
        "slice_list": slice_list,
    }

    print(data)

    return data





