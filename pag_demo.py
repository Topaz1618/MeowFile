__copyright__ = """ Copyright (c) 2021 HangYan. """
__license__ = 'MIT license'
__version__ = '1.0'
__author__ = 'topaz1668@gmail.com'

from models import conn_db, UploadFiles
from sqlalchemy import func, distinct, or_, and_
import datetime
from datetime import timedelta
import time
import math


def string_to_ts(str_time):
    try:
        if not isinstance(str_time, str):
            str_time = str(str_time)

        ts = time.mktime(time.strptime(str_time, "%Y-%m-%d %H:%M:%S"))
        return ts
    except ValueError as e:
        print("Catch error: ", e)
        return 0


def ts_to_string(ts):
    if not isinstance(ts, float):
        ts = float(ts)
    time_array = time.localtime(ts)
    str_time = time.strftime("%Y-%m-%d %H:%M:%S", time_array)
    return str_time


# def page_limit():
#     """ 10+ ms """
#     session = conn_db()
#     print(f"Before: {time.time()}")
#     order_obj = session.query(ShopOrder).filter(
#         ShopOrder.user_id == 1,
#         ShopOrder.is_deleted == 0,
#     ).all()
#     print(f"After1: {time.time()}")
#
#     print(len(order_obj))
#     print(f"After2: {time.time()}")
#
#
# def page_limit_scalar():
#     """ 5 ms """
#     session = conn_db()
#     print(f"Before: {time.time()}")
#     total = session.query(func.count(distinct(ShopOrder.id))).filter(
#         ShopOrder.user_id == 1,
#         ShopOrder.is_deleted == 0,
#     ).scalar()
#
#     print(f"After: {time.time()} {total}")
#
#     total_page = total / PAGE_LIMIT
#     total_page = math.ceil(total_page)
#
#     print("Total page: ", total_page)
#     return total, total_page
#
#
# def slice_data(total, current_page=1):
#     print(f"Current page: {current_page}")
#     session = conn_db()
#     start = (current_page -1) * PAGE_LIMIT
#     end = total if PAGE_LIMIT * current_page > total else PAGE_LIMIT * current_page
#     order_obj_list = session.query(ShopOrder).filter(
#         ShopOrder.user_id == 1,
#         ShopOrder.is_deleted == 0,
#     )[start:end]
#
#     for i in order_obj_list:
#         print(i.id)
#
#
# def get_all():
#     session = conn_db()
#     order_obj_list = session.query(ShopOrder).filter(
#         ShopOrder.user_id == 1,
#     ).all()
#
#     for i in order_obj_list:
#         print(i.id)
#
#
# def order_by_colum():
#     session = conn_db()
#     results = session.query(ShopGoods).filter(ShopGoods.is_delete==0).order_by(ShopGoods.goods_price.desc()).all()   # 高到低
#     # results = session.query(ShopGoods).filter(ShopGoods.is_delete==0).order_by(ShopGoods.goods_price).all()          # 低到高
#
#     for i in results:
#         print(i.goods_price)
#
#     print(results)
#
#
# def order_by_join():
#     session = conn_db()
#     before = time.time()
#     total = session.query(func.count(distinct(ShopGoods.id))).filter(
#         or_(*[ShopGoods.menu_path == name for name in ["Actor"]]),
#     ).scalar()
#     print("Total: ", total)
#
#     results = session.query(ShopGoods).filter(
#         or_(*[ShopGoods.menu_path == name for name in ["Clothes", ]]),
#     ).order_by(ShopGoods.goods_price.desc())[0:3]  # 高到低
#
#     # goods_list_obj = session.query(ShopGoods).filter(
#     #     or_(*[ShopGoods.goods_name == name for name in filter_list])).order_by(
#     #     ShopGoods.goods_price.desc())[start:end]
#
#     after = time.time()
#     for i in results:
#         print(i.goods_price, i.goods_name)
#
#     print(results, after - before)
#
#
# def order_by_or():
#     session = conn_db()
#     results = session.query(ShopMainMenu).filter(
#         or_(
#         ShopMainMenu.id == 1,
#         ShopMainMenu.id == 2)).all()
#
#     for i in results:
#         print(i.name)
#
#     print(results)
#
#
# def get_by_negate():
#     # TEST_USER = ["15600803270", "15612345678", "15600000000", "15600809876", "15600800080","15600801111","15611111111","15612111111","15711111111","15600000001","15600000002","15600000003","15600802222","15611119999", "18310703270", "18310700909", "18434471028", "17747121395", "18622606402", "18610404330", "18582045352", "18262676236" ]
#     # TEST_USER = ["15600803270", "15612345678", "18310703270", "18434471028",]
#     session = conn_db()
#     # total = session.query(func.count(distinct(ShopUser.id))).filter(
#     #     *[ShopUser.phonenum != name for name in TEST_USER]
#     # ).scalar()
#     #
#     # session.close()
#     # print("all data", total)
#
#
# def get_avg():
#     TEST_USER = [
#         "15600803270",
#         "15612345678",
#         "18310703270",
#         "18434471028",
#         "15600801111",
#         "17747121395",
#         "15600802222",
#         "18622606402",
#         # "18610404330",
#         # "18582045352",
#         # "18262676236",
#     ]
#
#     session = conn_db()
#     access_sum = session.query(func.sum(distinct(ShopUser.access_times))).filter(
#         *[ShopUser.phonenum != name for name in TEST_USER]
#     ).scalar()
#
#     total = session.query(func.count(distinct(ShopUser.id))).filter(
#         *[ShopUser.phonenum != name for name in TEST_USER]
#     ).scalar()
#
#     access_time_avg = 0
#     if total != 0:
#         access_time_avg = round(access_sum / total, 2)
#
#
#     session.close()
#     print("all data", total)
#
#
# def test_about_cut_value():
#     session = conn_db()
#     start = 0
#     end = 2
#     uid = 1
#     myitems_list_obj = session.query(ShopPersonalItems).filter(
#         ShopPersonalItems.uid == 1,
#     )[start:end]
#     # print(myitems_list_obj)
#
#     for myitems_obj in myitems_list_obj:
#         print(myitems_obj.id)
#
#
# def or_and_toghter():
#     TEST_USER = [
#         "15600803270",
#         "15612345678",
#     ]
#     old_users_list = ["15612345678", "15101231234", "15101231236"]
#     session = conn_db()
#     usage_amount = session.query(func.count(distinct(ShopUser.id))).filter(
#         and_(
#         *[ShopUser.phonenum != name for name in TEST_USER],
#         or_(
#             *[ShopUser.phonenum == name for name in old_users_list],
#             ShopUser.access_times > 0,
#         ))
#     ).scalar()
#
#     statistics_users_obj= session.query(ShopUser).filter(
#         and_(*[ShopUser.phonenum != name for name in TEST_USER],
#         or_(
#             *[ShopUser.phonenum == name for name in old_users_list],
#             ShopUser.access_times > 0,
#         ))
#     ).all()
#
#     # for statistics_obj in statistics_users_obj:
#     #     print(statistics_obj.id, type(statistics_obj.access_times))
#     # print("!!!!!", usage_amount)
#
#     day_time = datetime.date.today()
#
#     today_usage_amount = session.query(func.count(distinct(ShopUser.id))).filter(
#         *[ShopUser.phonenum != name for name in TEST_USER],
#         ShopUser.last_access_time > day_time
#     ).scalar()
#
#     print(">>>", today_usage_amount)
#
#     today_usage_amount = session.query(ShopUser).filter(
#         *[ShopUser.phonenum != name for name in TEST_USER],
#        ShopUser.last_access_time > day_time
#     ).all()
#
#     for i in today_usage_amount:
#         print("!!!", i.last_access_time)
#
#
# def test_about_or():
#     session = conn_db()
#     TEST_USER = ["15600803270"]
#     utc_time = datetime.datetime.utcnow()
#
#     # internal_user_amount = session.query(func.count(ShopMember.id)).filter(
#     #     ShopMember.senior_expire_time >= utc_time + timedelta(days=100*12*30),
#     # ).scalar()
#
#
#     internal_user_amount = session.query(ShopMember.id).filter(
#         ShopMember.senior_expire_time >= utc_time + timedelta(days=1 * 12 * 30),
#     ).join(ShopUser).filter(
#         or_(*[ShopUser.phonenum == name for name in TEST_USER])
#     ).scalar()
#
#     member_list_obj = session.query(ShopMember).filter(
#         ShopMember.senior_expire_time >= utc_time + timedelta(days=130 * 12 * 30)
#     ).all()
#
#     uid_list = []
#     for member_obj in member_list_obj:
#         uid_list.append(member_obj.id)
#
#     user_list_obj = session.query(ShopUser).filter(
#         or_(
#             *[ShopUser.phonenum == name for name in TEST_USER],
#             *[ShopUser.id == id for id in uid_list],
#         )
#     ).all()
#
#
#     # print("!!!", user_list_obj)
#
#     for i in user_list_obj:
#         print(">>> ", i)
#
#     # internal_user_amount = session.query(ShopMember).filter(
#     #     ShopMember.senior_expire_time > utc_time + timedelta(days=10*12*30),
#     # ).all()
#     #
#     # for i in internal_user_amount:
#     #     print(i.uid, i.senior_expire_time)
#
#     print("count", internal_user_amount)
#
# def tog():
#     session = conn_db()
#     TEST_USER = ["15600803270"]
#     utc_time = datetime.datetime.utcnow()
#
#     user_list_obj = session.query(ShopUser).filter(
#         *[ShopUser.phonenum != name for name in TEST_USER]
#     ).join(ShopMember).filter(
#         ShopMember.senior_expire_time >= utc_time + timedelta(days=30 * 12 * 100),
#     ).order_by(ShopUser.id.desc())[0:10]
#
#     for i in user_list_obj:
#         print(i.phonenum)


def show_all_data():
    session = conn_db()
    file_obj_list = session.query(UploadFiles).filter(
        UploadFiles.is_intranet == True,
        UploadFiles.is_delete == False,
    ).all()

    utc_time = datetime.datetime.utcnow()

    for file_obj in file_obj_list:

        if utc_time - file_obj.upload_time > timedelta(days=1):
            print(f"file name: {file_obj.filename} Time: {file_obj.upload_time}"  )


def show_desc_data():
    session = conn_db()
    file_obj_list = session.query(UploadFiles).filter(
        UploadFiles.is_intranet == True,
        UploadFiles.is_delete == False,
    ).order_by(UploadFiles.id.desc()).all()

    utc_time = datetime.datetime.utcnow()
    for file_obj in file_obj_list:

        # if utc_time - file_obj.upload_time > timedelta(days=1):
        print(f"file name: {file_obj.filename} Time: {file_obj.upload_time}"  )


if __name__ == "__main__":
    PAGE_LIMIT = 12
    # total, total_page = page_limit_scalar()
    # or_and_toghter()
    # get_all()
    # slice_data(total)
    # for i in range(1, 7):
    #     slice_data(total, i)

    # order_by_colum()

    # order_by_join()
    # order_by_or()
    # get_by_negate()
    # get_avg()
    # test_about_cut_value()
    # a = None
    # string_to_ts(a)
    # test_about_or()
    # tog()

    show_desc_data()