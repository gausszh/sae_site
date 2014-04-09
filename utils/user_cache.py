# coding=utf8

try:
    import simplejson as json
except Exception:
    import json
import datetime
from sqlalchemy.sql import or_
from models.base import create_session, User
from configs import settings
import sae.kvdb

_cache = sae.kvdb.KVClient()
APP = "base"


def get_user(uid, format="json"):
    key = str("%s:user:%s" % (APP, uid))
    userinfo = _cache.get(key)
    new = False
    if not userinfo:
        session = create_session()
        userinfo = session.query(User).filter(or_(User.id == uid, User.open_id == uid )).first()
        userinfo = orm2json(userinfo)
        _cache.set(key, json.dumps(userinfo), time=settings.CACHE_TIMEOUT)
        new = True
        session.close()
    if not new:
        userinfo = json.loads(userinfo)

    if format == 'object' and userinfo:
        user = User() 
        for k in userinfo:
            setattr(user, k, userinfo.get(k))
        userinfo = user
    return userinfo or None

def delete_user(uid):
    key = "%s:user:%s" % (APP, uid)
    _cache.delete(key)


def get_anonymous_count():
	key = "%s:anonymous:count" % APP
	count = _cache.get(key)
	if not count:
		session = create_session()
		count = session.query(User).filter(User.open_id.startswith("anonymous")).count()
		_cache.set(key, count, time=settings.CACHE_TIMEOUT)
		session.close()
	return int(count)

def incr_anonymous_count():
	key = "%s:anonymous:count" % APP
	count = get_anonymous_count()
	_cache.set(key, count + 1, time=settings.CACHE_TIMEOUT)

def orm2json(orm):
    """
    将sqlalchemy返回的对象转换为可序列话json类型的对象
    """
    def single2py(instance):
        d = {}
        if instance:
            keys = instance.__dict__.keys()
            for key in keys:
                if key.startswith('_'):
                    continue
                value = getattr(instance, key)
                d[key] = isinstance(value, datetime.datetime) and \
                    value.strftime('%Y-%m-%d %H:%M:%S') or value
        return d
    if isinstance(orm, list):
        return [single2py(ins) for ins in orm]
    return single2py(orm)
