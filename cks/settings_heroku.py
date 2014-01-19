from cks.settings_common import *
import os, os.path

############################################################
##### STATIC FILES #########################################
############################################################

# Static asset configuration
STATIC_ROOT = 'staticfiles'
STATIC_URL = '/static/'

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