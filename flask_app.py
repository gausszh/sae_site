#!/usr/bin/python
# coding=utf8


from flask import Flask
from configs import settings
from utils.filters import JINJA2_FILTERS
from views.blog import bp_blog

def create_app(debug=settings.DEBUG):
    app = Flask(__name__)
    app.register_blueprint(bp_blog)
    app.jinja_env.filters.update(JINJA2_FILTERS)
    app.debug = debug
    return app

app = create_app(settings.DEBUG)


if __name__ == '__main__':
    host = settings.APP_HOST
    port = settings.APP_PORT
    app.run(host=host, port=port)
