#!/usr/bin/python
# coding=utf8


from flask import Flask
from flask_login import LoginManager

from configs import settings
from utils.filters import JINJA2_FILTERS
from utils import user_cache, AnonymousUserMixin
from models.base import User
from views.blog import bp_blog

def create_app(debug=settings.DEBUG):
    app = Flask(__name__)
    app.register_blueprint(bp_blog)
    app.jinja_env.filters.update(JINJA2_FILTERS)
    app.debug = debug
    app.secret_key = "gausszh"

    login_manager = LoginManager()
    login_manager.setup_app(app)

    @login_manager.user_loader
    def load_user(userid):
        d = user_cache.get_user(str(userid))
        user = User() 
        for k in d:
            setattr(user, k, d.get(k))
        return user


    login_manager.anonymous_user = AnonymousUserMixin

    return app

app = create_app(settings.DEBUG)




if __name__ == '__main__':
    host = settings.APP_HOST
    port = settings.APP_PORT
    app.run(host=host, port=port)
