from cks.settings_common import *
import os, os.path

############################################################
##### STATIC FILES #########################################
############################################################

STATICFILES_STORAGE = 'storages.backends.s3boto.S3BotoStorage'
DEFAULT_FILE_STORAGE = 'storages.backends.s3boto.S3BotoStorage'
AWS_ACCESS_KEY_ID = os.environ.get('AWS_ACCESS_KEY')
AWS_SECRET_ACCESS_KEY = os.environ.get('AWS_SECRET_ACCESS_KEY')
AWS_STORAGE_BUCKET_NAME = 'cks'
STATIC_URL = 'http://{}.s3.amazonaws.com/'.format(AWS_STORAGE_BUCKET_NAME)
MIDDLEWARE_CLASSES += ["bugsnag.django.middleware.BugsnagMiddleware"]

############################################################
##### DATABASE #############################################
############################################################

# Parse database configuration from $DATABASE_URL
import dj_database_url
DATABASES['default'] =  dj_database_url.config()

# Honor the 'X-Forwarded-Proto' header for request.is_secure()
SECURE_PROXY_SSL_HEADER = ('HTTP_X_FORWARDED_PROTO', 'https')

############################################################
##### OTHER ################################################
############################################################

DEBUG = False
TEMPLATE_DEBUG = False
USE_CLING = True