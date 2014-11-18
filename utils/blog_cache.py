# coding=utf8
from configs import settings
from utils import redis_connection


APP = "blog"


def set_draft_blog(uid, markdown):
    _cache = redis_connection()
    key = str("%s:draft:blog:%s" % (APP, uid))
    _cache.set(key, markdown, settings.DRAFT_BLOG_TIMEOUT)
