from cks.settings_common import *
import os, os.path

############################################################
##### STATIC FILES #########################################
############################################################

STATIC_URL = '/static/'
DEFAULT_FILE_STORAGE = 'storages.backends.s3boto.S3BotoStorage'
AWS_S3_SECURE_URLS = False       # use http instead of https
AWS_QUERYSTRING_AUTH = False     # don't add complex authentication-related query parameters for requests
AWS_ACCESS_KEY_ID = os.environ.get('AWS_ACCESS_KEY')
AWS_SECRET_ACCESS_KEY = os.environ.get('AWS_SECRET_ACCESS_KEY')
AWS_STORAGE_BUCKET_NAME = 'cks'

############################################################
##### DATABASE #############################################
############################################################

DATABASES = {
    'default': {
        'ENGINE':'django.db.backends.postgresql_psycopg2',
        'NAME': 'cks',
        'USER': 'jharvard',
        'PASSWORD': 'crimson',
        'HOST': '127.0.0.1',
        'PORT': '5432',
    }
}

############################################################
##### OTHER ################################################
############################################################

DEBUG = True
TEMPLATE_DEBUG = True
USE_CLING = False