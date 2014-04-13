#!/usr/bin/python
# coding=utf8


from flask import Flask, render_template, g
import flask_login

from configs import settings
from utils.filters import JINJA2_FILTERS
from utils import user_cache
from views import blog, base, security


def create_app(debug=settings.DEBUG):
    app = Flask(__name__)
    app.register_blueprint(blog.bp_blog)
    app.register_blueprint(base.bp_base)
    app.register_blueprint(security.bp_security)
    app.jinja_env.filters.update(JINJA2_FILTERS)
    app.debug = debug
    app.secret_key = "gausszh"

    @app.route('/')
    def index():
        return render_template('index.html')

    @app.before_request
    def check_user():
        g.user = flask_login.current_user

    login_manager = flask_login.LoginManager()
    login_manager.setup_app(app)

    @login_manager.user_loader
    def load_user(userid):
        user = user_cache.get_user(userid, format='object')
        return user

    login_manager.unauthorized = blog.list
    # login_manager.anonymous_user = AnonymousUserMixin

    return app

app = create_app(settings.DEBUG)


if __name__ == '__main__':
    host = settings.APP_HOST
    port = settings.APP_PORT
    app.run(host=host, port=port)
