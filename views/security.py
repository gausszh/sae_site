# coding=utf8
"""
学web安全用到的一些页面
"""
from flask import Blueprint, render_template
from sae.storage import Bucket

from configs import settings


bp_security = Blueprint('security', __name__, url_prefix='/security')
bucket = Bucket(settings.STORAGE_BUCKET_DOMAIN_NAME)
bucket.put()


@bp_security.route('/wanbo/video/')
def wanbo_video():
    return render_template('security/wanbo_video.html')