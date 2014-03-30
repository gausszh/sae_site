#coding=utf8

import datetime
import urllib
import markdown
from flask import Blueprint, request, jsonify, render_template, make_response
import flask_login 
from sae.storage import Bucket

from models.blog import create_session, BlogArticle
from configs import settings


bp_blog = Blueprint('blog', __name__, url_prefix='/blog')
bucket = Bucket(settings.STORAGE_BUCKET_DOMAIN_NAME)
bucket.put()

@bp_blog.route('/')
@bp_blog.route('/list/')
def list():
	session = create_session()
	blogs = session.query(BlogArticle).filter_by(is_active=1).all()
	return render_template('blog/blog_list.html', blogs=blogs, user=flask_login.current_user)


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
		html = form.get('html')
		title = form.get('title')
		blog_id = form.get('blog_id')
		if markdown and html and title and \
			(len(markdown.strip()) * len(markdown.strip()) * len(markdown.strip()) > 0):

			session = create_session()
			now = datetime.datetime.now()
			# blog_id belong to this user
			if blog_id:
				blog = session.query(BlogArticle).filter_by(id=blog_id).first()
			if not blog_id or not blog:
				blog = BlogArticle()
				blog.create_by = 'gausszh'
				blog.create_time = now

			blog.update_time = now
			blog.title = title
			blog.markdown = markdown
			blog.html = html
			session.add(blog)
			session.commit()
			blog_id = blog.id
			session.close()
			return jsonify(ok=True, data={'blog_id': blog_id})
		return jsonify(ok=False, reason=u'数据错误')


@bp_blog.route('/view/<int:blog_id>/')
def view_blog(blog_id):
	session = create_session()
	blog = session.query(BlogArticle).filter_by(id=blog_id).first()
	session.close()
	return render_template('blog/blog_view.html', blog=blog)

@bp_blog.route('/files/', methods=['POST'])
def save_file():
	"""
	存储上传的图片
	"""
	files_name = request.files.keys()
	ret = []
	for fn in files_name:
		#暂未做安全校验 PIL
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

		
		


@bp_blog.route('/test/')
def test():
	return render_template('%s.html' % request.args.get('p'))

