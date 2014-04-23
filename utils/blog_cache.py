# coding=utf8
import pylibmc

from configs import settings

_cache = pylibmc.Client()
APP = "blog"


def set_draft_blog(uid, markdown):
    key = str("%s:draft:blog:%s" % (APP, uid))
    _cache.set(key, markdown, time=settings.DRAFT_BLOG_TIMEOUT)
