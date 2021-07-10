__copyright__ = """ Copyright (c) 2021 HangYan. """
__license__ = 'MIT license'
__version__ = '1.0'
__author__ = 'topaz1668@gmail.com'

from code import AuthError

from models import conn_db, Users


def get_user_id(username):
    session = conn_db()
    user_obj = session.query(Users).filter(
        Users.username == username,
    ).first()\

    if user_obj is None:
        session.close()
        raise AuthError("1002")

    user_id = user_obj.id
    session.close()
    return user_id

