#coding=utf8

import datetime

from flask import request
import flask_login

from models.base import User, create_session
from utils import user_cache

def AnonymousUserMixin():
    '''
    This is the default object for representing an anonymous user.
    '''
    session = create_session()
    user = User()
    count = user_cache.get_anonymous_count()
    anonymouser_id = 1000 + count
    user.open_id = 'anonymous%s' % anonymouser_id
    user.name = u'游客%s' % anonymouser_id
    user.token = ''
    user.create_time = datetime.datetime.now()
    session.add(user)
    session.commit()
    user_cache.incr_anonymous_count()
    flask_login.login_user(user, remember=True)
    session.close()
    return user


