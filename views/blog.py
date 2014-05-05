# coding=utf8

import datetime
import urllib
from flask import Blueprint, request, jsonify, render_template, g
import flask_login
from sae.storage import Bucket

from models.blog import create_session, BlogArticle
from utils.blog_cache import set_draft_blog
from configs import settings


bp_blog = Blueprint('blog', __name__, url_prefix='/blog')
bucket = Bucket(settings.STORAGE_BUCKET_DOMAIN_NAME)
bucket.put()


@bp_blog.route('/')
@bp_blog.route('/list/')
def list():
    session = create_session()
    blogs = session.query(BlogArticle).order_by(BlogArticle.update_time.desc())\
        .all()
    session.close()
    return render_template('blog/blog_list.html', blogs=blogs)


@bp_blog.route('/delete/<int:blog_id>/', methods=['POST'])
@flask_login.login_required
def delete(blog_id):
    session = create_session()
    blog = session.query(BlogArticle).filter_by(id=blog_id).first()
    if blog.create_by == g.user.id:
        blog.is_active = 0
        session.commit()
        session.close()
        return jsonify(ok=True, data={'blog_id': blog_id})
    session.close()
    return jsonify(ok=False, reason=u'数据错误')


@bp_blog.route('/draft/', methods=['POST'])
@flask_login.login_required
def draft():
    """
    保存未上传的文章为草稿
    """
    form = request.form
    markdown = form.get('markdown', '')
    set_draft_blog(flask_login.current_user.id, markdown)
    return jsonify(ok=True)


@bp_blog.route('/edit/<int:blog_id>/', methods=['GET', 'POST'])
@bp_blog.route('/edit/', methods=['GET', 'POST'])
@flask_login.login_required
def edit(blog_id=0):
    if request.method == 'GET':
        if blog_id == 0:
            blog = None
        else:
            session = create_session()
            blog = session.query(BlogArticle).filter_by(id=blog_id).first()
            session.close()
        return render_template('blog/blog_edit.html', blog=blog)

    if request.method == 'POST':
        form = request.form
        markdown = form.get('markdown')
        title = form.get('title')
        blog_id = form.get('blog_id')
        if markdown and title and (len(markdown.strip()) * 
                                   len(title.strip()) > 0):

            session = create_session()
            now = datetime.datetime.now()
            # blog_id belong to this user
            if blog_id:
                blog = session.query(BlogArticle).filter_by(id=blog_id).first()
            if not blog_id or not blog:
                blog = BlogArticle()
                blog.create_by = flask_login.current_user.id
                blog.create_time = now
            blog.is_active = 1
            blog.update_time = now
            blog.title = title
            blog.markdown = markdown
            session.add(blog)
            session.commit()
            blog_id = blog.id
            session.close()
            return jsonify(ok=True, data={'blog_id': blog_id})
        return jsonify(ok=False, reason=u'数据错误')


@bp_blog.route('/view/<int:blog_id>/')
def view_blog(blog_id):
    session = create_session()
    query = session.query(BlogArticle).filter_by(id=blog_id)
    if not flask_login.current_user.is_active():
        query = query.filter_by(is_active=1)
    blog = query.first()
    session.close()
    return render_template('blog/blog_view.html', blog=blog)


@bp_blog.route('/files/', methods=['POST'])
@flask_login.login_required
def save_file():
    """
    存储上传的图片
    """
    files_name = request.files.keys()
    ret = []
    for fn in files_name:
        # 暂未做安全校验 PIL
        img_file = request.files.get(fn)
        bucket.put_object(fn, img_file)
        link = bucket.generate_url(fn)
        ret.append({'name': fn, 'link': link})
    http_files_link = request.form.keys()
    for fn in http_files_link:
        http_link = request.form.get(fn)
        img_file = urllib.urlopen(http_link)
        bucket.put_object(fn, img_file)
        link = bucket.generate_url(fn)
        ret.append({'name': fn, 'link': link})
    return jsonify(ok=True, data=ret)


