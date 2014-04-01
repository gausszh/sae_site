#coding=utf8
import os

# system setting
DEBUG = True
APP_HOST = '127.0.0.1'
APP_PORT = 7020
STORAGE_BUCKET_DOMAIN_NAME = 'blogimg'

# database

if os.environ.get('SERVER_SOFTWARE'):#线上
	import sae
	DB_SAE_URI = 'mysql://%s:%s@%s:%s/database_name' % (sae.const.MYSQL_USER, 
        	sae.const.MYSQL_PASS, sae.const.MYSQL_HOST, sae.const.MYSQL_PORT)
	DB_POOL_RECYCLE_TIMEOUT = 10
	DB_ECHO = True
else:
	DB_SAE_URI = 'mysql://user:pass@127.0.0.1:3306/database_name'
	# DB_SAE_URI = 'sqlite:////database.db'
	DB_POOL_RECYCLE_TIMEOUT = 10
	DB_ECHO = True

# cache
CACHE_TIMEOUT = 3

# app
API_KEY = '***'
API_SECRET = '****'
REDIRECT_URI = 'http://****'
