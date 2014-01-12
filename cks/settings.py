"""
Django settings for cks project.

For more information on this file, see
https://docs.djangoproject.com/en/1.6/topics/settings/

For the full list of settings and their values, see
https://docs.djangoproject.com/en/1.6/ref/settings/
"""

# Build paths inside the project like this: os.path.join(BASE_DIR, ...)
import os
import private_settings
BASE_DIR = os.path.dirname(os.path.dirname(__file__))
import local_settings

# Quick-start development settings - unsuitable for production
# See https://docs.djangoproject.com/en/1.6/howto/deployment/checklist/

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = private_settings.SECRET_KEY

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = local_settings.DEBUG

TEMPLATE_DEBUG = local_settings.TEMPLATE_DEBUG


# Application definition

INSTALLED_APPS = (
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'south',
    'widget_tweaks',
    'dbbackup',
    'social.apps.django_app.default',
    'debug_toolbar',
    'storages',
    'app',
)

CACHES = {
    'default': {
        'BACKEND': 'django.core.cache.backends.memcached.MemcachedCache',
        'LOCATION': '127.0.0.1:11211',
    }
}

MIDDLEWARE_CLASSES = (
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
    'social.apps.django_app.middleware.SocialAuthExceptionMiddleware',
)

if DEBUG:
    MIDDLEWARE_CLASSES += ('app.middleware.ProfilerMiddleware',)

ROOT_URLCONF = 'cks.urls'

WSGI_APPLICATION = 'cks.wsgi.application'


# Database
# https://docs.djangoproject.com/en/1.6/ref/settings/#databases

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

# Internationalization
# https://docs.djangoproject.com/en/1.6/topics/i18n/

LANGUAGE_CODE = 'en-us'

USE_I18N = True

USE_L10N = True

USE_TZ = True

TIME_ZONE = 'America/New_York'


# in form (month, date)
FALL_SEMESTER_START = (9, 1)
FALL_SEMESTER_END = (12, 31)

SPRING_SEMESTER_START = (1, 1)
SPRING_SEMESTER_END = (6, 1)

SEMESTER_START = {}
SEMESTER_END = {}

SEMESTER_START['fall'] = FALL_SEMESTER_START
SEMESTER_END['fall'] = FALL_SEMESTER_END
SEMESTER_START['spring'] = SPRING_SEMESTER_START
SEMESTER_END['spring'] = SPRING_SEMESTER_END

# options are 'less' or 'css'
STYLE_PROTOCOL = 'css'

import os.path

TEMPLATE_DIRS = (
    # Put strings here, like "/home/html/django_templates" or "C:/www/django/templates".
    # Always use forward slashes, even on Windows.
    # Don't forget to use absolute paths, not relative paths.
    os.path.join(os.path.dirname(__file__), 'templates').replace('\\','/'),
)


from django.conf.global_settings import TEMPLATE_CONTEXT_PROCESSORS as TCP

TEMPLATE_CONTEXT_PROCESSORS = TCP + (
    'django.core.context_processors.request',
    'app.context_processors.style_protocol',
    'django.contrib.messages.context_processors.messages',
    'social.apps.django_app.context_processors.backends',
    'social.apps.django_app.context_processors.login_redirect',
)


SESSION_SERIALIZER = 'django.contrib.sessions.serializers.JSONSerializer'


# URL of the login page.
LOGIN_URL = '/login/'
LOGIN_REDIRECT_URL = '/'

AUTHENTICATION_BACKENDS = (
  'social.backends.open_id.OpenIdAuth',
  'social.backends.google.GoogleOpenId',
  'social.backends.username.UsernameAuth',
  'django.contrib.auth.backends.ModelBackend',
)


LOGIN_URL = '/login/'
LOGIN_REDIRECT_URL = '/'
URL_PATH = ''
SOCIAL_AUTH_STRATEGY = 'social.strategies.django_strategy.DjangoStrategy'
SOCIAL_AUTH_STORAGE = 'social.apps.django_app.default.models.DjangoStorage'


SOCIAL_AUTH_PIPELINE = (
    'social.pipeline.social_auth.social_details',
    'social.pipeline.social_auth.social_uid',
    'social.pipeline.social_auth.auth_allowed',
    'social.pipeline.social_auth.social_user',
    'social.pipeline.user.get_username',
    'social.pipeline.social_auth.associate_user',
    'social.pipeline.social_auth.load_extra_data',
    'social.pipeline.user.user_details'
)

EMAIL_USE_TLS = True
FROM_EMAIL = private_settings.EMAIL_ADDRESS
EMAIL_HOST = 'smtp.gmail.com'
EMAIL_HOST_USER = private_settings.EMAIL_ADDRESS
EMAIL_HOST_PASSWORD = private_settings.EMAIL_PASSWORD
EMAIL_PORT = 587
EMAIL_BACKEND = 'django.core.mail.backends.smtp.EmailBackend'


STATICFILES_STORAGE = local_settings.STATICFILES_STORAGE
DEFAULT_FILE_STORAGE = local_settings.DEFAULT_FILE_STORAGE
STATIC_URL = local_settings.STATIC_URL
AWS_ACCESS_KEY_ID = private_settings.AWS_ACCESS_KEY_ID
AWS_SECRET_ACCESS_KEY = private_settings.AWS_SECRET_ACCESS_KEY
AWS_STORAGE_BUCKET_NAME = 'cks'


DBBACKUP_STORAGE = 'dbbackup.storage.s3_storage'
DBBACKUP_S3_BUCKET = 'cks_db_backups'
DBBACKUP_S3_ACCESS_KEY = AWS_ACCESS_KEY_ID
DBBACKUP_S3_SECRET_KEY = AWS_SECRET_ACCESS_KEY

ALLOWED_HOSTS = [
'.184.72.228.154',
'.ip-10-72-107-248.ec2.internal',
'django-dbbackup'
]
#else:
    # Static files (CSS, JavaScript, Images)
    # https://docs.djangoproject.com/en/1.6/howto/static-files/

   # STATIC_URL = '/static/'

ADMINS = (
    ('Andrew Raftery', 'andrewraftery@gmail.com'),
    )