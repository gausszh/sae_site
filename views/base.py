#coding=utf8

import datetime
from flask import Blueprint, request, jsonify, render_template, redirect
import flask_login 
import weibo as sinaweibo

from models.base import create_session, User
from utils import user_cache
from configs import settings


bp_base = Blueprint('base', __name__, url_prefix='/base')


@bp_base.route('/weibo/login/')
def weibo_login():
    api = sinaweibo.Client(settings.API_KEY,settings.API_SECRET,settings.REDIRECT_URI)
    code = request.args.get('code')
    try:
        api.set_code(code)
    except Exception, e:
        return redirect('/blog/')

    sinainfo = api.token
    user = user_cache.get_user(sinainfo.get('uid'), format='object')
    if user:
        flask_login.login_user(user, remember=True)
    else:
        user = User()
        user.open_id = sinainfo.get('uid')
        user.token = sinainfo.get('access_token')
        userinfo = api.get('users/show', uid=sinainfo.get('uid'))
        user.name = userinfo.get('name')
        user.address = userinfo.get('location')
        user.create_time = datetime.datetime.now()
        session = create_session()
        session.add(user)
        session.commit()
        flask_login.login_user(user, remember=True)
        session.close()
    return redirect('/blog/')


@bp_base.route('/logout/')
def logout():
    flask_login.logout_user()
    return redirect('/blog/')