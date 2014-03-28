#!/usr/bin/python
#coding=utf8


from flask import Flask
from configs import settings
from views.blog import bp_blog

def create_app(debug=settings.DEBUG):
	app = Flask(__name__, )
	app.debug= debug
	app.register_blueprint(bp_blog)
	return app

app = create_app(settings.DEBUG)

# static file



if __name__ == '__main__':
	host = settings.APP_HOST
	port = settings.APP_PORT
	app.run(host=host, port=port)